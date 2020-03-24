from pathlib import Path
from functools import namedtuple
from datetime import datetime
import sqlite3

LogEntry = namedtuple("LogEntry", "page time")

def make_entry(page, timestamp):
    return LogEntry(page, datetime.fromtimestamp(timestamp))

class SqlDB:
    def __init__(self, db_path):
        self._conn = sqlite3.connect(str(db_path))
        self._conn.execute("CREATE TABLE IF NOT EXISTS logs (path text, page integer, time integer)")
        # self._conn.execute("CREATE TABLE IF NOT EXISTS metadata (path text, numpages integer)")
    def tracked(self):
        return [a for (a,) in self._conn.execute("SELECT DISTINCT path FROM logs")]
    def doc_data(self, path):
        cursor = self._conn.cursor()
        cursor.execute("SELECT page, time FROM logs WHERE path=? ORDER BY time ASC", (path,))
        log = [make_entry(page, timestamp) for (page, timestamp) in cursor]
        return log
    def last_entry(self, path):
        cursor = self._conn.cursor()
        cursor.execute("SELECT page, time FROM logs WHERE path=? ORDER BY time DESC", (path,))
        page, timestamp = cursor.fetchone()
        return make_entry(page, timestamp)
    def insert(self, path, entry):
        self._conn.execute("INSERT INTO logs values(?,?,?)", (path, entry.page, round(entry.time.timestamp())))
    def update(self, path, entry):
        last_time = self.last_entry(path).time.timestamp()
        self._conn.execute("UPDATE logs SET page=?, time=? WHERE path=? AND time=?", (entry.page, round(entry.time.timestamp()), path, last_time))
    def delete(self, path):
        self._conn.execute("DELETE FROM logs WHERE path=?", (path,))
    def is_tracked(self, path):
        cursor = self._conn.cursor()
        cursor.execute("SELECT 1 FROM logs WHERE path=?", (path,))
        return True if cursor.fetchone() else False
    def save(self):
        self._conn.commit()


# from hashlib import sha256
# class PlainDB:
#     def __init__(self, path):
#         self._tracked_list = path/'tracked'
#         # self._tracked_list.touch
#     def tracked_files(self):
#         with self._tracked_list.open('r') as f:
#             return [Path(x.strip()) for x in f.readlines()]
#     def track(self, path):
#         t = self.tracked_files()
#         if path in t:
#             return t
#         t.append(path)
#         with self._tracked_list.open('a') as f:
#             f.write(str(path)+'\n')
#             return t

# import json
# class JsonDB:
#     def __init__(self, path):
#         self.path = path
#         if path.exists():
#             with path.open() as f:
#                 self._data = json.load(f)
#         else:
#             self._data = {}
#     def save(self):
#         with self.path.open('w') as f:
#             json.dump(self._data, f)
#     def update(self, path, entry):
#         self._data[str(path)].append(entry)
#     def track(self, path):
#         self._data[str(path)] = []