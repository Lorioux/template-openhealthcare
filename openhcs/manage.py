#!/bin/bash python

import sys

sys.path.append("..")

from openhcs import manager


if __name__ == "__main__":
    manager.run()
