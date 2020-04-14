from functools import namedtuple

Diff = namedtuple("Diff", "pages time")

def diff(entries):
    return [Diff(b.page-a.page, b.time-a.time)
                for a,b in zip(entries, entries[1:])]

def geometric(factor, start=1):
    x = start
    while True:
        yield x
        x *= factor

def days_per_page(hist):
    if len(hist) < 2:
        return None
    first = hist[0]
    last = hist[-1]

    if first.page == last.page:
        return None

    print([d.pages for d in diff(hist)])

    return (last.time - first.time).days/(last.page - first.page)
