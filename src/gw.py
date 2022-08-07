"""
Demo of the Python-based NN pipeline gateway with the REST API

# Run the gateway with:
    python gw.py

# More on command line arguments:
    python gw.py -h

Command line arguments:

--addr_service    specifies the address and port of Gateway's service listener.
--addr_worker     specifies the address and port of Gateway's computation listener.
-h                print this help message.

"""

import argparse
import pynng
import trio

from hypercorn.config import Config
from hypercorn.trio import serve
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from core.api import APIGateway
from core.app_stats import ApplicationStatistics
from core.defaults import Defaults
from core.help import HelpStrings
from core.msg_helper import MessageHelper
from core.tasks import task_gw_service, task_gw_predict
from core.ver import ver_tag

async def bootstrap():
    p = argparse.ArgumentParser(add_help=False, usage=__doc__)
    p.add_argument(
        '--addr_rest',
        default=Defaults.ADDR_REST,
        help=HelpStrings.addr_rest,
    )
    p.add_argument(
        '--addr_service',
        default=Defaults.ADDR_SERVICE,
        help=HelpStrings.addr_service,
    )
    p.add_argument(
        '--addr_worker',
        default=Defaults.ADDR_WORKER,
        help=HelpStrings.addr_worker,
    )
    p.add_argument(
        '-h', '--help', 
        action='help', 
        default=argparse.SUPPRESS,
        help=HelpStrings.help)
    args = p.parse_args()

    msg = f'Gateway (version {ver_tag}) is going to run at {args.addr_rest} ...'
    print(msg)

    conf_hypercorn = Config.from_mapping({'bind': args.addr_rest})

    chan_service_send_api2cluster, chan_service_receive_api2cluster = trio.open_memory_channel(
        max_buffer_size=Defaults.GW_SIZE_QUEUE_SERVICE)
    chan_service_send_cluster2api, chan_service_receive_cluster2api = trio.open_memory_channel(
        max_buffer_size=Defaults.GW_SIZE_QUEUE_SERVICE)

    chan_compute_send_api2cluster, chan_compute_receive_api2cluster = trio.open_memory_channel(
        max_buffer_size=Defaults.GW_SIZE_QUEUE_COMPUTE)
    chan_compute_send_cluster2api, chan_compute_receive_cluster2api = trio.open_memory_channel(
        max_buffer_size=Defaults.GW_SIZE_QUEUE_COMPUTE)

    ApplicationStatistics.setup_for_gw()

    with pynng.Surveyor0(listen=args.addr_service) as sock_surveyor, \
        pynng.Req0(listen=args.addr_worker) as sock_req:
 
        """
        def pre_connect_cb(pipe):
            addr = str(pipe.remote_address)
            print('~~~~got connection from {}'.format(addr))
        def post_remove_cb(pipe):
            addr = str(pipe.remote_address)
            print('~~~~goodbye for now from {}'.format(addr))
        sock_req.add_pre_pipe_connect_cb(pre_connect_cb)
        sock_req.add_post_pipe_remove_cb(post_remove_cb)
        sock_req.listen(args.addr_worker)

        await trio.sleep(0.5)
        """

        async with chan_service_send_api2cluster, chan_service_receive_api2cluster, \
                chan_service_send_cluster2api, chan_service_receive_cluster2api, \
                chan_compute_send_api2cluster, chan_compute_receive_api2cluster, \
                chan_compute_send_cluster2api, chan_compute_receive_cluster2api:
            async with trio.open_nursery() as nursery:
                nursery.start_soon(task_gw_predict, 
                    chan_compute_send_cluster2api, chan_compute_receive_api2cluster, sock_req)

                nursery.start_soon(task_gw_service, 
                    chan_service_send_cluster2api, chan_service_receive_api2cluster, 
                    chan_compute_send_api2cluster, sock_surveyor)

                nursery.start_soon(serve, APIGateway(
                    chan_service_send_api2cluster, chan_service_receive_cluster2api,
                    chan_compute_send_api2cluster, chan_compute_receive_cluster2api), conf_hypercorn)

def main():
    try:
        trio.run(bootstrap, restrict_keyboard_interrupt_to_checkpoints=True)
    except KeyboardInterrupt:
        print('Exiting...')

if __name__ == '__main__':
    main()
