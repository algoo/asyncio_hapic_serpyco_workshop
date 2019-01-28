# coding: utf-8

import socket  # here in order not to avoid
import sys


def get_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 1))  # connect() for UDP doesn't send packets
    return s.getsockname()[0]


def get_python_version() -> str:
    v = sys.version_info
    return f"{v.major}.{v.minor}.{v.micro}"
