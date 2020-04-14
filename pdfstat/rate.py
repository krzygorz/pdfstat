from functools import namedtuple
from itertools import tee, chain

Diff = namedtuple("Diff", "pages time")

def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)
def peek(iterable):
    x = next(iterable)
    return x, chain([x], iterable)

def weighted(pairs):
    s = 0
    total_weight = 0
    for x, weight in pairs:
        s += x*weight
        total_weight += weight
    return s/total_weight

def pages_per_day(hist, factor=.8):
    mostrecent, hist = peek(hist) # kinda hacky
    def weight(entry):
        return factor**(mostrecent.time-entry.time).days

    return weighted(
        (a.page-b.page, weight(a)) for a,b in pairwise(hist)
    )