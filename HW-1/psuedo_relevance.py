import math
from operator import itemgetter
import re
import dill
from elasticsearch import Elasticsearch

es = Elasticsearch()

avg_doc_len = es.termvectors(index='sf_1000', id='AP891108-0170', fields='text')['term_vectors']['text'][
    'field_statistics']
avgLen = avg_doc_len['sum_ttf'] / avg_doc_len['doc_count']


def get_k_docs(k, qno):
    f = open("./results_sf_1000/okapi_tf.txt", "r")
    docs = []
    count = 0
    i = 0
    for line in f:
        q = line.split()[0]
        if q == qno:
            docs.append(line.split()[2])
            count += 1
            if count == k:
                break
    return docs


def result(line):
    l = ""
    path_2 = "./query_desc.51-100.short.txt."
    f_2 = open(path_2, "a+")
    for word in line.split():
        sig = []
        if word not in sw:
            print("SIG TERMS FOR:", word)
            sig_body = {
                "query": {
                    "match": {"text": word}
                },
                "aggregations": {
                    "keywords": {
                        "significant_terms": {"field": "text", "size": 10}
                    }
                }
            }
            sig_terms = es.search(index="sf_1000", body=sig_body)
            print("LEN:",len(sig_terms))
            if len(sig_terms) > 0:
                for i in range(len(sig_terms)):
                    w = sig_terms["aggregations"]["keywords"]["buckets"][i]["key"]
                    s = (sig_terms["aggregations"]["keywords"]["buckets"][i]["score"])
                    sig.append([w, s])
                sig.sort(key=itemgetter(1), reverse=True)
                for i in range(1,4):
                    l += " " + sig[i][0]
                print(l)
                f_2.write(str(l))
                f_2.write("\n")
                # f_2.close()


def getStopWords(stopWords):
    path = "/Users/shridatta/Documents/hw1/config/stoplist.txt"
    f = open(path, "r")
    for line in f:
        stopWords.append(line.strip())
    f.close()


sw = []
getStopWords(sw)
file = open("./query_desc.51-100.short.txt", "r")
for line in file:
    qno = line.split()[0].strip()
    print("PROcessing for query #", qno)
    doc_ids = get_k_docs(10, qno)
    l = re.sub(r'[0-9]', '', line)
    result(l)
