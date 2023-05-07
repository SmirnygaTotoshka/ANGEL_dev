#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
NetChop 3.1 -  neural network
https://services.healthtech.dtu.dk/services/NetChop-3.1/
https://doi.org/10.1007/s00251-005-0781-7

NetChop доступна только для in vitro const и in vivo данных
'''
import argparse
import re
import time
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

def parseTable(lines):
    result = pd.DataFrame(columns=["a"] * 5)
    body = False
    k = 0
    for line in lines:
        elements = re.split("\\s+", line.strip())
        if len(elements) == 5 and not body:
            body = True
            result = result.set_axis(labels=elements, axis=1)
            continue
        if len(elements) == 5 and body:
            result.loc[k] = elements
            k += 1
    return result

parser = argparse.ArgumentParser(description='NetChop only in vitro constitutive and in vivo data')
parser.add_argument("-t","--type", choices=["vitro","vivo"], help="Type of data",default="vitro")
parser.add_argument("input", help="Text file with sequences, 1 per line")
parser.add_argument("output", help="Output file")

args = parser.parse_args()

cookie_button = "/html/body/div[5]/div[4]/div[3]"
input_field_xpath = "/html/body/div[3]/main/div/div[3]/div/div[2]/div[1]/form/p[1]/textarea"
method_xpath = "/html/body/div[3]/main/div/div[3]/div/div[2]/div[1]/form/p[3]/select"
submit_xpath = "/html/body/div[3]/main/div/div[3]/div/div[2]/div[1]/form/p[6]/input[1]"

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get('https://services.healthtech.dtu.dk/services/NetChop-3.1/')
cookie_button_accept = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.XPATH, cookie_button))
)
cookie_button_accept.click()

with open(args.input, "r") as file:
    res_netchop = pd.DataFrame()
    for i,seq in enumerate(file):
        if not isCorrectSequence(seq):
            print(f"Sequence at line {i+1} not correct")
        else:
            query = f">{i}\n{seq}"
            driver.get('https://services.healthtech.dtu.dk/services/NetChop-3.1/')
            driver.find_element_by_xpath(input_field_xpath).send_keys(query)
            select_prot = Select(driver.find_element_by_xpath(method_xpath))
            if args.type == "vitro":
                select_prot.select_by_index(1)
            else:
                select_prot.select_by_index(1)#dont delete - it removes elements interception
                select_prot.select_by_index(0)
            time.sleep(2)#dont delete - it removes elements interception
            submit_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, submit_xpath))
            )
            submit_button.click()
            table = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/pre"))
            )
            lines = table.get_attribute('outerHTML').split("\n")
            tmp = parseTable(lines)
            tmp["sequence"] = seq
            res_netchop = pd.concat([res_netchop, tmp])
            print(i, "Finish")
driver.close()
res_netchop.to_excel(args.output,index = False)

