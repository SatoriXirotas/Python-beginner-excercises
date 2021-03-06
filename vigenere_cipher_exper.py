    
from math import log10
from itertools import permutations

def attack(inFile, outFile):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    shift_dict = {letter: alphabet.index(letter) for letter in alphabet}

    en_ics_lst = [0.0815, 0.0144, 0.0276, 0.0379, 0.1311, 0.0292, 0.0199, 0.0526, 0.0635, 
                  0.0013, 0.0042, 0.0339, 0.0254, 0.071, 0.08, 0.0198, 0.0012, 0.0683, 
                  0.061,  0.1047, 0.0246, 0.0092, 0.0154, 0.0017, 0.0198, 0.0008]
    en_ics = {letter: ic for letter, ic in zip(alphabet, en_ics_lst)}

    with open(inFile, 'r', encoding='utf8') as fi:
        rawtxt = ''.join(line for line in fi)
        cleantxt = ''.join([c for c in rawtxt if c.isalpha()])
    
    def getNgrams(ngramData=None, ctxt=None, getDict=None):
        ngrams_dict = ngramData if type(ngramData)==dict else {line.split()[0]: int(line.split()[1]) for line 
                                                                    in open(ngramData, 'r', encoding='utf8')}
        N = sum(ngrams_dict.values())
        if type(ngramData)==str:
            for ngram, count in ngrams_dict.items():
                ngrams_dict[ngram] = log10(float(count))/N
        if getDict:
            return ngrams_dict
        if ctxt:
            score, klength = 0, len(list(ngrams_dict.keys())[-1])
            for i in range(len(ctxt)-klength+1):
                score += ngrams_dict[ctxt[i:i+klength]] if ctxt[i:i+klength] in ngrams_dict else score + log10(0.1/N)
            return score
    
    def getKeylen(x=0):
        all_periods_ics = []
        for period in range(1, 51):
            period_sub_ics = []
            for start in range(period):
                sequence, ic_lst = cleantxt[start::period], []
                if len(sequence) < 2:
                    break
                ic_lst = [sequence.count(l) * (sequence.count(l) - 1) for l in alphabet]
                period_sub_ics.append(sum(ic_lst) / (len(sequence) * (len(sequence) - 1)))
            all_periods_ics.append(sum(period_sub_ics) / len(period_sub_ics))
        keylen_candidates = sorted([(keylen, ic) for keylen, ic in enumerate(all_periods_ics, start=1)
                                                 if ic > sum(all_periods_ics) / len(all_periods_ics)])
        return keylen_candidates[x][0]

    def getKeycipher(x=0, z=0):
        keylen, start, key_cipher = getKeylen(x), 0, []
        while start < keylen:
            init_str, avg_chi_lst = cleantxt[start::keylen], []
            for i in range(len(alphabet)):
                new_str = ''.join([(chr(ord(let) - i) if i <= shift_dict[let] 
                               else chr(ord(let) + (26 - i))) for let in init_str])
                exp_count = {l: en_ics[l] * len(new_str) for l in new_str}
                chi_lst = [((new_str.count(l) - exp_count[l]) ** 2) / exp_count[l] for l in new_str]
                avg_chi_lst.append(sum(chi_lst) / len(chi_lst))
            if z > 0:
                for z in range(z):
                    avg_chi_lst.remove(min(avg_chi_lst))
            key_cipher.append(alphabet[avg_chi_lst.index(min(avg_chi_lst))])
            start += 1
        return ''.join(key_cipher)

    def decipher_a(x=0, z=0, key_cipher=None):
        key_cipher = key_cipher.lower() or getKeycipher(x,z)
        i, nextxt = 0, []
        print(key_cipher)
        for char in rawtxt:
            if char.isalpha():
                new_ord, shift = ord(char) - shift_dict[key_cipher[i]], shift_dict[key_cipher[i]]
                char = (chr(new_ord) if new_ord >= ord('a') else chr(ord(char) + (26 - shift)))
                i =  i + 1 if i < (len(key_cipher) - 1) else 0
            nextxt.append(char)
        return ''.join(nextxt)
    
    def decipher_b():
        trigramDict = dict(getNgrams('english_trigrams.txt', getDict=True))
        for klen in range(3, 20):
            keyslst, nBest = sorted(list(trigramDict.keys())), []
            for tki in range(keyslst.index('ABC'), len(keyslst)):
                key = ''.join(keyslst[tki]) + 'A'*(klen-len(keyslst[tki]))
                pt, score = decipher_a(key_cipher=key), 0
                print(key)
                print(pt)
                for j in range(0, len(pt), klen):
                    score += getNgrams(ngramData=trigramDict, ctxt=pt[j:j+klen].upper())
                nBest.append([score,keyslst[tki]])
                nBest = sorted(nBest[:100], reverse=True)
            print(nBest, len(nBest))
    
    if len(cleantxt) > 350: 
        txt_ic, x = 0, 0
        while txt_ic < 0.0645:
            for z in range(3):
                nextxt = decipher_a(x=x, z=z)
                txt_ic_lst = [nextxt.count(c)/len(cleantxt) for c in nextxt if c.isalpha()]
                txt_ic = sum(txt_ic_lst) / len(txt_ic_lst)
                if txt_ic > 0.0645:
                    print(nextxt, '\ntext ic = {}'.format(txt_ic))
                    break
            x += 1
    else:
        decipher_b()
        
    
    with open(outFile, 'w', encoding='utf8') as fout:
        fout.write(nextxt)

attack('input1.txt', 'output.txt')
