from archivist_cli import get_parser
from utils import depend_check

import hashlib
import os
import sys
import six.moves.urllib as urllib

try:
    import colorama
    def blue(text): return "%s%s%s" % (colorama.Fore.BLUE, text, colorama.Style.RESET_ALL)
    def red(text): return "%s%s%s" % (colorama.Fore.RED, text, colorama.Style.RESET_ALL)
    def green(text): return "%s%s%s" % (colorama.Fore.GREEN, text, colorama.Style.RESET_ALL)
    def yellow(text): return "%s%s%s" % (colorama.Fore.YELLOW, text, colorama.Style.RESET_ALL)
except ImportError:
    def blue(text) : return text
    def red(text) : return text
    def green(text) : return text
    def yellow(text) : return text


def tester(ver):
    """Run each of the test functions to determine if the md5 and Filesize
       of a given version of the Anaconda installer are the same as the one
       listed in the archive.
    """

    archive_link = "http://repo.continuum.io/archive/"

    html_doc = get_html(archive_link)
    pkg_dict = scrape_pkgs(ver, archive_link, html_doc)

    if not args.nodl:
        for download in pkg_dict.iterkeys():
            writer(archive_link, download)

    results = {}
    path = os.getcwd()
    testpath = os.path.join(path, 'pkgs')
    packages = os.listdir(testpath)

    # In case you have called the --no-download option but have nothing in /pkgs
    if len(packages) == 0:
        print("Nothing in pkgs directory to test.")
        sys.exit(1)

    print("")

    for pkg in packages:
        if pkg in pkg_dict:
            print(green("Package: %s\n" % pkg))

            pkgpath = os.path.join(path, 'pkgs', pkg)
            md5 = reader(pkgpath, pkg_dict, pkg)
            size = sizer(pkgpath, pkg_dict, pkg)
            if not args.log:
                md5 = colorizer(md5)
                size = colorizer(md5)

            results.update({pkg: (md5, size)})

        else:
            print(blue("!! UNEXPECTED FILE %s !!\n" % pkg))

        print(yellow("-")*60 + "\n")  # make a yellow seperator

    return results


def get_html(some_url):
    """Return a webpage's html
       as a string.
    """

    try:
        page = urllib.request.urlopen(os.path.join(some_url, "index.html"))
    except IOError:
        print("Unable to connect to %s" % some_url)
        sys.exit(1)

    html_doc = page.read()
    page.close()

    return html_doc


def scrape_pkgs(version, archive_link, html_doc):
    """Find all Anaconda packages of a specified version within an html document
    and populate a dict for md5 and size checking."""

    soup = BeautifulSoup(html_doc)

    pkgs = {}
    for tr in soup.find_all('tr'):
        # The first <tr>'s children are <th> tags and we want <td>'s, so we're skipping them like this.
        pkg_name = ''
        for i, td in enumerate(tr.find_all('td')):
            if i == 0:
                link = td.a
                pkg_name = str(link.get('href').strip('./'))
                ver = pkg_name.split('-')[1]
            elif i == 1:
                size = int(td.text.split('.')[0])
            elif i == 3:
                md5 = td.text
        if pkg_name:
                if ver == version:
                    pkgs[pkg_name] = md5, size

    if pkgs == {}:
        print("No results found in archive.  Please choose a different version.")
        sys.exit(1)
    return pkgs


def writer(location, package):
    """Download packages by writing them to a file in ~/Archivist/pkgs/"""

    download_path = os.path.join(location, package)
    print(yellow("\nDownloading file %s" % package))

    if not os.path.exists("pkgs"):
        os.system("mkdir pkgs")

    os.system("curl %s > pkgs/%s" % (download_path, package))


def reader(path, dirDict, pkg):
    """Compare package md5 with the archive's expected md5"""
    expectedmd5 = dirDict[pkg][0]
    # open file as binary to avoid UnicodeDecodeError in Python 3
    # (tries to read binary file as though it's encoded in utf-8, otherwise)
    with open(path, "rb") as f:
        m = hashlib.md5()
        while True:
            text = f.read(2 ** 20)
            # read file in binary mode, must compare to binary empty string
            # since '' != b'' in python 3
            if text == b'':
                result = m.hexdigest()
                break
            else:
                m.update(text)

    print("expected md5: %s, actual md5: %s" % (expectedmd5, result))

    if expectedmd5 == result:
        return "Correct md5"
    else:
        print("Expected md5: %s\nActual md5: %s" % (green(expectedmd5), red(result)) + "\n")
        return "Incorrect md5"


def sizer(path, dirDict, pkg):
    """Compare package size with the archive's expected size"""

    expectedSize = dirDict[pkg][1]
    size = os.path.getsize(path) >> 20
    print("expected size: %d, actual size: %d\n" % (expectedSize, size))
    if expectedSize == size:
        return "Correct size"
    else:
        return "Incorrect size"


def colorizer(string):
    """Apply proper color formatting to strings
    """

    if string.split(" ")[0] == "Correct":
        string = green(string)
    else:
        string = red(string)

    return string


def formatter(results):
    """Takes a results dictionary and returns a formatted list
    that includes a header, border, and proper spacing
    """

    formatted_results = []

    headers = ('Name', 'md5', 'Filesize')
    formatted_results.append("%-35s %-25s %-30s" % headers)
    border = ["-"*35, "-"*25, "-"*30]
    formatted_results.append(" ".join(border))
    for result in results:
        # adds extra space to middle field to account for hidden color control characters
        formatted_results.append("%-35s %-34s %-30s" % (result, results[result][0], results[result][1]))
    return formatted_results


def printer(results_list, log=False):
    """Output the results of each of the tests to the terminal or log them
       if the 'log' optional argument is set to True
    """

    if log:
        f = open('archivist_log.txt', 'w')
        action = f.write
    else:
        action = print_function

    for line in results_list:
        action(line)

    if log:
        f.close()


def print_function(string):
    """A generic function to print a string.  Necessary for line 200, where it would be impossible
       to bind 'print' to a variable in python2 otherwise.
    """

    print(string)

if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    print("Checking for dependencies...")
    if depend_check('archivist', 'bs4'):
        from bs4 import BeautifulSoup
    else:
        sys.exit(1)

    if args.version:
        version = args.version
    else:
        print("Please choose a version of Anaconda to test ('python archivist.py -v 1.7.0')")
        sys.exit(1)

    results = tester(version)

    printer(formatter(results), args.log)
