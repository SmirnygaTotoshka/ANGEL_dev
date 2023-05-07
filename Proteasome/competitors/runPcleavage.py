#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Pcleavage
https://doi.org/10.1093/nar/gki587
https://webs.iiitd.edu.in/raghava/pcleavage/

SVM one hot encoding, Валидирована на данных Saxova, P., Buus, S., Brunak, S., Kesmir, C. 2003 Predicting proteasomal cleavage sites: a comparison of available methods Int. Immunol. 15 781 –78

Осторожно вывод варьирует как минимум от -1,5 до 1,5
Pcleavage доступна только для in vitro const и in vivo данных
'''

import argparse

import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

def isCorrectSequence(sequence):
    alphabet = list("ACDEFGHIKLMNPQRSTVWY")
    seq = sequence.strip()
    for i in range(0,len(seq)):
        if seq[i] not in alphabet:
            return False
    return True


parser = argparse.ArgumentParser(description='Pcleavage only in vitro constitutive and in vivo data')
parser.add_argument("-t","--type", choices=["vitro","vivo"], help="Type of data",default="vitro")
parser.add_argument("input", help="Text file with sequences, 1 per line")
parser.add_argument("output", help="Output file")

args = parser.parse_args()
#Автоматическое выполнение на веб-сервере
result_table_xpath = "/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[4]/td/table/tbody/tr/td/pre/table[2]/tbody/tr[2]/td/center/table"
invitro_button_xpath = "/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[4]/td/table/tbody/tr/td/form/p[3]/table/tbody/tr[1]/td[1]/input"
invivo_button_xpath = "/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[4]/td/table/tbody/tr/td/form/p[3]/table/tbody/tr[2]/td[1]/input"
input_field_xpath = "/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[4]/td/table/tbody/tr/td/form/p[1]/textarea"
submit_xpath = "/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[4]/td/table/tbody/tr/td/form/input[4]"

driver = webdriver.Chrome(ChromeDriverManager().install())
with open(args.input, "r") as file:
    res_pcleavage = pd.DataFrame()
    for i,seq in enumerate(file):
        if not isCorrectSequence(seq):
            print(f"Sequence at line {i+1} not correct")
        else:
            driver.get('https://webs.iiitd.edu.in/raghava/pcleavage/')
            driver.find_element_by_xpath(input_field_xpath).send_keys(seq)
            if args.type == "vitro":
                driver.find_element_by_xpath(invitro_button_xpath).click()
            else:
                driver.find_element_by_xpath(invivo_button_xpath).click()
            driver.find_element_by_xpath(submit_xpath).click()
            tmp = pd.read_html(driver.find_element_by_xpath(result_table_xpath).get_attribute('outerHTML'), header = 0)[0]
            tmp["sequence"] = seq
            res_pcleavage = pd.concat([res_pcleavage, tmp])
            print(i, "Finish")
driver.close()
res_pcleavage.dropna(subset=["Position",'Amino Acid',"Score"],inplace=True)
res_pcleavage.to_excel(args.output,index = False)
