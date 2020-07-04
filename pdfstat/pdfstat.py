#!/usr/bin/env python3
import os
import sys
import argparse
from datetime import datetime

from xdg import XDG_DATA_HOME

from pdfstat.database import SqlDB, LogEntry
from pdfstat.documents import ZathuraHistory, HistKeyError, HistFileNotFoundError, total_pages
from pdfstat.rate import pages_per_day

def trunc(string, n, ell='.. '):
    maxlen = n-len(ell)
    return string[:maxlen] + ell if len(string) > maxlen else string

def format_rate(rate):
    if rate > .5:
        return f"{rate:.2f} pages/day"
    else:
        return f"{1/rate:.2f} days/page"

def printStats(path, log, total):
    current_page = log[-1].page
    percent = current_page/total * 100
    short_name = trunc(os.path.basename(path), 40)
    basic_descr = "{}: {}/{} ({:.0f}%)".format(short_name, current_page, total, percent)

    if not (rate := pages_per_day(reversed(log))):
        print(basic_descr)
    else:
        pages_left = total - current_page
        time_left = pages_left/rate

        rate_str = format_rate(rate)
        print(basic_descr+" - {}, {:.0f} days left".format(rate_str, time_left))

#TODO: use pathlib
default_zhist_path = str(XDG_DATA_HOME/"zathura/history")
default_db_path = str(XDG_DATA_HOME/"pdfstat.db")

class PdfStat:
    def __init__(self, db_path=default_db_path, zhist_path=default_zhist_path):
        self.db = SqlDB(db_path)
        self.zhist = ZathuraHistory(zhist_path)
    def make_entry(self, path):
        hist_entry = self.zhist.get_by_path(path)
        return LogEntry(hist_entry.page, datetime.now())
    def track(self, path):
        if self.db.is_tracked(path):
            return False
        self.db.insert(path, self.make_entry(path))
        return True
    def forget(self, path):
        if not self.db.is_tracked(path):
            return False
        self.db.delete(path)
        return True
    def should_overwrite(self, path):
        entry_day = self.db.last_entry(path).time.day
        return entry_day == datetime.now().day
    def update(self, path):
        entry = self.make_entry(path)
        if self.should_overwrite(path):
            self.db.update(path, entry)
        else:
            self.db.insert(path, entry)

def error(msg, code):
    print(msg, file=sys.stderr)
    sys.exit(code)

def cmd_show(app):
    for path in app.db.tracked():
        try:
            total = total_pages(path)
        except FileNotFoundError:
            print("WARNING: File missing:", path, file=sys.stderr)
        else:
            log = app.db.doc_data(path)
            printStats(path, log, total)
def cmd_update(app):
    for path in app.db.tracked():
        if os.path.exists(path):
            try:
                app.update(path)
            except HistKeyError:
                print("WARNING: \"{}\" not found in zathura history!")
        else:
            print("WARNING: File missing:", path, file=sys.stderr)
def cmd_track(app, path):
    if not app.track(path):
        sys.exit("File is already tracked!")
def cmd_forget(app, path):
    if not app.forget(path):
        sys.exit("File is not tracked!")

# Uses abspath instead of realpath because that's how Zathura appears to normalize file names (ie no symlink resolution)
def normalized_path(path):
    return os.path.abspath(path)

def main():
    parser = argparse.ArgumentParser(description="Track progress of reading pdf documents.")
    parser.add_argument("--db", type=normalized_path, help="Set path to the database. Defaults to "+default_db_path)
    parser.add_argument("--zhist", type=normalized_path, help="Set path to zathura history file. Defaults to "+default_zhist_path)

    subparsers = parser.add_subparsers(dest='command', required=True)
    parser_update = subparsers.add_parser('update', help="Save current page and time for all tracked documents.") #pylint:disable=unused-variable
    parser_show = subparsers.add_parser('show', help="Display the statistics for tracked documents.")  #pylint:disable=unused-variable

    parser_track = subparsers.add_parser('track', help="Add a new file to the list of tracked documents.")
    parser_track.add_argument('path', type=normalized_path)

    parser_forget = subparsers.add_parser('forget', help="Remove the document's data from database.")
    parser_forget.add_argument('path', type=normalized_path)

    args = parser.parse_args()
    zathura_hist_path = args.zhist or os.path.expanduser(default_zhist_path)
    db_path = args.db or os.path.expanduser(default_db_path)
    try:
        app = PdfStat(db_path, zathura_hist_path)
    except HistFileNotFoundError as e:
        error("Zathura history file not found: {}".format(e.path), 2)

    try:
        if args.command == 'update':
            cmd_update(app)
        elif args.command == 'show':
            cmd_show(app)
        elif args.command == 'track':
            cmd_track(app, args.path)
        elif args.command == 'forget':
            cmd_forget(app, args.path)
    except HistKeyError as e:
        error("Error: \"{}\" not found in zathura history!".format(e.path), 2)

    app.db.save()