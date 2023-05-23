#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Скрипт делают сводку результатов 5-кратной кросс-валидации для моделей TAP. Отличие в том, что эти модели имеют 1 гиперпараметр, а не 2
internal - HST файлы PASS, внутренняя валидация качества модели по leave-one-out и 20-кратной кросс-валидации
external - csv файлы, результаты предсказания на тестовой выборке

input - директория, содержащий один тип данных (internal или external)
output - путь к таблице
'''


import pandas as pd
import argparse
from glob import glob
from sklearn.metrics import roc_auc_score,average_precision_score
import re
import os

def group_by_folds(files, mode):
    groups = {}
    for f in files:
        if mode == "console":
            desc = os.path.splitext(os.path.basename(f))[0].split("-")[1] #Возьмем правую часть имени файла, за имя модели
        else:
            s = os.path.splitext(os.path.basename(f))[0]
            desc = s[s.find("(") + 1:s.find(")")]
        components_desc = re.split("_",desc)
        key = "_".join([components_desc[1],components_desc[3]])#model_level
        if key not in groups.keys():
            groups[key] = [f]
        else:
            groups[key].append(f)
    return groups

parser = argparse.ArgumentParser()
parser.add_argument("type", choices=["internal","external"], help="Type of validation. interal - PASS HST files, external - csv files with prediction",default="internal")
parser.add_argument("program", choices=["console","GUI"], help="Type of executed PASS program",default="console")
parser.add_argument("input", help="Path to directory with files")
parser.add_argument("output", help="Path to excel table")
args = parser.parse_args()

if args.type == "internal":
    if args.program == "console":
        glob_path = f"{args.input}/*.HST"
        header = "No	 Check	 Number	 IAP	 20-Fold	 Activity"
    else:
        glob_path = f"{args.input}/*_CRV.LOG"
        header = "No	 Check	 Group	 Number	 IAP	 20-Fold	 Activity"

    results = glob(glob_path)
    tbl = pd.DataFrame(columns=["model_name", "fold", "descriptor_level", "iap", "twentyCV", "activity", "num_subst"])
    for r in results:
        with open(r, "r", encoding='cp1252') as f:
            split_name = re.split("_", os.path.splitext(os.path.basename(r))[0])
            model_name = split_name[1]
            level = split_name[3]
            fold = split_name[2]
            lines = f.readlines()
            flag = False
            for line in lines:
                if header in line:
                    flag = True
                    continue
                if line == "\n" and flag:
                    break
                if flag:
                    components = re.split("\t\\s+", line)
                    num_subst = components[2]
                    iap = components[3]
                    twentyCV = components[4]
                    activity = components[5].strip()
                    row = pd.DataFrame.from_dict({"model_name": [model_name],
                                                  "fold": int(fold),
                                                  "descriptor_level": [int(level)],
                                                  "num_subst": [int(num_subst)],
                                                  "iap": [float(iap.replace(",", "."))],
                                                  "twentyCV": [float(twentyCV.replace(",", "."))],
                                                  "activity": [int(activity)]})
                    tbl = pd.concat([tbl, row], ignore_index=True)
            if not flag:
                print(f"{r} not any predictable activity")
    tbl.to_excel(args.output, index = False)
else:
    if args.program == "console":
        glob_path = f"{args.input}/*.csv"
        columns_to_drop = ["Substructure Descriptors", "New Descriptors", "Possible Activities at Pa>Pi"]
        header = 0
    else:
        glob_path = f"{args.input}/*.CSV"
        columns_to_drop = ["Substructure Descriptors", "New Descriptors", "Possible Activities at Pa > Pi"]
        header = 4

    results = glob(glob_path)
    models = group_by_folds(results,args.program)
    result = pd.DataFrame(columns=["model", "level", "auc_roc", "ap"])
    i = 0
    for k, folds in models.items():
        comps = re.split("_",k)
        model_name = f"{comps[0]}"
        level = int(comps[1])
        union = pd.DataFrame()
        for f in folds:
            tbl = pd.read_csv(f, sep=";", header=header,decimal=",")
            union = pd.concat([union, tbl])
        union = union.drop(columns=columns_to_drop)
        union = union.dropna()
        union = union.rename(columns={union.columns[0]: "activity"})
        auc_roc = roc_auc_score(union["activity"], union["1"])
        ap = average_precision_score(union["activity"], union["1"])
        result.loc[i] = [model_name, level, auc_roc, ap]
        i += 1
    result.to_excel(args.output, index = False)