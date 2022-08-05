"""
Demo of the Python-based NN pipeline compute node 

# Run the worker node with:
    python worker.py

# More on command line arguments:
    python worker.py -h

"""

import argparse
import pynng
import trio

from core.defaults import Defaults
from core.help import HelpStrings
from core.tasks import task_work_service, task_work_predict
from core.ver import ver_tag

async def bootstrap():
    p = argparse.ArgumentParser(add_help=False, usage=__doc__)
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

    with pynng.Respondent0(dial=args.addr_service) as sock_responder, \
           pynng.Rep0(dial=args.addr_worker, reconnect_time_min=1000, reconnect_time_max=5000) as sock_rep:
        # TODO: Remove debug output
        print('[Connecting...]')
        await trio.sleep(0.5)
        # TODO: Remove debug output
        print('[Possibly Connected]')
        async with trio.open_nursery() as nursery:
            nursery.start_soon(task_work_predict, sock_rep)
            nursery.start_soon(task_work_service, sock_responder)

def main():
    try:
        trio.run(bootstrap, restrict_keyboard_interrupt_to_checkpoints=True)
    except KeyboardInterrupt:
        print('Exiting...')

if __name__ == '__main__':
    main()
