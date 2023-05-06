#Data source
#TAPREG - 10.1002/prot.22535 - supplementary
library(dplyr)
library(readxl)
library(caret)

#TAPREG supplementary
# 1 - 10.4049/jimmunol.161.2.617 + 10.1186/1745-7580-1-4
# 2 - 5 613-peptide dataset using the purge utility of the Gibbs Sampler (10.1002/pro.5560040820) 
# with an exhaustive method and maximum blosum 62 relatedness scores of 25, 30, 35, and 37.

#let tapreg log(IC50_relative) as is pIC50_relative in mhc bn 
first = read_excel("TAP/data/raw/TAPREG/prot_22535_sm_supptable1.xls") %>%
  rename("log_IC50_rel" = "log(IC50_relative)")

second = read_excel("TAP/data/raw/TAPREG/prot_22535_sm_supptable2.xls") %>%
  rename("log_IC50_rel" = "log(IC50_relative)")

third = read_excel("TAP/data/raw/TAPREG/prot_22535_sm_supptable3.xls") %>%
  rename("log_IC50_rel" = "log(IC50_relative)")

fourth = read_excel("TAP/data/raw/TAPREG/prot_22535_sm_supptable4.xls") %>%
  rename("log_IC50_rel" = "log(IC50_relative)")

fifth = read_excel("TAP/data/raw/TAPREG/prot_22535_sm_supptable5.xls") %>%
  rename("log_IC50_rel" = "log(IC50_relative)")

total = bind_rows(first,second,third,fourth,fifth) %>% 
  group_by(PEPTIDE) %>% 
  summarise(median_log10_IC50_rel = median(log_IC50_rel)) %>% 
  mutate(activity = if_else(median_log10_IC50_rel > (log10(800)), 0, 1))

write.csv2(total, "TAP/data/train/total_train_TAP.csv",row.names = F)

set.seed(9)
folds = createFolds(total$activity, k = 5, returnTrain = T)
k = 1
for (i in folds) {
  write.csv2(total[i,], paste0("TAP/data/train/train_TAP_",k,".csv"),row.names = F)
  write.csv2(total[-i,], paste0("TAP/data/train/test_TAP_",k,".csv"),row.names = F)
  k = k + 1
}

print("TAP train activiies:")
print(table(total$activity))