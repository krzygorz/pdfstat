from database import LogEntry
from datetime import datetime
from functools import namedtuple
import configparser
import pikepdf

def total_pages(path):
    #TODO: This is very slow. Use different library or call pdfinfo or just cache it in database.
    with pikepdf.Pdf.open(path) as pdf:
        return len(pdf.pages)

ZHistEntry = namedtuple("ZHistEntry", "page time_opened")
class ZathuraHistory:
    def __init__(self, path):
        self._raw = configparser.ConfigParser()
        with path.open() as histfile:
            self._raw.read_file(histfile)
    def get(self, path):
        entry = self._raw[path]
        return ZHistEntry(int(entry['page']), datetime.fromtimestamp(int(entry['time'])))
