import sys
from .detector import Detector
from .decoder import decode, DecodeError


def detect(path):
    for candidate in Detector().detect(path):
        try:
            return decode(candidate)
        except DecodeError as e:
            pass
    return None
