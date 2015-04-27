import sys


def depend_check(*args):
    """Check for missing dependencies
    """
    found = True

    for dependency in args:
        try:
            __import__(dependency)
        except ImportError as e:
            print(e)
            found = False

    if not found:
        print("Please use conda or pip to install any missing dependencies.")
        sys.exit(1)
    else:
        return True
