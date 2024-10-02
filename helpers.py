from typing import Callable, Iterable

def get_srcset(srcset_raw: str):
    "Get a HTML srcset in dict form."
    if not srcset_raw:
        return {}
    srcset = dict()
    for src in srcset_raw.split(','):
        url, width = src.strip().split(' ', 1)
        assert width.endswith('w')
        width = int(width[:-1])
        srcset[width] = url
    srcset['max'] = url
    return srcset

def collate[T, K](
    iterable: Iterable[T],
    pred: Callable[[T], K]
) -> dict[K, list[T]]:
    "Collate an iterable by a predicate."
    collation = {}
    for item in iterable:
        key = pred(item)
        collation.setdefault(key, []).append(item)
    return collation