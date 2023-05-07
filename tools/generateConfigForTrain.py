#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Генерирует конфиг для консольной версии PASS для обучения моделей (OLMPASSdoSAR.exe)
# Example:
# python tools/generateConfigForTrain.py -l 4 -b meow -s meow.sdf -a activity -p model/meow meow.txt
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Generate config for PASS train. Remember, PASS home directory is config directory. "
                                                 "All paths in config should be relative to this directory!")
    parser.add_argument("output", help="Path to the generated config.")
    parser.add_argument("-l","--level", help="Level of MNA descriptors using for model building",type = int,default = 3)
    parser.add_argument("-b","--base_name", help="Name of SAR Base",default="tmp",type= str)
    parser.add_argument("-s","--sdf", help="Relative path to train data in SDF format. With extension.")
    parser.add_argument("-a","--activity", help="Column name contains activity.", type = str) #default - создавать заряженные последовательности
    parser.add_argument("-p","--model_output", help="Relative path to PASS output. Without extension.", default="tmp")
    args = parser.parse_args()

    with open(args.output, "w", encoding="cp1251") as tr_cfg:
        tr_cfg.write(f"BaseCreate={args.level};{args.base_name}\n")
        tr_cfg.write(f"BaseAddNewData={args.sdf};{args.activity}\n")
        tr_cfg.write(f"BaseSave={args.model_output}\n")
        tr_cfg.write("BaseTraining\n")
        tr_cfg.write("BaseValidation\n")
        tr_cfg.write("BaseClose\n")
    print("Success")