library(dplyr)
library(stringr)
library(vroom)

multiallelic = vroom("HLA/data/raw/MULTIALLELIC.csv",delim = ',')
total.train = vroom("HLA/data/train/total_train_HLA.csv", delim = ";")
hits = multiallelic %>%
  filter(hit == 1) %>%
  filter(!(peptide %in% total.train$epitope)) %>%
  filter(grepl("^[ACDEFGHIKLMNPQRSTVWY]+$", peptide))


total_hla = parallel::mclapply(hits$hla,function(x){
  stringr::str_split(x, "\\s+")
  }, mc.cores = 10)

total_hla = unique(unlist(total_hla))
columns = c("peptide","activity")
for (a in total_hla){
  set.seed(9)
  if (str_detect(a,"^HLA-[ABC]\\*\\d{2}:\\d{2}$")){
    allele_sub = hits %>% mutate(activity = as.integer(grepl(a,hla, fixed = T)))
    sample_size = min(table(allele_sub$activity))
    positive = allele_sub %>% filter(activity == 1) %>% slice_sample(n = sample_size)
    negative = allele_sub %>% filter(activity == 0) %>% slice_sample(n = sample_size)
    all = bind_rows(positive,negative) %>% select(all_of(columns)) %>% distinct(peptide,.keep_all = T)
    write.csv2(all, paste0("HLA/data/validation/",str_remove_all(a,"\\*|:"),".csv"),row.names = F)
  }
  else{
    print(a)
  }
}
