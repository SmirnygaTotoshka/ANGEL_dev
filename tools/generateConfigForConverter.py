#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Генерирует конфиг для конвертера SeqToSDF.py https://github.com/SmirnygaTotoshka/SequenceToSDF
# Example
# python generateConfigForConverter.py -i HLA/data/train/test_HLA_1.csv -o HLA/data//train/sdf -c peptide test.json
# Paths should be absolute
import json
import argparse
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate config for launch SeqToSDF.")
    parser.add_argument("output", help="Path to the generated config.")
    parser.add_argument("-i","--con_input", help="Path to converter input csv file. If file doesn`t exist, the script will throw exception.", required=True)
    parser.add_argument("-o","--con_output", help="Path to converter output directory. If dir doesn`t exist, it will be created.", required= True)
    parser.add_argument("-c","--column", help="Column with sequences. It will be used for convertation to the chemical structure", required=True)
    parser.add_argument("-u","--uncharged", action='store_false', help="Should be sequences are neutral?") #default - создавать заряженные последовательности
    parser.add_argument("-a","--alphabet", help="Which type sequences are used?",choices=["DNA","RNA","protein"], default="protein")
    parser.add_argument("-t","--threads", help="How many threads should be used. It has limit 1 < t < 2 * cpu_cores",type=int,default=1)
    parser.add_argument("-s","--separator", help="What separator are used in csv file.",type=str, default=";")
    parser.add_argument("-f","--filename", help="Custom output filename. Default is input filename.",default="")
    parser.add_argument("-st","--save_tmp", action='store_false',help="Should it saves temporary files after execution?")#default - удалять временные файлы
    args = parser.parse_args()

    if args.filename == "":
        filename = os.path.splitext(os.path.basename(args.con_input))[0]
    else:
        filename = args.filename

    config = {
        "input": args.con_input,
        "output": args.con_output,
        "column": args.column,
        "charged": args.uncharged,
        "alphabet": args.alphabet,
        "threads": args.threads,
        "separator": args.separator,
        "filename": filename,
        "delete_tmp": args.save_tmp
    }

    if not os.path.exists(config["input"]):
        raise BaseException("Input file doesn`t exist")

    if not os.path.exists(config["output"]):
        os.mkdir(config["output"])

    with open(args.output, "w", encoding="utf-8") as file:
        file.write(json.dumps(config))

    print("Success")