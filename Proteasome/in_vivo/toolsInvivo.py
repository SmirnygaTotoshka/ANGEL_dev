from multiprocessing import Pool

import pandas as pd
import numpy as np

def isCorrectSequence(sequence):
    alphabet = list("ACDEFGHIKLMNPQRSTVWY")
    seq = sequence.strip()
    for i in range(0,len(seq)):
        if seq[i] not in alphabet:
            return False
    return True

#%%
def generateSamplesOnlyC(X, window_radius = 2):
	result = pd.DataFrame(columns=["peptide","sequence","activity"])
	k = 0
	for i in X.index:
		np.random.seed(9)
		end = X.loc[i,"sequence"].find(X.loc[i, "linear_peptide_seq"]) + len(X.loc[i, "linear_peptide_seq"])-1
		end = int(end)#сайт левее найденной позиции
		if end+window_radius+1 > len(X.loc[i,"sequence"]):
			continue
		#positive
		peptide = X.loc[i,"sequence"][(end-window_radius):(end+window_radius+1)]
		if len(peptide) == 2 * window_radius + 1:
			result.loc[k] = [peptide, peptide, 1]
			k += 1
		else:
			continue
		#negative
		possible = list(range(X.loc[i,"sequence"].find(X.loc[i, "linear_peptide_seq"]), end - window_radius))
		random_site = np.random.choice(possible,1)[0]
		peptide = X.loc[i,"sequence"][(random_site-window_radius):(random_site+window_radius+1)]
		if len(peptide) == 2 * window_radius + 1:
			result.loc[k] = [peptide, peptide, 0]
			k += 1
		else:
			continue
	print(result.activity.value_counts())
	return result

def getSamplesMulti(X,number_threads = 5, w = 2):
	total = len(X.index)
	size_part = total // number_threads
	size_last_part = size_part + (total - size_part * number_threads)
	            # procs - количество ядер
	            # calc - количество операций на ядро
	partitions = []
	            # делим вычисления на количество ядер
	for proc, start in zip(range(number_threads), range(0, total, size_part)):
	    if proc == number_threads - 1:
	        partition = X[start:start + size_last_part]
	    else:
	        partition = X[start:start + size_part]
	    partitions.append(partition)

	with Pool(number_threads) as p:
	    results = p.starmap(generateSamplesOnlyC, zip(partitions, [w]*len(partitions)))
	return pd.concat(results, ignore_index = True)
