#1) MHC BN - 10.1186/1756-0500-2-61 parsed by python mhcbnRawDownload.py
library(dplyr)
library(vroom)
library(stringr)

#MHC BN
mhcbn = vroom("TAP/data/raw/MHCBN_2023-05-08.tsv", delim = "\t") %>%
  select(-1) %>%
  filter(`MHC Allele` == "TAP") %>%
  filter(`Host Organism` == "HUMAN") %>%
  filter(!is.na(Comment)) %>%
  filter(grepl("Relative", Comment)) %>%
  filter(!grepl("approx", Comment)) %>%
  filter(grepl("nM|uM",Comment,ignore.case = T)) %>%
  filter(`Experimental Method` != '?') %>%
  mutate(unit = str_extract(Comment,"\\(([^)]+)\\)",group = T),
         value = if_else(grepl("u",unit),
                         sapply(str_split(Comment,"="),function(x){as.double(x[2])}) * 1000,
                         sapply(str_split(Comment,"="),function(x){as.double(x[2])}))) %>%
  filter(!is.na(value)) %>%
#  mutate(log_IC50_rel = log10(value)) %>%
#  select(all_of(c("Peptide Sequence", "log_IC50_rel"))) %>%
  select(all_of(c("Peptide Sequence", "value"))) %>%
  rename("PEPTIDE" = "Peptide Sequence")

total = read.csv2("TAP/data/train/total_train_TAP.csv")

validation = mhcbn[!(mhcbn$PEPTIDE %in% total$PEPTIDE),] %>%
  group_by(PEPTIDE) %>%
#  summarise(median_log10_IC50_rel = median(log_IC50_rel)) %>%)
#  mutate(activity = if_else(median_log10_IC50_rel > log10(800), 0, 1))
  summarise(median_IC50_rel = median(value)) %>%
  mutate(activity = if_else(median_IC50_rel > 100,0,1))
write.csv2(validation, "TAP/data/validation/validation_TAP.csv", row.names = F)

print("TAP validation activiies:")
print(table(validation$activity))