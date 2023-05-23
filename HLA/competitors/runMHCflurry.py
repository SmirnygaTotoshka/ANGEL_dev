#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
MHCflurry
https://doi.org/10.1016/j.cels.2020.06.010
https://github.com/openvax/mhcflurry

mhcflurry-predict [-h] [--list-supported-alleles] [--list-supported-peptide-lengths] [--version] [--alleles ALLELE [ALLELE ...]] [--peptides PEPTIDE [PEPTIDE ...]] [--allele-column NAME]
                         [--peptide-column NAME] [--n-flank-column NAME] [--c-flank-column NAME] [--no-throw] [--out OUTPUT.csv] [--prediction-column-prefix NAME] [--output-delimiter CHAR]
                         [--no-affinity-percentile] [--always-include-best-allele] [--models DIR] [--affinity-only] [--no-flanking]
                         [INPUT.csv]

mhcflurry-predict-scan [-h] [--list-supported-alleles] [--list-supported-peptide-lengths]
                              [--version] [--input-format {guess,csv,fasta}]
                              [--alleles ALLELE [ALLELE ...]] [--sequences SEQ [SEQ ...]]
                              [--sequence-id-column NAME] [--sequence-column NAME] [--no-throw]
                              [--peptide-lengths L] [--results-all]
                              [--results-best {presentation_score,processing_score,affinity,affinity_percentile}]
                              [--results-filtered {presentation_score,processing_score,affinity,affinity_percentile}]
                              [--threshold-presentation-score THRESHOLD_PRESENTATION_SCORE]
                              [--threshold-processing-score THRESHOLD_PROCESSING_SCORE]
                              [--threshold-affinity THRESHOLD_AFFINITY]
                              [--threshold-affinity-percentile THRESHOLD_AFFINITY_PERCENTILE]
                              [--out OUTPUT.csv] [--output-delimiter CHAR]
                              [--no-affinity-percentile] [--models DIR] [--no-flanking]
                              [INPUT]
Стоит в отдельном окружении anaconda
'''

import argparse
import pandas as pd
import os
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq

#Path to the conda environment, installed by the instruction from https://github.com/openvax/mhcflurry
MHCFLURRY_ENV_HOME = "/home/stotoshka/Soft/anaconda3/envs/mhcflurry/"

def isCorrectSequence(sequence):
    alphabet = list("ACDEFGHIKLMNPQRSTVWY")
    seq = sequence.strip()
    for i in range(0,len(seq)):
        if seq[i] not in alphabet:
            return False
    return True

parser = argparse.ArgumentParser(description='Before launch in another computer dont forget change MHCFLURRY_ENV_HOME inside the script.')
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