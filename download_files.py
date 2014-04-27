#!python
# vim: set fileencoding=utf-8 shiftwidth=4 tabstop=4 expandtab smartindent :

"""
Download all files from ec.europa.eu.
Files will be stored in the "input" directory.
"""

# Code blatantly stolen from: http://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python user http://stackoverflow.com/users/2357007/stan
# Licensed under CC BY-SA 2.5 according to http://stackexchange.com/legal/terms-of-service

# Responses are located at:
# 
# http://ec.europa.eu/internal_market/consultations/docs/2013/copyright/registered_en.zip
# http://ec.europa.eu/internal_market/consultations/docs/2013/copyright/users_en.zip
# http://ec.europa.eu/internal_market/consultations/docs/2013/copyright/other-stakeholders_en.zip

from __future__ import ( division, absolute_import, print_function, unicode_literals )

import sys, os, tempfile, logging, shutil

if sys.version_info >= (3,):
    import urllib.request as urllib2
    import urllib.parse as urlparse
else:
    import urllib2
    import urlparse

def download_file(url, desc=None):
    u = urllib2.urlopen(url)

    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
    filename = os.path.basename(path)
    if not filename:
        filename = 'downloaded.file'
    if desc:
        filename = os.path.join(desc, filename)

    with open(filename, 'wb') as f:
        meta = u.info()
        meta_func = meta.getheaders if hasattr(meta, 'getheaders') else meta.get_all
        meta_length = meta_func("Content-Length")
        file_size = None
        if meta_length:
            file_size = int(meta_length[0])
        print("Downloading: {0} Bytes: {1}".format(url, file_size))

        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)

            status = "{0:16}".format(file_size_dl)
            if file_size:
                status += "   [{0:6.2f}%]".format(file_size_dl * 100 / file_size)
            status += chr(13)
            print(status, end="")
        print()

    return filename

urls = ["http://ec.europa.eu/internal_market/consultations/docs/2013/copyright/registered_en.zip", "http://ec.europa.eu/internal_market/consultations/docs/2013/copyright/users_en.zip", "http://ec.europa.eu/internal_market/consultations/docs/2013/copyright/other-stakeholders_en.zip"]

if not os.path.isdir("input"):
    os.mkdir("input")
os.chdir("input")

for url in urls:
    basename = url.split("/")[-1]
    if os.path.exists(os.path.join("..", basename)):
        shutil.move(os.path.join("..", basename), ".")
    elif not os.path.exists(basename):
        filename = download_file(url)
        print(filename)
