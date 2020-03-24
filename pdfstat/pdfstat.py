#!/usr/bin/env python3
from pathlib import Path
import os
import sys
from datetime import datetime
from pdfstat.database import SqlDB, LogEntry
from pdfstat.documents import ZathuraHistory, HistKeyError, total_pages
import argparse

def trunc(string, n, ell='.. '):
    maxlen = n-len(ell)
    return string[:maxlen] + ell if len(string) > maxlen else string

def format_rate(pages, days):
    if pages > days:
        return f"{pages/days:g} pages/day"
    else:
        return f"{days/pages:g} days/page"

def printStats(path, log, total):
    first = log[0]
    last = log[-1]

    delta_t = datetime.now() - first.time #TODO: abstract out rate calculations
    delta_p = last.page - first.page
    percent = last.page/total * 100

    if delta_p == 0:
        print("{}: {}/{} ({:.0f}%)".format(trunc(os.path.basename(path), 40), last.page, total, percent))
    else:
        pages_left = total - last.page
        time_left = delta_t.days/delta_p * pages_left

        rate_str = format_rate(delta_p, delta_t.days)
        print("{}: {}/{} ({:.0f}%) - {}, {} days left".format(trunc(os.path.basename(path), 40), last.page, total, percent, rate_str, time_left))

class PdfStat:
    def __init__(self, db_path, zhist_path):
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

zathura_hist_path = Path("~/.local/share/zathura/history").expanduser()
db_path = Path("data.db")

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

def main():
    parser = argparse.ArgumentParser(description="Track progress of reading pdf documents.")
    subparsers = parser.add_subparsers(dest='command', required=True)
    parser_update = subparsers.add_parser('update', help="Save current page and time for all tracked documents.")
    parser_show = subparsers.add_parser('show', help="Display the statistics for tracked documents.")

    parser_track = subparsers.add_parser('track', help="Add a new file to the list of tracked documents.")
    parser_track.add_argument('path', type=os.path.abspath)

    parser_forget = subparsers.add_parser('forget', help="Remove the document's data from database.")
    parser_forget.add_argument('path', type=os.path.abspath)
    args = parser.parse_args()

    app = PdfStat(db_path, zathura_hist_path)
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