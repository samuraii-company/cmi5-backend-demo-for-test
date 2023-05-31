# flake8: noqa
import re
from typing import Union

Matchable = Union[dict, list, set, tuple]


def urljoin(*parts: str):
    """Прокаченая версия urljoin."""

    if len(parts) == 0:
        return ""

    parsed_parts = [
        re.sub(r"^\/+|\/+$", "", part, 0, re.MULTILINE) for part in parts if part
    ]
    parsed_parts = [part for part in parsed_parts if len(part) > 0]

    url = "/".join(parsed_parts)

    if parts[0] == "/":
        url = "/" + url

    return url


def matches(obj: Matchable, sample: Matchable, any_order: bool = False) -> bool:
    """Matches a given object against another
    which can contain "wildcard" elements (`...`)
    :return: bool
    """
    if isinstance(sample, dict) and isinstance(obj, dict):
        if ... in sample:
            keys = set(sample) - {...}
        else:
            keys = set(sample) | set(obj)
        for k in keys:
            if k not in sample or k not in obj:
                return False
            if sample[k] is ...:
                continue
            if not matches(obj[k], sample[k]):
                return False

        if ... in sample and sample[...] is not ...:
            remaining = set(obj) - set(sample) - {...}
            if len(remaining) != 1:
                return False

            return matches(obj[remaining.pop()], sample[...])

        return True

    elif isinstance(sample, set) and isinstance(obj, set):
        if ... in sample:
            return (sample - {...}).issubset(obj)
        else:
            return sample == obj

    elif (isinstance(sample, list) and isinstance(obj, list)) or (
        isinstance(sample, tuple) and isinstance(obj, tuple)
    ):
        if any_order is True:
            obj = sorted(obj)
            sample = sorted(obj)
        obj_idx = 0
        skip = False
        for idx, el in enumerate(sample):
            if el is ...:
                if idx == len(sample) - 1:
                    return True
                skip = True
                continue

            if skip:
                while not matches(obj[obj_idx], el):
                    if obj_idx == len(obj) - 1:
                        return False
                    obj_idx += 1
                skip = False

            if obj_idx >= len(obj) or not matches(
                obj[obj_idx], el, any_order=any_order
            ):
                return False

            obj_idx += 1

        if not skip and obj_idx != len(obj):
            return False

        return True

    return sample == obj
