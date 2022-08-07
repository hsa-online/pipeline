"""
Demo of the Python-based NN pipeline compute node 

# Run the worker node with:
    python worker.py

# More on command line arguments:
    python worker.py -h

Command line arguments:

--addr_service    specifies the address and port of Gateway's service listener.
--addr_worker     specifies the address and port of Gateway's computation listener.
-h                print this help message.
"""

import argparse
import pynng
import trio

from core.app_stats import ApplicationStatistics
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

    ApplicationStatistics.setup_for_work()

    with pynng.Respondent0(dial=args.addr_service) as sock_responder, \
            pynng.Rep0(dial=args.addr_worker, 
                reconnect_time_min=Defaults.WORK_RECONNECT_TIME_MIN_MS, 
                reconnect_time_max=Defaults.WORK_RECONNECT_TIME_MAX_MS) as sock_rep:
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
