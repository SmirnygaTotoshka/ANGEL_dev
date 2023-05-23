#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import sys
import traceback
import pandas as pd

WINDOW_RADIUS = 3

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Подготовить входной файл для предсказания на сайты протеасомы. "
                                                 "Представить каждую последовательность как множество подстрок с помощью скользящего окна [i-w;i+w+1)")
    parser.add_argument("uuid")
    args = parser.parse_args()

    try:
        input_file = pd.read_csv(fr"C:\Users\SmirnygaTotoshka\Desktop\diplom\angel_userdata\{args.uuid}\{args.uuid}.csv",sep=";")
        output_table = pd.DataFrame(columns=["peptide", "id"])
        k = 0
        for i in input_file.index:
            protein = input_file.loc[i, "proteins"]
            for j in range(0 + WINDOW_RADIUS, len(protein) - WINDOW_RADIUS):
                output_table.loc[k] = [protein[(j-WINDOW_RADIUS):(j+WINDOW_RADIUS+1)], i]
                k+=1
        output_table.to_csv(fr"C:\Users\SmirnygaTotoshka\Desktop\diplom\angel_userdata\{args.uuid}\ready_Proteasome_{args.uuid}.csv",sep=";",index=False)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)
