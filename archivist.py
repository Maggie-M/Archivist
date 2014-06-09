import hashlib
import os
import sys
import six.moves.urllib as urllib

from utils import depend_check

Version = "0.2"


def tester(ver):
    """Run each of the test functions to determine if the md5 and Filesize
    of a given version of the Anaconda installer are the same as the one
    listed in the archive."""
    archive_link, html_doc = get_archive()
    pkg_dict = scrape_pkgs(ver, archive_link, html_doc)
    results = {}
    path = os.getcwd()
    testpath = os.path.join(path, 'pkgs')
    packages = os.listdir(testpath)

    print("")

    for pkg in packages:
        if pkg in pkg_dict:
            print(colored("Package: %s.\n" % pkg, "green"))

            pkgpath = os.path.join(path, 'pkgs', pkg)
            md5 = reader(pkgpath, pkg_dict, pkg)
            size = sizer(pkgpath, pkg_dict, pkg)
            results.update({pkg: (md5, size)})

        else:
            print(colored("!! UNEXPECTED FILE %s !!\n" % pkg, "magenta"))

        print(colored("-", "yellow")*60 + "\n")  # make a yellow seperator

    printer(results)


def get_archive():
    """Read Continuum archive and return its URL and html
    as two separate strings."""
    BASE_URL = "http://repo.continuum.io/archive/"

    try:
        page = urllib.request.urlopen(os.path.join(BASE_URL, "index.html"))
    except IOError:
        print("Unable to connect to %s" % BASE_URL)
        sys.exit(1)

    html_doc = page.read()
    page.close()

    return BASE_URL, html_doc


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
                    writer(archive_link, pkg_name)

    if pkgs == {}:
        print("No results found in archive.  Please choose a different version.")
        sys.exit(1)
    return pkgs


def writer(location, package):
    """Download packages by writing them to a file in ~/Archivist/pkgs/"""

    download_path = os.path.join(location, package)
    print(colored("Downloading file %s" % package, "yellow"))

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
        return colored("Correct md5", "cyan")
    else:
        print("Expected md5: %s\nActual md5: %s" % (colored(expectedmd5, "green"), colored(result, "red")) + "\n")
        return colored("Incorrect md5", "red")


def sizer(path, dirDict, pkg):
    """Compare package size with the archive's expected size"""
    expectedSize = dirDict[pkg][1]
    size = os.path.getsize(path) >> 20
    print("expected size: %d, actual size: %d\n" % (expectedSize, size))
    if expectedSize == size:
        return colored("Correct size", "green")
    else:
        return colored("Incorrect size", "red")


def printer(results):
    """Output the results of each of the tests to the terminal"""
    headers = ('Name', 'md5', 'Filesize')
    print("%-35s %-25s %-30s" % headers)
    border = ["-"*35, "-"*25, "-"*30]
    print(" ".join(border))
    for result in results:
        # adds extra space to middle field to account for hidden color control characters
        print("%-35s %-34s %-30s" % (result, results[result][0], results[result][1]))


if __name__ == '__main__':
    if depend_check("bs4", "termcolor"):
        from bs4 import BeautifulSoup
        from termcolor import colored
        if len(sys.argv) == 2:
            version = sys.argv[1]
        else:
            print("Please choose a version of Anaconda to test ('python archivist.py 1.7.0')")
            sys.exit(1)
    results = tester(version)
