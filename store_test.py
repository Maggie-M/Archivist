import hashlib
import os
import re
import sys
import urllib

from bs4 import BeautifulSoup
from termcolor import colored


""" TODO

Add command line automation for license checking:

ipython -c "import iopro, numbapro, llvmpy"
 for license in licenses:
     mv licenses/<license> ~/.continuum/.
     ipython -c "import iopro, numbapro, llvmpy"
     check output message
     mv ~/.continuum/* licenses/.

 Will also need to create a 'store' directory with 'full' and 'licenses' dirs, then remove
 them when done"""

def scrape_pkgs(version):
    """Find and download all Anaconda packages of a specified version
    and populate a dict for md5 and size checking."""

    BASE_URL = "http://repo.continuum.io/archive/"
    page = urllib.urlopen(os.path.join(BASE_URL, "index.html"))
    html_doc = page.read()
    page.close()

    soup = BeautifulSoup(html_doc)

    pkgs = {}
    for tr in soup.find_all('tr'):
        pkg_name = '' # The first <tr>'s children are <th> tags and we want <td>'s, so we're skipping them like this.
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
                    download_path =  os.path.join(BASE_URL, pkg_name)
                    print "Downloading file %s" % pkg_name
                    url = urllib.urlopen(download_path) # replace with curl
                    tmpfile = open('full/%s' % pkg_name, 'w')

                    # initialize and start progress bar here

                    # these two lines get replaced with a loop that reads chunks and updates
                    # a progress bar
                    data = url.read()
                    tmpfile.write(data)

                    # finish progress bar here

                    tmpfile.close
                    
    if pkgs == {}:
        print "No results found in archive.  Please choose a different version."
        sys.exit()
    return pkgs

def printer(results):
    headers = ('Name','md5','Filesize')
    print "%-35s %-25s %-30s" % headers
    print "-"*35, "-"*25, "-"*30
    for result in results:
        # add extra space to middle field to account for hidden color control characters
        print "%-35s %-34s %-30s" % (result, results[result][0], results[result][1])

def reader(path, dirDict, pkg):
    """Compare package md5 with the archive's expected md5"""
    expectedmd5 = dirDict[pkg][0]
    items = os.listdir(os.getcwd())
    f = open(path, "r+")
    m = hashlib.md5()
    while True:
        next = f.read(2 ** 20)
        if next == "":
            result = m.hexdigest()
            f.close()
            break
        else:
            m.update(next)
    print "expcted md5: %s, actual md5: %s" % (expectedmd5, result)

    if expectedmd5 == result:
        return colored("Correct md5", "cyan")
    else:
        print  "Expected md5: %s\nActual md5:   %s" % (colored(expectedmd5, "green"), colored(result, "red")) + "\n"
        return colored("Incorrect md5", "red")

def sizer(path, dirDict, pkg):
    """Compare package size with the archive's expected size"""
    expectedSize = dirDict[pkg][1]
    size = os.path.getsize(path) >> 20
    print "expected size: %d, actual size: %d\n" % (expectedSize, size)
    if expectedSize == size:
        return colored("Correct size", "green")
    else:
        return colored("Incorrect size", "red")

def tester(ver):
    pkg_dict = scrape_pkgs(ver)
    results = {}
    path = os.getcwd()
    testpath = os.path.join(path, 'full')
    packages = os.listdir(testpath)

    print ""

    for pkg in packages:
        if pkg in pkg_dict:
            print colored("Directory: %s, package: %s.\n" % ('full', pkg), "green")

            pkgpath = os.path.join(path, 'full', pkg)
            md5 = reader(pkgpath, pkg_dict, pkg)
            size = sizer(pkgpath, pkg_dict, pkg)
            results.update({pkg:(md5,size)})

        else:
            print colored("!! UNEXPECTED FILE %s !!\n" % pkg, "magenta")

        print colored("-", "yellow")*60 + "\n"  # make a yellow seperator 

    printer(results)

def licenseCheck():
    testpath = os.path.join(os.getcwd(), 'licenses')
    print testpath
    licenses = os.listdir(testpath)
    cmd = os.system
    destination = os.path.expanduser('~/.continuum/')

    for license in licenses:
        print license
        cmd('mv %s ~/.continuum/.' % license)
        cmd('ipython -c "import iopro, numbapro, llvmpy"')
        cmd('mv ~/.continuum/* %s/.' % testpath)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        version = sys.argv[1]
    else:
        print "Please choose a version of Anaconda to test ('python storetest.py 1.7.0')"
        sys.exit(1)
    results = tester(version)
# license_check = licenseCheck()        