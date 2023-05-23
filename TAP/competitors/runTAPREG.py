#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
TAPREG
https://doi.org/10.1002/prot.22535
http://imed.med.ucm.es/Tools/tapreg/
SVM prediction for TAP affinity.
'''

import argparse
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def isCorrectSequence(sequence):
    alphabet = list("ACDEFGHIKLMNPQRSTVWY")
    seq = sequence.strip()
    for i in range(0,len(seq)):
        if seq[i] not in alphabet:
            return False
    return True


parser = argparse.ArgumentParser(description='TAPREG. SVM prediction for TAP affinity.')
parser.add_argument("-t","--type", choices=["sparse","blosum"], help="Type of data",default="sparse")
parser.add_argument("input", help="Text file with sequences, 1 per line")
parser.add_argument("output", help="Output file")

args = parser.parse_args()

result_table_xpath = "/html/body/center[2]/table"
sparse_button_xpath = "/html/body/table/tbody/tr/td/table[3]/tbody/tr[3]/td[3]/table[1]/tbody/tr/td/form/table[1]/tbody/tr[6]/td/table/tbody/tr/td[2]/input[1]"
blosum_button_xpath = "/html/body/table/tbody/tr/td/table[3]/tbody/tr[3]/td[3]/table[1]/tbody/tr/td/form/table[1]/tbody/tr[6]/td/table/tbody/tr/td[2]/input[2]"
input_field_xpath = "/html/body/table/tbody/tr/td/table[3]/tbody/tr[3]/td[3]/table[1]/tbody/tr/td/form/table[1]/tbody/tr[8]/td/table/tbody/tr/th[2]/table/tbody/tr[3]/td/textarea"
type_input_xpath = "/html/body/table/tbody/tr/td/table[3]/tbody/tr[3]/td[3]/table[1]/tbody/tr/td/form/table[1]/tbody/tr[8]/td/table/tbody/tr/th[2]/table/tbody/tr[1]/td/input[3]"
submit_xpath = "/html/body/table/tbody/tr/td/table[3]/tbody/tr[3]/td[3]/table[1]/tbody/tr/td/form/table[1]/tbody/tr[11]/td/p/font/input"

driver = webdriver.Chrome(ChromeDriverManager().install())
with open(args.input, "r") as file:
    query = ""
    for i,seq in enumerate(file):
        if not isCorrectSequence(seq):
            print(f"Sequence at line {i+1} not correct")
        else:
            query += f">{i}\n{seq}"

driver.get('http://imed.med.ucm.es/Tools/tapreg/')
driver.find_element_by_xpath(input_field_xpath).send_keys(query)
if args.type == "sparse":
    driver.find_element_by_xpath(sparse_button_xpath).click()
else:
    driver.find_element_by_xpath(blosum_button_xpath).click()
driver.find_element_by_xpath(type_input_xpath).click()
driver.find_element_by_xpath(submit_xpath).click()
driver.switch_to.window(driver.window_handles[1])
table = WebDriverWait(driver, 120).until(
    EC.presence_of_element_located((By.XPATH, result_table_xpath))
)
res = pd.read_html(table.get_attribute('outerHTML'), header=0)[0]
res_tapreg = pd.read_html(table.get_attribute('outerHTML'), header=0)[0]
driver.close()
driver.switch_to.window(driver.window_handles[0])
driver.close()
print("Finish")
res_tapreg.to_excel(args.output,index = False)
