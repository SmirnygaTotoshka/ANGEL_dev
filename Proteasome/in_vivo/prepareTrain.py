#!/usr/bin/env python
# -*- coding: utf-8 -*-
import multiprocessing

import pandas as pd
import numpy as np
from sklearn.model_selection import GroupKFold
import argparse
from toolsInvivo import getSamplesMulti, isCorrectSequence

parser = argparse.ArgumentParser()
parser.add_argument("-t","--threads", type=int, choices=range(1,multiprocessing.cpu_count() * 3), help="Window`s radius",default=1)
parser.add_argument("-w","--window", type=int, choices=range(2,6), help="Window`s radius",default=2)
args = parser.parse_args()

'''
Обучающая выборка состоит из данных масс-спектрометрии БД IEDB
'''
#Фильтрация
iedb_elution = pd.read_csv("Proteasome/data/raw/epi_mhc_elution_human_total.csv",sep = ";", low_memory=False)
iedb_elution["as_char_value"] = np.where(iedb_elution["as_char_value"] == 'Negative', 'Negative', "Positive")
iedb_elution_filtered = iedb_elution.query("e_region_domain_flag == 'Exact Epitope'")
# Убрать записи с сомнительными комментариями
iedb_elution_filtered = iedb_elution_filtered[~iedb_elution_filtered["as_comments"].str.contains("bad", na=False)]
iedb_elution_filtered = iedb_elution_filtered[~iedb_elution_filtered["as_comments"].str.contains("did not", na=False)]
iedb_elution_filtered = iedb_elution_filtered[~iedb_elution_filtered["as_comments"].str.contains("TAP deficient ", na=False)]
iedb_elution_filtered = iedb_elution_filtered[~iedb_elution_filtered["as_comments"].str.contains("predict", na=False)]
iedb_elution_filtered = iedb_elution_filtered[~iedb_elution_filtered["as_comments"].str.contains("ERAP1 silencing", na=False)]
# Положительные случаи (Отрицательных слишком мало и будут мешать)
iedb_elution_filtered = iedb_elution_filtered.query("as_char_value == 'Positive'")
# Первый класс и корректно записанные последовательности
iedb_elution_filtered = iedb_elution_filtered[iedb_elution_filtered["class"] == "I"]
iedb_elution_filtered = iedb_elution_filtered[iedb_elution_filtered["linear_peptide_seq"].apply(isCorrectSequence)]
iedb_elution_filtered = iedb_elution_filtered[iedb_elution_filtered["sequence"].apply(isCorrectSequence)]
for i in iedb_elution_filtered.index:
	if iedb_elution_filtered.loc[i, "linear_peptide_seq"] not in iedb_elution_filtered.loc[i, "sequence"]:
		iedb_elution_filtered.drop(index=i,inplace=True)
# Удалить дупликаты, оставить только эпитопы подходящей длины, которые встречаются в последовательности 1 раз (т.е. их местоположение
# можно однозначно определить)
iedb_elution_filtered = iedb_elution_filtered.loc[:,["linear_peptide_seq","sequence"]]
iedb_elution_filtered = iedb_elution_filtered.drop_duplicates()
iedb_elution_filtered = iedb_elution_filtered[(iedb_elution_filtered["linear_peptide_seq"].str.len() > 7) & (iedb_elution_filtered["linear_peptide_seq"].str.len() < 14)]
for i in iedb_elution_filtered.index:
	iedb_elution_filtered.loc[i,"count"] = iedb_elution_filtered.loc[i,"sequence"].count(iedb_elution_filtered.loc[i,"linear_peptide_seq"])
iedb_elution_filtered = iedb_elution_filtered.query("count == 1")
iedb_elution_filtered = iedb_elution_filtered.loc[:,["linear_peptide_seq","sequence"]]
iedb_elution_filtered = iedb_elution_filtered.reset_index(drop = True)
iedb_elution_filtered.to_csv("Proteasome/in_vivo/train/total_train_invivo.csv",sep = ";", index =False)
print(f"Num substrate = {len(iedb_elution_filtered.sequence.unique())}")
# Выборки для 5CV

fiveCV = GroupKFold(n_splits=5)
for i, (train_index, test_index) in enumerate(fiveCV.split(X = iedb_elution_filtered["linear_peptide_seq"],groups=iedb_elution_filtered["sequence"])):
    print(f"Fold {i}:")

    train_fold = iedb_elution_filtered.loc[train_index,:]
    test_fold = iedb_elution_filtered.loc[test_index,:]

    print(f"Train {len(train_fold.sequence.unique())}")
    ready_train_fold = getSamplesMulti(train_fold,number_threads = args.threads, w = args.window)
    print(f"Test {len(test_fold.sequence.unique())}")
    ready_test_fold = getSamplesMulti(test_fold,number_threads = args.threads, w = args.window)

    train_fold.to_csv(f"Proteasome/in_vivo/train/train_invivo_{args.window}_{i}.csv", index=False, sep=";")
    test_fold.to_csv(f"Proteasome/in_vivo/train/test_invivo_{args.window}_{i}.csv", index=False, sep=";")
    ready_train_fold.to_csv(f"Proteasome/in_vivo/train/train_ready_invivo_{args.window}_{i}.csv", index = False, sep = ";")
    ready_test_fold.to_csv(f"Proteasome/in_vivo/train/test_ready_invivo_{args.window}_{i}.csv", index = False, sep = ";")