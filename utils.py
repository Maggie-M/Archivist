import sys

def depend_check(*deps):
    """Check for missing dependencies
    """
    found = True

    for dependency in deps:
        try:
            __import__(dependency)
        except ImportError as e:
            print(e)
            found = False

    if not found:
        print("Please use pip to install any missing dependencies.")
        sys.exit(1)
    else:
        return True