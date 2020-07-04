from functools import namedtuple
from itertools import tee

def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def weighted(pairs):
    s = 0
    total_weight = 0
    for x, weight in pairs:
        s += x*weight
        total_weight += weight
    return s/total_weight

def pages_per_day(hist, factor=.8):
    reference_time = hist[0].time
    def weight(entry):
        return factor**(reference_time-entry.time).days

    return weighted(
        (a.page-b.page, weight(a)) for a,b in pairwise(hist)
    )