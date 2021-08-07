#!/bin/bash python

import sys

sys.path.append("..")

from backend import manager


if __name__ == "__main__":
    manager.run()
