#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import argparse
from toolsInvivo import getSamplesMulti, isCorrectSequence

parser = argparse.ArgumentParser()
parser.add_argument("-w","--window", type=int, choices=range(2,6), help="Window`s radius",default=2)
args = parser.parse_args()

'''
Валидационная выборка состоит из двух датасетов
1) 10.1038/ncomms13404 - данные взяты из статьи pepsickle - supplementary - неоэпитопы и раковые эпитопы
2) https://doi.org/10.1186/s12859-020-03782-1 supplementary - вирус-специфичные
'''

cancer_epitopes = pd.read_excel("Proteasome/data/raw/pepsickle_validation_invivo.xlsx")


