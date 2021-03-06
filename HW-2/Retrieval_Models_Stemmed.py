import linecache
import math
from collections import defaultdict
from operator import itemgetter
from stemming.porter2 import stem
import dill


def getKeyWords(l):
    keys = []
    for word in l.split():
        if word.strip() not in stop_words:
            keys.append(stem(word.lower().strip()))
    return keys


def getCatalog(merge_catalog):
    c_path = "./Stemmed_CatalogFiles_wo-dfttf/main_catalog_stemmed.txt"
    c = open(c_path, 'r')
    for c_line in c:
        merge_catalog.append(c_line.split()[0])
    c.close()
    # print(len(merge_catalog))


def getStopWords(stop_words):
    sw_path = "./stoplist.txt"
    sw = open(sw_path, "r")
    for sw_line in sw:
        stop_words.append(sw_line.strip())
    sw.close()


def calc_avg_doc_len():
    len = 0
    for ids in doc_len_info.keys():
        len += doc_len_info[ids]
    return len/84678


def get_TTF(term):
    for ids in query_data:
        if term == query_data[ids]:
            return query_data[ids][term][3]


def okapiTF(data, query_no):
    print("PRocessing OKAPI for query #", query_no)
    okapi_score = []
    for ids in data:
        okapi = 0
        for term in data[ids]:
            tfwd = data[ids][term][1]  # Term Frequency in document.
            doc_len = data[ids][term][2]  # Length of the document.
            # Main Calculation
            okapi += (tfwd / (tfwd + 0.5 + (1.5 * (doc_len / avgLen))))
        okapi_score.append([ids, okapi])  # Appending the scores to the array.
    okapi_score.sort(key=itemgetter(1), reverse=True)  # Sorting the array by score.
    f = open("./okapiTF_stemmed.txt", "a+")
    rank = 1
    for s in okapi_score:
        f.write('%d Q0 %s %d %lf Exp\n' % (int(query_no), s[0], rank, s[1]))  # Writing the results to the array.
        if rank == 1000:
            break
        rank += 1
    f.close()


def tf_idf(termVectors, query_no):
    print("Processing TF-IDF for query #", query_no)
    tfidf_score = []
    # words = []
    for docid in termVectors:
        tfidf = 0
        for key in termVectors[docid]:
            # words.append(key)
            tfwd = termVectors[docid][key][0]  # Term Frequency in document d.
            doc_freq = termVectors[docid][key][1]  # Document Frequency - number of docs that contain the key.
            doc_len = termVectors[docid][key][2]  # Length of the document.
            # Main Calculation
            okapi_part = tfwd / (tfwd + 0.5 + 1.5 * (doc_len / avgLen))
            tfidf += okapi_part * math.log10(84678 / doc_freq)
        tfidf_score.append([docid, tfidf])  # Appending the scores to the array.
    tfidf_score.sort(key=itemgetter(1), reverse=True)  # Sorting the array by score.

    # print(words)
    f = open("./TFIDF_stemmed.txt", "a+")
    rank = 1
    for s in tfidf_score:
        f.write('%d Q0 %s %d %lf Exp\n' % (int(query_no), s[0], rank, s[1]))  # Writing the results to the array.
        if rank == 1000:
            break
        rank += 1
    f.close()


def okapi_bm25(termVectors, query_no):
    print("Processing BM25 for query #", query_no)
    k1, k2 = 1.2, 100  # 0.2
    b = 0.25
    bm25_score = []
    for doc_id in termVectors:
        bm = 0
        for key in termVectors[doc_id]:
            tfwd = termVectors[doc_id][key][0]
            tfwq = 1  # getQueryTermFreq(key, query_no)
            doc_freq = termVectors[doc_id][key][1]
            doc_len = termVectors[doc_id][key][2]
            bm += ((math.log10((84678 + 0.5) / (doc_freq + 0.5))) * (
                    (tfwd + (tfwd * k1)) / (tfwd + k1 * ((1 - b) + b * (doc_len / avgLen)))) * (
                           (tfwq + k2 * tfwq) / (tfwq + k2)))
        bm25_score.append([doc_id, bm])

    bm25_score.sort(key=itemgetter(1), reverse=True)
    f = open("./bm25_stemmed.txt", "a+")
    rank = 1
    for s in bm25_score:
        f.write('%d Q0 %s %d %lf Exp\n' % (int(query_no), s[0], rank, s[1]))
        if rank == 1000:
            break
        rank += 1
    f.close()


def unigram_laplace(termVectors, query_no):
    print("Processing Unigram Laplace for Query #", query_no)
    keys = []
    for doc_id in termVectors:
        for key in termVectors[doc_id]:
            keys.append(key)
    keys = list(set(keys))

    docScore = {}
    laplace_score = []
    for word in keys:
        for docid in termVectors:
            if word in termVectors[docid]:
                tfwd = termVectors[docid][word][0]
                doc_len = termVectors[docid][word][2]
                score = (tfwd + 1) / (doc_len + V)
            else:
                score = 1 / (avgLen + V)
            if docid not in docScore:
                docScore[docid] = 0.0
            docScore[docid] += math.log(score)
    for docid in docScore.keys():
        laplace_score.append((docid, docScore[docid]))
    laplace_score.sort(key=itemgetter(1), reverse=True)

    f = open('./laplace_stemmed.txt', 'a+')
    rank = 1
    for ls in laplace_score:
        f.write('%s Q0 %s %d %f Exp\n' % (int(query_no), ls[0], rank, ls[1]))
        if rank == 1000:
            break
        rank += 1
    f.close()


def unigram_jelinek_mercer(termVectors, query_no):
    print("Processing Unigram Jelinek-Mercer for Query #", query_no)
    keys = []
    for doc_id in termVectors:
        for key in termVectors[doc_id]:
            keys.append(key)
    keys = list(set(keys))

    lambdaa = 0.75
    docScore = {}
    jm_score = []
    for word in keys:
        for doc_id in termVectors:
            if word in termVectors[doc_id]:
                tfwd = termVectors[doc_id][word][0]
                ttf = termVectors[doc_id][word][3]
                doc_len = termVectors[doc_id][word][2]
                score = float(lambdaa * (tfwd / doc_len)) + float((1 - lambdaa) * ((ttf - tfwd) / (V - doc_len)))
            else:
                score = ((1 - lambdaa) * (ttf_dict[word] / V))
            if doc_id not in docScore:
                docScore[doc_id] = 0.0
            docScore[doc_id] += score
    for docid in docScore.keys():
        jm_score.append((docid, docScore[docid]))
    jm_score.sort(key=itemgetter(1), reverse=True)

    f = open('./jm_stemmed.txt', 'a+')
    rank = 1
    for ls in jm_score:
        f.write('%s Q0 %s %d %f Exp\n' % (query_no, ls[0], rank, ls[1]))
        if rank == 1000:
            break
        rank += 1
    f.close()


stop_words = []
getStopWords(stop_words)

merge_catalog = []
getCatalog(merge_catalog)
V = len(merge_catalog)

inv_path = "./Stemmed_InvFiles_wo-dfttf/main_inv_stemmed.txt"
q_path = "/Users/shridatta/Downloads/Info Retrieval - CS6200/hw1/config/Query Files/query_desc.51-100.short.txt"

d_path = "./doc_len_stemmed.txt"
d_file = open(d_path, 'rb')
doc_len_info = dill.load(d_file)
d_file.close()
avgLen = calc_avg_doc_len()

d_id_path = "./doc_dict.txt"
d_id_file = open(d_id_path, 'rb')
doc_id_info = dill.load(d_id_file)
d_id_file.close()

ttf_dict = {}
q = open(q_path, 'r')
queryNo = 0
for line in q:
    i = line.split('.')
    i[1] = i[1].strip()
    q_num = i[0]
    query_data = defaultdict(lambda: defaultdict(list))

    key_words = getKeyWords(i[1])
    # print(key_words)
    for word in key_words:
        if word in merge_catalog:
            ttf = 0
            word_index = merge_catalog.index(word)
            word_data = linecache.getline(inv_path, word_index + 1).rstrip('\n')
            for item in word_data.split(";"):
                items = item.strip().split(",")
                items[1] = items[1].split(' ')
                ttf += len(items[1])
                query_data[doc_id_info[int(items[0])]][word].append(len(items[1]))
                query_data[doc_id_info[int(items[0])]][word].append(len(word_data.split(";")))
                query_data[doc_id_info[int(items[0])]][word].append(doc_len_info[int(items[0])])
            for item in word_data.split(";"):
                items = item.strip().split(",")
                ttf_dict[word] = ttf
                query_data[doc_id_info[int(items[0])]][word].append(ttf)
    # print(query_data)
    # print("processing query")

    # okapiTF(query_data, q_num)
    # tf_idf(query_data, q_num)
    # okapi_bm25(query_data, q_num)
    # unigram_laplace(query_data, q_num)
    # unigram_jelinek_mercer(query_data, q_num)
q.close()
