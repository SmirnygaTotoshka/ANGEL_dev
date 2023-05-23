#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import sys
from glob import glob
import os
import traceback

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Удалить непонятные кавычки из имени файлов вдиректории")
    parser.add_argument("inputdir", help="Путь к папке")
    args = parser.parse_args()

    try:
        for f in glob(f"{args.inputdir}/*"):
            dst = f.replace("'","")
            os.rename(f,dst)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)
