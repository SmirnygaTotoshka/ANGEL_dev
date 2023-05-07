#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import argparse
from toolsInvitro import generateSamples, isCorrectSequence

parser = argparse.ArgumentParser()
parser.add_argument("-t","--type", choices=["I","C"], help="Type of proteasome: C - 20S constitutive, I - 20S immunoproteasome",default="C")
parser.add_argument("-w","--window", type=int, choices=range(2,6), help="Window`s radius",default=2)
args = parser.parse_args()

if args.type == "C":
    type = "C"
    train_path = "Proteasome/in_vitro/const/train/total_train_const.csv"
    validation_path = "Proteasome/in_vitro/const/validation"
    name = "const"
else:
    type = "I"
    train_path = "Proteasome/in_vitro/immuno/train/total_train_immuno.csv"
    validation_path = "Proteasome/in_vitro/immuno/validation"
    name = "immuno"

'''
Валидационная выборка состоит из двух датасетов
1) https://github.com/pdxgx/pepsickle-paper запуском скрипта scripts/dataset_processing/prep_winter_data.py
2) 10.1007/s00251-014-0815-0 supplementary
'''

total_train = pd.read_csv(train_path, sep = ";")
ready_total_train = generateSamples(total_train, window_radius=args.window)
ready_total_train.to_csv(f"{validation_path}/ready_train_{name}_{args.window}.csv", index = False, sep = ";")


winter_dataset = pd.read_csv("Proteasome/data/raw/pepsickle_winter_et_al_cleavage_fragments.csv")
winter_dataset_filtered = winter_dataset.query("Organism == 'human'")
winter_dataset_filtered = winter_dataset_filtered.query("Proteasome != @type")
winter_dataset_filtered = winter_dataset_filtered.query("Subunit == '20S'")
winter_dataset_filtered = winter_dataset_filtered[winter_dataset_filtered["fragment"].apply(isCorrectSequence)]
winter_dataset_filtered = winter_dataset_filtered[winter_dataset_filtered["full_sequence"].apply(isCorrectSequence)]
winter_dataset_filtered = winter_dataset_filtered[~winter_dataset_filtered["full_sequence"].isin(total_train['substrate'])]
for i in winter_dataset_filtered.index:
	if winter_dataset_filtered.loc[i, "fragment"] not in winter_dataset_filtered.loc[i, "full_sequence"]:
		winter_dataset_filtered.drop(index=i,inplace=True)

winter_dataset_filtered = winter_dataset_filtered.rename(columns={"full_sequence": "substrate"})
winter_dataset_filtered = winter_dataset_filtered.loc[:,["fragment","substrate","exclusions"]]

calis_data = pd.read_csv("Proteasome/data/raw/calis_et_all_cleavage.txt",sep = " ")
calis_data_filtered = calis_data.query("Proteasome_type == @type")
calis_data_filtered["sequence"] = calis_data_filtered["cleavage_sites"].str.replace("\\|","")
calis_data_filtered = calis_data_filtered[calis_data_filtered["sequence"].apply(isCorrectSequence)]
calis_data_filtered = calis_data_filtered[~calis_data_filtered["sequence"].isin(total_train['substrate'])]

calis_result = pd.DataFrame(columns=["fragment", "substrate","exclusions"])

k = 0
for i in calis_data_filtered.index:
    previous_start = 0
    for j in calis_data_filtered.loc[i,"cleavage_sites"]:
        site = calis_data_filtered.loc[i,"cleavage_sites"].find("|",previous_start)
        peptide = calis_data_filtered.loc[i,"cleavage_sites"][0:site].replace("\\|","")
        previous_start = site + 1
        calis_result.loc[k] = [peptide, calis_data_filtered.loc[i,"sequence"],""]
        k += 1

validation_invitro = pd.concat([winter_dataset_filtered, calis_result], ignore_index = True)
validation_invitro = validation_invitro.drop_duplicates(subset= ['fragment', 'substrate'])
validation_invitro.reset_index(inplace=True,drop = True)

validation_invitro.to_csv(f"{validation_path}/total_validation_{name}.csv", index = False, sep = ";")
print(f"Num substrate = {len(validation_invitro.substrate.unique())}")

ready_validation = generateSamples(validation_invitro, excluded="exclusions", window_radius=args.window)
validation_invitro.to_csv(f"{validation_path}/ready_validation_{name}_{args.window}.csv", index = False, sep = ";")
