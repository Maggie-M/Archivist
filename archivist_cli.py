import argparse
import textwrap


def get_parser():
    """Create the parser that will be used to add arguments to the script.
    """

    parser = argparse.ArgumentParser(description=textwrap.dedent("""
                    Downloads and tests the md5 and file size of a given version of Anaconda located in
                    http://repo.continuum.io/archive/

                    The version option (-v) allows you to select a specific version of Anaconda to download and test.
                    This will include every system's Anaconda distribution for that version (OSX, Windows, Linux)

                    The --log option will write the results of these tests to a log file.  If not enabled, results
                    will be written to stdout.

                    If you already have Anaconda installers inside the pkgs directory and wish to test those without
                    downloading new ones, use the --no-download option.  NOTE: You will still need to provide the
                    version (-v) of the installers.
                    """), formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--log', action='store_true', dest='log', default=False,
                        help="save a log of any errors discovered")
    parser.add_argument('-v', '--version', action='store', default=False,
                        help="version of Anaconda to download and test")
    parser.add_argument('--no-download', action='store_true', dest='nodl', default=False,
                        help="test local anaconda packages in pkgs, rather than download new ones")

    return parser
