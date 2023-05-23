#!/usr/bin/env python
# -*- coding: utf-8 -*-
import traceback

import pandas as pd
import argparse
import requests
from io import StringIO
from Bio import SeqIO
from requests.adapters import HTTPAdapter, Retry

def retrieveFromUniprot(id, epitopes):
    base_query = "https://rest.uniprot.org/uniprotkb/{}.fasta"
    query = base_query.format(id)
    s = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=0.1,
                    status_forcelist=[500, 502, 503, 504])
    s.mount('https://', HTTPAdapter(max_retries=retries))
    try:
        response = s.get(query)
    except:
        return None
    io = StringIO(response.text)
    flag = True
    for r in SeqIO.parse(io, format="fasta"):
        for e in epitopes:
            if e not in r.seq:#Если какого-то эпитопа нет, то не берем в рассмотрение
                flag = False
        if flag:
            return str(r.seq)
        else:
            return None


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()

parser = argparse.ArgumentParser(description = "Download reference sequence by uniprot id, map to the epitope table and drop epitopes without reference sequence.")
parser.add_argument("input", type=str, help="Path to the input (excel)")
parser.add_argument("output", type=str, help="Path to the output (excel)")
parser.add_argument("accession", type=str, help="Column name with accession ids.")
parser.add_argument("epitopes", type=str, help="Column name with epitopes sequences.")
parser.add_argument("header", type=int, help="Number of row with header (from 0)")

args = parser.parse_args()

input_tbl = pd.read_excel(args.input, header=args.header)
total = len(input_tbl.index)
success = 0
failed = 0
try:
    for i in input_tbl.index:
        try:
            ids = input_tbl.loc[i,args.accession].split(";")
            seq = None
            for j in ids:
                seq = retrieveFromUniprot(j, list(input_tbl.loc[i,args.epitopes]))
                if seq is not None:
                    input_tbl.loc[i, "id_ref_seq"] = j
                    input_tbl.loc[i, "ref_seq"] = seq
                    success += 1
                    break
            if seq is None:
                failed += 1
            printProgressBar(i+1, total, suffix=f"success={success}; failed={failed}; total={total}")
        except Exception as e:
            traceback.print_exc()
            print(f"{i} {id}")
except:
    traceback.print_exc()
finally:
    input_tbl.dropna(subset=["ref_sequence"], inplace=True)
    input_tbl.to_excel(args.output, index = False)