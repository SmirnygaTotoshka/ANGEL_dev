# Скрипт по подготовке обучающей выборки для модели пептид-HLA
# Работает с выгрузкой данных c IEDB и обучающей выборкой MHCflurry 2.0 (https://doi.org/10.1016/j.cels.2020.06.010).
# Данные смешанные: in vitro (mhc_bind, affinity) и in vivo (mhc_elution, mass_spec)
# Кроме всего, разбивает обучающую выборку на 5 фолдов, для 5-кратной кросс-валидации
library(vroom)
library(dplyr)
library(stringr)
library(caret)

iedb.bind = vroom("HLA/data/raw/epi_mhc_bind_human_total.csv",delim = ";", show_col_types = F) %>%
  mutate(as_char_value = if_else(as_char_value == 'Negative', 'Negative', 'Positive')) %>% 
  filter(grepl("Exact Epitope", e_region_domain_flag,fixed = T)) %>% 
  filter(!grepl("bad",as_comments,fixed = T)) %>% 
  filter(!grepl("did not",as_comments,fixed = T)) %>% 
  filter(!grepl("TAP-deficient",as_comments,fixed = T)) %>% #Необходимо исключить данные, которые получены с дефектами какого-либо звена процессинга
  filter(!grepl("predict",as_comments,fixed = T)) %>% 
  filter(!grepl("non-immunogenic",as_comments,fixed = T)) %>% 
  filter(class == "I") %>% 
  filter(grepl("^HLA-[ABC]\\*\\d{2}:\\d{2}$", chain_i_name)) %>% 
  filter(grepl("^[ACDEFGHIKLMNPQRSTVWY]+$", linear_peptide_seq)) %>% 
  select(all_of(c("as_char_value", "linear_peptide_seq", "chain_i_name"))) %>% 
  rename("allele" = "chain_i_name", "epitope" = "linear_peptide_seq", "outcome" = "as_char_value") %>% 
  mutate(sequence = epitope)


iedb.elution = vroom("HLA/data/raw/epi_mhc_elution_human_total.csv",delim = ";",col_types = cols(as_num_value = "d",
                                                                                                as_inequality = "c",
                                                                                                units = "c",
                                                                                                as_num_subjects = "i",
                                                                                                as_num_responded = "i",
                                                                                                as_response_frequency = "i",
                                                                                                e_ref_start = "i",
                                                                                                e_ref_end = "i"), show_col_types = F)%>% 
  mutate(as_char_value = if_else(as_char_value == 'Negative', 'Negative', 'Positive')) %>% 
  filter(grepl("Exact Epitope", e_region_domain_flag,fixed = T)) %>% 
  filter(!grepl("bad",as_comments,fixed = T)) %>% 
  filter(!grepl("did not",as_comments,fixed = T)) %>% 
  filter(!grepl("TAP deficient",as_comments,fixed = T)) %>% #Необходимо исключить данные, которые получены с дефектами какого-либо звена процессинга
  filter(!grepl("predict",as_comments,fixed = T)) %>% 
  filter(!grepl("ERAP1 silencing",as_comments,fixed = T)) %>% 
  filter(class == "I") %>% 
  filter(grepl("^HLA-[ABC]\\*\\d{2}:\\d{2}$", chain_i_name)) %>% 
  filter(grepl("^[ACDEFGHIKLMNPQRSTVWY]+$", linear_peptide_seq))%>% 
  select(all_of(c("as_char_value", "linear_peptide_seq", "chain_i_name"))) %>% 
  rename("allele" = "chain_i_name", "epitope" = "linear_peptide_seq", "outcome" = "as_char_value") %>% 
  mutate(sequence = epitope)

#https://help.iedb.org/hc/en-us/articles/114094152371
cutoff = read.csv("HLA/data/class_i_allelic_cutoff.csv",sep = ";")

flurry.bind = vroom("HLA/data/raw/MHCflurry.csv", delim = ",",show_col_types = FALSE) %>%
  filter(measurement_kind == 'affinity') %>% 
  filter(grepl("^HLA-[ABC]\\*\\d{2}:\\d{2}$", allele)) %>% 
  filter(grepl("^[ACDEFGHIKLMNPQRSTVWY]+$", peptide)) %>% 
  left_join(x = ., y = cutoff, by = c("allele" = "Allele")) %>% 
  mutate(affinity_cutoff = if_else(is.na(affinity_cutoff), 500, affinity_cutoff), #Если известен порог активной концентрации для аллеля, используем его, иначе обычный
         outcome = if_else((measurement_inequality == "<" | measurement_inequality == "=") & 
                                   measurement_value <= affinity_cutoff,
                                 "Positive", "Negative")) %>% 
  select(all_of(c("outcome", "peptide","allele"))) %>% 
  rename("epitope" = "peptide") %>% 
  mutate(sequence = epitope)

flurry.elution = vroom("HLA/data/raw/MHCflurry.csv", delim = ",",show_col_types = FALSE) %>%
  filter(measurement_kind == 'mass_spec') %>% 
  filter(grepl("^HLA-[ABC]\\*\\d{2}:\\d{2}$", allele)) %>% 
  filter(grepl("^[ACDEFGHIKLMNPQRSTVWY]+$", peptide))%>% 
  left_join(x = ., y = cutoff, by = c("allele" = "Allele")) %>% 
  mutate(affinity_cutoff = if_else(is.na(affinity_cutoff), 500, affinity_cutoff),
       outcome = if_else((measurement_inequality == "<" | measurement_inequality == "=") & 
                           measurement_value <= affinity_cutoff,
                         "Positive", "Negative")) %>% 
  select(all_of(c("outcome", "peptide","allele"))) %>% 
  rename("epitope" = "peptide") %>% 
  mutate(sequence = epitope)

total.train = bind_rows(iedb.bind, flurry.bind, iedb.elution, flurry.elution) %>% 
  filter(outcome == "Positive") %>% 
  distinct(epitope, allele) %>% 
  rename("activity"="allele")

vroom_write(total.train, "HLA/data/train/total_train.csv", delim = ";")

set.seed(9)

folds = createFolds(total.train$activity, k = 5, returnTrain = T)

k = 1
for (i in folds) {
  vroom_write(total.train[i,], paste0("HLA/data/train/train_HLA_",k,".csv"),delim = ";")
  vroom_write(total.train[-i,], paste0("HLA/data/train/test_HLA_",k,".csv"),delim = ";")
  k = k + 1
}