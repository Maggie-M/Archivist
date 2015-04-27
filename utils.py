from __future__ import print_function

import sys

try:
    import colorama
    def blue(text): return "%s%s%s" % (colorama.Fore.BLUE, text, colorama.Style.RESET_ALL)
    def red(text): return "%s%s%s" % (colorama.Fore.RED, text, colorama.Style.RESET_ALL)
except ImportError:
    def blue(text) : return text
    def red(text) : return text

pkg_info_dict = {'bs4' : 'beautiful-soup'}

def depend_check(deps_name, *args):
    """Check for missing dependencies
    """

    found = True
    missing = []

    for dependency in args:
        try:
            __import__(dependency)
        except ImportError as e:
            missing.append(dependency)
            found = False

    print('-'*80)
    if not found:
        print(red("You are missing the following %s dependencies:") % deps_name)

        for dep in missing:
            name = pkg_info_dict.get(dep, dep)
            print(" * ", name)
        print()
        return False
    else:
        print(blue("All %s dependencies installed!  You are good to go!\n") % deps_name)
        return True
