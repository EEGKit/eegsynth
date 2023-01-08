import sys
import time

from .redis import _setup, _start, _loop_once, _loop_forever, _stop

class Executable:
    def __init__(self, args=None):
        if args!=None:
            # override the command line arguments
            sys.argv = [sys.argv[0]] + args

        # the setup MUST pass without errors
        _setup()

        while True:
            # keep running until KeyboardInterrupt
            try:
                _start()
                _loop_forever()
            except RuntimeError:
                # do not restart
                raise SystemExit
            except KeyboardInterrupt:
                raise SystemExit