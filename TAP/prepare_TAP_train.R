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
  rename("log_IC50_rel" = "log(IC50_relative)")%>%
  mutate(activity = if_else(log_IC50_rel > (log(100)), 0, 1))

write.csv2(first, "TAP/data/train/total_train_TAP.csv",row.names = F)

set.seed(9)
folds = createFolds(first$activity, k = 5, returnTrain = T)
k = 1
for (i in folds) {
  write.csv2(first[i,], paste0("TAP/data/train/train_TAP_",k,".csv"),row.names = F)
  write.csv2(first[-i,], paste0("TAP/data/train/test_TAP_",k,".csv"),row.names = F)
  k = k + 1
}

print("TAP train activiies:")
print(table(first$activity))