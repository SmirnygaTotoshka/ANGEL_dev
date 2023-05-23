#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import pandas as pd

WINDOWS_RADIUS = 3
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("uuid")
    parser.add_argument("threshold",type=float,default=0)
    args = parser.parse_args()

    sample = pd.read_csv(fr"C:\Users\SmirnygaTotoshka\Desktop\diplom\angel_userdata\{args.uuid}\{args.uuid}.csv", sep=";",header=0)

    prediction = pd.read_csv(fr"C:\Users\SmirnygaTotoshka\Desktop\diplom\angel_userdata\{args.uuid}\{args.uuid}_Proteasome.csv", sep=";",header=0, decimal=",")
    prediction = prediction.drop(columns=["Substructure Descriptors", "New Descriptors", "Possible Activities at Pa>Pi"])

    output = pd.DataFrame(columns=["Residue", "Protein Number", "Score", "Active"])
    k = 0
    for i in sample.index:
        sequence = sample.loc[i,"proteins"]
        id = i
        prediction_subset = prediction[prediction["id"] == id].reset_index(drop=True)
        prediction_subset["1"] = prediction_subset["1"].fillna(0)
        for j, residue in enumerate(sequence):
            if j < WINDOWS_RADIUS or j > len(sequence) - WINDOWS_RADIUS - 1:
                score = 0
            else:
                score = prediction_subset.loc[j - WINDOWS_RADIUS, "1"]
            active = '+' if score >= args.threshold else '-'
            output.loc[k] = [residue, id, score, active]
            k+=1
    output.to_csv(rf"C:\Users\SmirnygaTotoshka\Desktop\diplom\angel_userdata\{args.uuid}\{args.uuid}_Proteasome_result.csv",sep=";",index=False)
