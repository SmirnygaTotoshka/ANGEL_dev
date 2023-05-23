#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor

This script download data about TAP binders from MHC BN database

author: Smirnov Anton
date: 16 Feb 2023
"""

import requests as req
import pandas as pd
import time
from datetime import datetime
import os

PROJECT_DATA_PATH = "/home/stotoshka/Documents/ANGEL_dev/TAP/data/raw"
MHCBN_TAPBINDER_SEQ_URL = "https://webs.iiitd.edu.in/cgibin/mhcbn/tapbinder_download.pl"
MHCBN_DISPLAY_URL = "https://webs.iiitd.edu.in/cgibin/mhcbn/display.pl"
DISPLAY_PARAMS = {"field":"sequence",\
                  "value":""}

def isCorrectSequence(seq):
    alphabet = list("ACDEFGHIKLMNPQRSTVWY")
    seq = str(seq).strip()
    for i in range(0,len(seq)):
        if seq[i] not in alphabet:
            return False
    return True

print("Download list of sequences")
seq_table_req_res = req.get(MHCBN_TAPBINDER_SEQ_URL)
if seq_table_req_res.status_code == 200:
    seq_table = pd.read_html(seq_table_req_res.text)[1]
else:
    raise Exception("Cannot get list of database sequences, "\
                    f"because HTTP Error {seq_table_req_res.status_code}")
    sys.exit(1)

print("----------------------------\nCleaning data")
seq_table = seq_table.drop(index = 0)
print(f"Total {seq_table.shape}")
seq_table = seq_table.rename(columns = {0:"id",1:"seq"})
seq_table = seq_table.drop_duplicates(subset = "seq", ignore_index = True)
print(f"Total unique {seq_table.shape}")

seq_table["isCorrectSeq"] = seq_table["seq"].apply(isCorrectSequence)
seq_table = seq_table.loc[seq_table["isCorrectSeq"],:]
print(f"Total unique and correct {seq_table.shape}")

all_records = pd.DataFrame()
for i in seq_table.index:
    DISPLAY_PARAMS["value"] = seq_table.loc[i,"seq"]
    record_req = req.get(MHCBN_DISPLAY_URL, params = DISPLAY_PARAMS)
    if record_req.status_code == 200:
        record_tables = pd.read_html(record_req.text)
        for table in record_tables:
            record = table.T
            record.columns = record.iloc[0]
            record = record.drop(index = 0)
            if all_records.empty:
                all_records = record.copy()
            else:
                all_records = pd.concat([all_records, record])
        print(f"{DISPLAY_PARAMS['value']} SUCCESS. Total records {all_records.shape}")
    else:
        print(f"Cannot get records for {DISPLAY_PARAMS['value']}, "\
              f"because HTTP Error {seq_table_req_res.status_code}")
        continue
    time.sleep(1)
all_records.to_csv(os.path.join(PROJECT_DATA_PATH, "MHCBN_"+datetime.today().strftime('%Y-%m-%d')+".tsv"), sep="\t")
