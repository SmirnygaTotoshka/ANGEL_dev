#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Генерирует конфиг для консольной версии PASS для предсказания (OLMPASS2CSV.exe)
# Example:
# python tools/generateConfigForPrediction.py -m meow.MSAR -s meow.sdf -a activity -p result meow.txt
import argparse
import os

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Generate config for PASS зкувшсешщт. Remember, PASS home directory is config directory. "
                                                 "All paths in config should be relative to this directory!")
    parser.add_argument("output", help="Path to the generated config.")
    parser.add_argument("-m","--model", help="Relative path to SAR Base. With extension (.MSAR).",default="tmp",type= str)
    parser.add_argument("-s","--sdf", help="Relative path to test data in SDF format. With extension.")
    parser.add_argument("-a","--activity", help="Column name contains activity.", type = str) #default - создавать заряженные последовательности
    parser.add_argument("-p","--pred_output", help="Relative path to prediction directory(!). Output name is <test_filename> <model_filename>.csv", default="tmp")
    args = parser.parse_args()

    with open(args.output, "w", encoding="cp1251") as val_cfg:
        val_cfg.write(f"InputName={args.sdf}\n")
        val_cfg.write(f"IdKeyField={args.activity}\n")
        val_cfg.write(f"BaseName={args.model}\n")
        val_cfg.write(f"OutputName={os.path.join(args.pred_output,os.path.splitext(os.path.basename(args.sdf))[0]+ '-' +os.path.splitext(os.path.basename(args.model))[0] + '.csv')}\n")
    print("Success")