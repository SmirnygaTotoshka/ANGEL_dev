#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
PCPS - Proteasome Cleavage Prediction Server
https://doi.org/10.1186/s12859-020-03782-1
http://imed.med.ucm.es/Tools/pcps/

Работает на n-grams, Валидирована на собственном датасете из вирус-специфичных CD8+ эпитопов.
PCPS - only in vitro (const and immuno)

Характеристики
Immuno
    1) Sens=0.906 Spec=0.545
    2) Sens=0.903 Spec=0.407
    3) Sens=0.763 Spec=0.708
Const
    1) Sens=0.855 Spec=0.603
    2) Sens=0.874 Spec=0.534
    3) Sens=0.792 Spec=0.723
'''

import argparse
import os

import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def isCorrectSequence(sequence):
    alphabet = list("ACDEFGHIKLMNPQRSTVWY")
    seq = sequence.strip()
    for i in range(0,len(seq)):
        if seq[i] not in alphabet:
            return False
    return True


parser = argparse.ArgumentParser(description='PCPS only in vitro (const and immuno)')
parser.add_argument("-t","--type", choices=["I","C"], help="Type of proteasome: C - 20S constitutive, I - 20S immunoproteasome",default="C")
parser.add_argument("input", help="Text file with sequences, 1 per line")
parser.add_argument("output", help="Output directory. It will save 3 files")

args = parser.parse_args()
#Автоматическое выполнение на веб-сервере
driver = webdriver.Chrome(ChromeDriverManager().install())
with open(args.input, "r") as file:
    pcps = {}
    for i,seq in enumerate(file):
        if not isCorrectSequence(seq):
            print(f"Sequence at line {i+1} not correct")
        else:
            pcps[seq] = []
            for m in range(0, 3):
                print(i, m)
                query = f">{i}\n{seq}"
                driver.get('http://imed.med.ucm.es/Tools/pcps/')
                driver.find_element_by_css_selector("#txt_protein").clear()
                driver.find_element_by_css_selector("#txt_protein").send_keys(query)
                if args.type == "C":#по умолчанию там стоят модели протеасомы, нужно переключить
                    driver.find_element_by_css_selector("#task1").click()
                    driver.find_element_by_css_selector("#task2").click()
                    select_prot = Select(driver.find_element_by_css_selector('#miForm > table > tbody > tr:nth-child(1) > td > fieldset > table > tbody > tr:nth-child(1) > td:nth-child(2) > table > tbody > tr > td > select'))
                else:
                    select_prot = Select(driver.find_element_by_css_selector('#miForm > table > tbody > tr:nth-child(1) > td > fieldset > table > tbody > tr:nth-child(1) > td:nth-child(1) > table > tbody > tr > td > select'))

                select_prot.select_by_index(m)#Выбрать модель
                driver.find_element_by_css_selector("#miForm > table > tbody > tr:nth-child(5) > td > input").click()#Submit
                driver.switch_to.window(driver.window_handles[1])
                table = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, "/html/body/center[1]/table/tbody/tr/td/table"))
                    )
                res = pd.read_html(table.get_attribute('outerHTML'), header=0)[0]
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                pcps[seq].append(res)
driver.close()
results = [pd.DataFrame()]*3

for k,v in pcps.items():
    for i,m in enumerate(v):
        m["sequence"] = k
        results[i] = pd.concat([results[i], m],ignore_index=True)

for i,r in enumerate(results):
    r.to_excel(os.path.join(args.output, f"pcps_{i+1}.xlsx"),index=False)
