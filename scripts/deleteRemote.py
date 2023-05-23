#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import sys
import traceback
from shutil import rmtree

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Удалить директорию после работы.")
    parser.add_argument("uuid")
    args = parser.parse_args()

    try:
        rmtree(fr"C:\Users\SmirnygaTotoshka\Desktop\diplom\angel_userdata\{args.uuid}")
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)
