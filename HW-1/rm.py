import math
import re
from operator import itemgetter
import dill
from elasticsearch import Elasticsearch

es = Elasticsearch()
# Vocabulary Size
request = {
    "aggs": {
        "vocabSize": {
            "cardinality": {
                "field": "text"
            }
        }
    },
    "size": 0
}
V = es.search(index="sf_1000", body=request)['aggregations']['vocabSize']['value']
print("vocabSize: ", V)


def getStopWords(stopWords):
    path = "/Users/shridatta/Documents/hw1/config/stoplist.txt"
    f = open(path, "r")
    for line in f:
        stopWords.append(line.strip())
    f.close()


def getQueryNumber(qNo, lines):
    f = open("/Users/shridatta/Documents/hw1/config/query_desc.51-100.short.txt", "r")
    for line in f:
        q = line.split()[0].strip()
        qNo.append(re.sub(r'[^\w\s]', '', q))
        l = re.sub(r'[0-9]', '', line)
        lines.append(l)


def getQueryTermFreq(key, query_no):
    count = 0
    l = ""
    f = open("/Users/shridatta/Documents/hw1/config/query_desc.51-100.short.txt", "r")
    for line in f:
        q = line.split()[0].strip()
        q = re.sub(r'[^\w\s]', '', q)
        # print("Q:",q)
        if q == query_no:
            l = line
            break
    for word in l.split():
        if word == key:
            count += 1
    return count


def es_builtin(query_no, line):
    print("Processing for query #", query_no)
    print("The query is: ", line)
    scores = []
    search_body = {
        'query': {
            'match': {
                'text': line
            }
        }
    }
    s = es.search(index="ap89_dataset", size=10000, scroll='3m', body=search_body)
    sid = s['_scroll_id']
    scroll_size = len(s['hits']['hits'])
    while scroll_size > 0:
        for score in s['hits']['hits']:
            scores.append([score["_id"], score["_score"]])

        s = es.scroll(scroll_id=sid, scroll='3m')

        sid = s['_scroll_id']
        scroll_size = len(s['hits']['hits'])

    scores.sort(key=itemgetter(1), reverse=True)
    f = open("./esbuiltin.txt", "a+")
    rank = 1
    for s in scores:
        f.write('%d Q0 %s %d %lf Exp\n' % (int(query_no), s[0], rank, s[1]))  # Writing the results to the array.
        rank += 1
    f.close()


def okapi_tf(query_no):
    print("PRocessing OKAPI for query #", query_no)
    okapi_score = []
    for docid in termVectors:
        okapi = 0
        for key in termVectors[docid]:
            tfwd = termVectors[docid][key][0]  # Term Frequency in document.
            doc_len = termVectors[docid][key][3]  # Length of the document.
            # Main Calculation
            okapi += (tfwd / (tfwd + 0.5 + (1.5 * (doc_len / avgLen))))
        okapi_score.append([docid, okapi])  # Appending the scores to the array.
    okapi_score.sort(key=itemgetter(1), reverse=True)  # Sorting the array by score.
    f = open("./okapiTF.txt", "a+")
    rank = 1
    for s in okapi_score:
        f.write('%d Q0 %s %d %lf Exp\n' % (int(num), s[0], rank, s[1]))  # Writing the results to the array.
        rank += 1
    f.close()


def tf_idf(query_no):
    print("Processing TF-IDF for query #", query_no)
    tfidf_score = []
    words = []
    for docid in termVectors:
        tfidf = 0
        for key in termVectors[docid]:
            words.append(key)
            tfwd = termVectors[docid][key][0]  # Term Frequency in document d.
            doc_freq = termVectors[docid][key][1]  # Document Frequency - number of docs that contain the key.
            doc_len = termVectors[docid][key][3]  # Length of the document.
            # Main Calculation
            okapi_part = (tfwd / (tfwd + 0.5 + (1.5 * (doc_len / avgLen))))
            tfidf += okapi_part * (math.log10(84678 / doc_freq))
        tfidf_score.append([docid, tfidf])  # Appending the scores to the array.
    tfidf_score.sort(key=itemgetter(1), reverse=True)  # Sorting the array by score.

    print(words)
    f = open("./TFIDF.txt", "a+")
    rank = 1
    for s in tfidf_score:
        f.write('%d Q0 %s %d %lf Exp\n' % (int(query_no), s[0], rank, s[1]))  # Writing the results to the array.
        rank += 1
    f.close()


def okapi_bm25(query_no):
    print("Processing BM25 for query #", query_no)
    k1, k2 = 1.2, 100  # 0.2
    b = 0.25
    bm25_score = []
    for doc_id in termVectors:
        bm = 0
        for key in termVectors[doc_id]:
            tfwd = termVectors[doc_id][key][0]
            tfwq = getQueryTermFreq(key, query_no)
            doc_freq = termVectors[doc_id][key][1]
            doc_len = termVectors[doc_id][key][3]
            bm += ((math.log10((84678 + 0.5) / (doc_freq + 0.5))) * (
                    (tfwd + (tfwd * k1)) / (tfwd + k1 * ((1 - b) + b * (doc_len / avgLen)))) * (
                           (tfwq + k2 * tfwq) / (tfwq + k2)))
        bm25_score.append([doc_id, bm])

    bm25_score.sort(key=itemgetter(1), reverse=True)
    f = open("./bm25.txt", "a+")
    rank = 1
    for s in bm25_score:
        f.write('%d Q0 %s %d %lf Exp\n' % (int(num), s[0], rank, s[1]))
        rank += 1
    f.close()


def unigram_laplace(query_no):
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
                doc_len = termVectors[docid][word][3]
                score = (tfwd + 1) / (doc_len + V)
            else:
                score = 1 / (avgLen + V)
            if docid not in docScore:
                docScore[docid] = 0.0
            docScore[docid] += math.log(score)
    for docid in docScore.keys():
        laplace_score.append((docid, docScore[docid]))
    laplace_score.sort(key=itemgetter(1), reverse=True)

    f = open('./laplace_r.txt', 'a+')
    rank = 1
    for ls in laplace_score:
        f.write('%s Q0 %s %d %f Exp\n' % (query_no, ls[0], rank, ls[1]))
        rank += 1
    f.close()


def unigram_jelinek_mercer(query_no):
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
                ttf = termVectors[doc_id][word][2]
                doc_len = termVectors[doc_id][word][3]
                score = float(lambdaa * (tfwd / doc_len)) + float((1 - lambdaa) * ((ttf - tfwd) / (avg_doc_len['sum_ttf'] - doc_len)))
            else:
                for i in TTF:
                    if word in i:
                        ttf = i[1]
                        break
                score = ((1 - lambdaa) * (ttf / avg_doc_len['sum_ttf']))
            if doc_id not in docScore:
                docScore[doc_id] = 0.0
            docScore[doc_id] += score
    for docid in docScore.keys():
        jm_score.append((docid, docScore[docid]))
    jm_score.sort(key=itemgetter(1), reverse=True)

    f = open('./jm.txt', 'a+')
    rank = 1
    for ls in jm_score:
        f.write('%s Q0 %s %d %f Exp\n' % (query_no, ls[0], rank, ls[1]))
        rank += 1
    f.close()


count = 0

qNo = []
sw = []
lines = []
TTF = []
ttf_unique = []
getStopWords(sw)
getQueryNumber(qNo, lines)


for num in qNo:
    es_builtin(num, lines[count])
    
    count += 1

    f = open("./tv_%s.txt" % count, 'rb')
    termVectors = dill.load(f)
    f.close()

    # for docid in termVectors:
    #     for key in termVectors[docid]:
    #         TTF.append([key, termVectors[docid][key][2]])
    # for t in TTF:
    #     if t not in ttf_unique:
    #         ttf_unique.append(t)

    f = open("./ttf.txt", "rb")
    TTF = dill.load(f)
    # dill.dump(ttf_unique, f)
    f.close()


    for doc_id in termVectors:
        avg_doc_len = es.termvectors(index='sf_1000', id=doc_id, fields='text')['term_vectors']['text'][
            'field_statistics']
        avgLen = avg_doc_len['sum_ttf'] / avg_doc_len['doc_count']
        break

    okapi_tf(num)
    tf_idf(num)
    okapi_bm25(num)
    unigram_laplace(num)
    unigram_jelinek_mercer(num)

