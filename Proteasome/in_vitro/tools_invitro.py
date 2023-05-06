import pandas as pd

# За активный сайт принимается остаток слева от разрезаемой связи
def generateSamples(X, excluded=None, window_radius=2):
    seqs = list(X["substrate"].unique())
    for i in X.index:
        finded_start = X.loc[i, "substrate"].find(X.loc[i, "fragment"])
        X.loc[i, "start"] = finded_start - 1  # сайт левее найденной позиции (левее N-конца)
        X.loc[i, "end"] = finded_start + len(X.loc[i, "fragment"]) - 1  # сайт левее найденной позиции (C-конец)
    result = pd.DataFrame(columns=["peptide", "sequence","full_sequence", "activity"])
    k = 0
    for s in seqs:
        subset = X.query("substrate == @s").reset_index(drop=True)
        possible_start = 0 + window_radius
        possible_end = len(s) - window_radius  # не включая эту позицию [start;end)
        start = list(subset['start'])
        end = list(subset['end'])
        for i in range(possible_start, possible_end):
            if excluded is not None:
                ex = subset.loc[0, excluded].split(";")
                if i in ex:
                    continue
            peptide = s[(i - window_radius):(i + window_radius + 1)]
            activity = int(i in start or i in end)
            result.loc[k] = [peptide, peptide, s, activity]
            k += 1
    print(result.activity.value_counts())
    return result

def isCorrectSequence(sequence):
    alphabet = list("ACDEFGHIKLMNPQRSTVWY")
    seq = sequence.strip()
    for i in range(0,len(seq)):
        if seq[i] not in alphabet:
            return False
    return True