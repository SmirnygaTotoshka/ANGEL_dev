#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
NetChop 3.1 -  neural network
https://github.com/pdxgx/pepsickle
https://doi.org/10.1093/bioinformatics/btab628

pepsickle доступна для всех типов данных
'''

import argparse
import pandas as pd
import os
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq

#Path to the conda environment, installed by the instruction from https://github.com/pdxgx/pepsickle
PEPSICKLE_ENV_HOME = "/home/stotoshka/Soft/anaconda3/envs/pepsickle-v0-2-1/"

def isCorrectSequence(sequence):
    alphabet = list("ACDEFGHIKLMNPQRSTVWY")
    seq = sequence.strip()
    for i in range(0,len(seq)):
        if seq[i] not in alphabet:
            return False
    return True

parser = argparse.ArgumentParser(description='Pepsickle can run on in vitro and in vivo data. Before launch in another computer dont forget change PEPSICKLE_ENV_HOME inside the script.')
parser.add_argument("-t","--type", choices=["C","I"], help="Type of data. If you use epitope model, ignore it.",default="C")
parser.add_argument("-m","--model", choices=["epitope","in-vitro","in-vitro-2"], help="allows the use of models trained on alternative data."
            "Defaults to epitope based model, with options for in-vitro based gradient boosted model (in-vitro) or an experimental neural network based in-vitro model (in-vitro-2)",
                    default="epitope")
parser.add_argument("input", help="Text file with sequences, 1 per line")
parser.add_argument("output", help="Output file")
args = parser.parse_args()



#Convert input to fasta file
with open(args.input, "r") as sequences, open(os.path.join(os.path.dirname(args.input),"pepsickle_tmp.fasta"),"w") as tmp:
    seq_records = []
    for i,seq in enumerate(sequences):
        if not isCorrectSequence(seq):
            print(f"Sequence at line {i+1} not correct")
        else:
            seq_records.append(SeqRecord(Seq(seq.strip()), id=seq.strip(), description=""))
    SeqIO.write(seq_records, tmp, "fasta")

if args.model == "epitope":
    command = f"conda run -p {PEPSICKLE_ENV_HOME} pepsickle -f {os.path.join(os.path.dirname(args.input),'pepsickle_tmp.fasta')} --human-only >> {os.path.join(os.path.dirname(args.input),'pepsickle_result.txt')}"
else:
    command = f"conda run -p {PEPSICKLE_ENV_HOME} pepsickle -f {os.path.join(os.path.dirname(args.input),'pepsickle_tmp.fasta')} -m {args.model} -p {args.type} --human-only >> {os.path.join(os.path.dirname(args.input),'pepsickle_result.txt')}"

print(command)
os.system(command)
print("Finish")

#Convert to excel, delete temporary files
result = pd.read_csv(os.path.join(os.path.dirname(args.input),'pepsickle_result.txt'),sep = "\t")
result.to_excel(args.output, index = False)
os.remove(os.path.join(os.path.dirname(args.input),"pepsickle_tmp.fasta"))
os.remove(os.path.join(os.path.dirname(args.input),'pepsickle_result.txt'))