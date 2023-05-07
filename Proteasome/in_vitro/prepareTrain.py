#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from sklearn.model_selection import GroupKFold
import argparse
from toolsInvitro import generateSamples, isCorrectSequence

parser = argparse.ArgumentParser()
parser.add_argument("-t","--type", choices=["I","C"], help="Type of proteasome: C - 20S constitutive, I - 20S immunoproteasome",default="C")
parser.add_argument("-w","--window", type=int, choices=range(2,6), help="Window`s radius",default=2)
args = parser.parse_args()

if args.type == "C":
    pepsickle_type = "C"
    invitrospi_type = "20S standard"
    path = "Proteasome/in_vitro/const/train"
    name = "const"
else:
    pepsickle_type = "I"
    invitrospi_type = "20S immuno"
    path = "Proteasome/in_vitro/immuno/train"
    name = "immuno"

'''
Обучающая выборка состоит из двух датасетов
1) https://github.com/pdxgx/pepsickle-paper запуском скрипта scripts/static_dataset_extractions/extract_digestion_data.py
2) БД InvitroSPI (10.1038/s41597-022-01890-6) - https://figshare.com/articles/dataset/Database_online_items_and_scripts_from_InvitroSPI_and_a_large_database_of_proteasome-generated_spliced_and_non-spliced_peptides_/17143865/1
'''

pepsickle_data = pd.read_csv("Proteasome/data/raw/pepsickle_invitro_total.csv")
pepsickle_data_filtered = pepsickle_data.query("Organism == 'human'")
pepsickle_data_filtered = pepsickle_data_filtered.query("Proteasome == @pepsickle_type")
pepsickle_data_filtered = pepsickle_data_filtered.query("Subunit == '20S'")
pepsickle_data_filtered = pepsickle_data_filtered[pepsickle_data_filtered["fragment"].apply(isCorrectSequence)]
pepsickle_data_filtered = pepsickle_data_filtered[pepsickle_data_filtered["full_sequence"].apply(isCorrectSequence)]
for i in pepsickle_data_filtered.index:
    if pepsickle_data_filtered.loc[i, "fragment"] not in pepsickle_data_filtered.loc[i, "full_sequence"]:
        pepsickle_data_filtered.drop(index=i,inplace=True)

invitrospi = pd.read_csv("Proteasome/data/raw/ProteasomeDB.csv")
invitrospi_filtered = invitrospi.query("protIsotype == @invitrospi_type")
invitrospi_filtered = invitrospi_filtered.query('digestTime < 5')
invitrospi_filtered = invitrospi_filtered.query("proteasomeSpecies == 'human'")
invitrospi_filtered = invitrospi_filtered.query("productType == 'PCP'")
invitrospi_filtered = invitrospi_filtered.loc[(invitrospi_filtered['synErrSR2'] == 'no') | (invitrospi_filtered['synErrSR2'].isna()),:]
invitrospi_filtered = invitrospi_filtered.loc[(invitrospi_filtered['PTM'].isna()),:]
invitrospi_filtered = invitrospi_filtered.drop_duplicates(subset = ['substrateSeq', 'pepSeq'])
invitrospi_filtered = invitrospi_filtered[invitrospi_filtered["pepSeq"].apply(isCorrectSequence)]
invitrospi_filtered = invitrospi_filtered[invitrospi_filtered["substrateSeq"].apply(isCorrectSequence)]
for i in invitrospi_filtered.index:
    if invitrospi_filtered.loc[i, "pepSeq"] not in invitrospi_filtered.loc[i, "substrateSeq"]:
        invitrospi_filtered.drop(index=i,inplace=True)

invitrospi_filtered = invitrospi_filtered.loc[:, ["protIsotype", "pepSeq", "substrateSeq", "substrateOrigin"]]
invitrospi_filtered = invitrospi_filtered.rename(
    columns={"pepSeq": "fragment", "substrateSeq": "substrate", "substrateOrigin": "name"})
pepsickle_data_filtered = pepsickle_data_filtered.loc[:, ["Proteasome", "fragment", "full_sequence", "Name"]]
pepsickle_data_filtered = pepsickle_data_filtered.rename(
    columns={"full_sequence": "substrate", "Name": "name"})

train_invitro = pd.concat([invitrospi_filtered, pepsickle_data_filtered], ignore_index=True)
train_invitro = train_invitro.drop_duplicates(subset= ['fragment', 'substrate'])
train_invitro.reset_index(inplace=True,drop = True)

train_invitro.to_csv(f"{path}/total_train_{name}.csv", index = False, sep = ";")
print(f"Num substrate = {len(train_invitro.substrate.unique())}")

fiveCV = GroupKFold(n_splits=5)
for i, (train_index, test_index) in enumerate(fiveCV.split(X = train_invitro["fragment"],groups=train_invitro["substrate"])):
    print(f"Fold {i}:")

    train_fold = train_invitro.loc[train_index,:]
    test_fold = train_invitro.loc[test_index,:]

    print(f"Train {len(train_invitro.loc[train_index, 'substrate'].unique())}")
    ready_train_fold = generateSamples(train_fold, window_radius=args.window)
    print(f"Test {len(train_invitro.loc[test_index,'substrate'].unique())}")
    ready_test_fold = generateSamples(test_fold, window_radius=args.window)

    train_fold.to_csv(f"{path}/train_{name}_{args.window}_{i}.csv", index=False, sep=";")
    test_fold.to_csv(f"{path}/test_{name}_{args.window}_{i}.csv", index=False, sep=";")
    ready_train_fold.to_csv(f"{path}/train_ready_{name}_{args.window}_{i}.csv", index = False, sep = ";")
    ready_test_fold.to_csv(f"{path}/test_ready_{name}_{args.window}_{i}.csv", index = False, sep = ";")
