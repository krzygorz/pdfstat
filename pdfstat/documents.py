from datetime import datetime
from functools import namedtuple
import configparser

import re
import subprocess
import os
import errno
# Horrible hack but it's kinda fast i guess???
# TODO: Consider using other method maybe with caching in the database.
pdfinfo_re = re.compile(r"Pages:\s*(\d+)")
def total_pages(path):
    if os.path.exists(path):
        o = subprocess.check_output(["pdfinfo", path]).decode()
        return int(re.search(pdfinfo_re, o).group(1))
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)

class HistKeyError(LookupError):
    def __init__(self, path):
        self.path = path

ZHistEntry = namedtuple("ZHistEntry", "page time_opened")
class ZathuraHistory:
    def __init__(self, path):
        self._raw = configparser.ConfigParser()
        with path.open() as histfile:
            self._raw.read_file(histfile)
    def get_by_path(self, path):
        try:
            entry = self._raw[path]
        except KeyError:
            raise HistKeyError(path)
        return ZHistEntry(int(entry['page']), datetime.fromtimestamp(int(entry['time'])))

####### Other versions of total_pages ########

### Slow
# import PyPDF2
# def total_pages(path):
#     p = PyPDF2.PdfFileReader(path)
#     return p.numPages

### Also slow...
# import pikepdf
# def total_pages(path):
#     with pikepdf.Pdf.open(path) as pdf:
        # return len(pdf.pages)

### Apparently this doesn't always work
# import re
# rxcountpages = re.compile(r"/Type\s*/Page([^s]|$)", re.MULTILINE|re.DOTALL)
# def total_pages(filename):
#     data = open(filename,"rb").read()
#     return len(rxcountpages.findall(data))