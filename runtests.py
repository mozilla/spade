#!/usr/bin/env python
"""
Run py.test after setting up the vendor library and DJANGO_SETTINGS_MODULE.

"""
import os
import sys

from _pytest.core import main as pytest_main

from spade.vendor import add_vendor_lib

def main():
    os.environ["DJANGO_SETTINGS_MODULE"] = "spade.tests.settings"
    add_vendor_lib()
    args = sys.argv[1:]
    if not args:
        args = ["spade/tests/"]
    raise SystemExit(pytest_main(args))


if __name__ == "__main__":
    main()
