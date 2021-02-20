import re
from collections import defaultdict
from elasticsearch import Elasticsearch
import dill

es = Elasticsearch()


def getStopWords(stopWords):
    path = "/Users/shridatta/Documents/hw1/config/stoplist.txt"
    f = open(path, "r")
    for line in f:
        stopWords.append(line.strip())
    f.close()


# def getQuery():
#     path = "./query_desc.51-100.short.txt"
#     path_1 = "./query_desc.51-100.short.updated.txt"
#     f = open(path, "r")
#     f_1 = open(path_1, "w")
#     for line in f:
#         q = re.sub(r'\s+', ' ', line).strip()
#         q = re.sub(r'[0-9]', '', q)
#         q = re.sub(r'[^\w\s]', '', q)
#         f_1.write(q)
#         f_1.write("\n")
#     f.close()
#     f_1.close()


def getKeyWords(query):
    key = ""
    for word in query.split():
        if word not in stopWords:
            key += word + " "
    return key


def getInfo(key, docInfo):
    search_body = {
        'query': {
            'match': {
                'text': key
            }
        }
    }
    s = es.search(index="ap89_dataset", size=10000, scroll='3m', body=search_body)
    sid = s['_scroll_id']
    scroll_size = len(s['hits']['hits'])
    while scroll_size > 0:
        for doc in s['hits']['hits']:
            # doc_len: length of the document is retrieved
            # doc_len = len(doc['_source']['text'].split())
            docInfo.append(doc['_id'])

        s = es.scroll(scroll_id=sid, scroll='3m')

        sid = s['_scroll_id']
        scroll_size = len(s['hits']['hits'])


qNo = 0

queries = []
stopWords = []
TTF = []
ttf_unique = []

getStopWords(stopWords)
# getQuery()

path1 = "./query_desc.51-100.short.txt"
f1 = open(path1, "r")

for query in f1:
    term_vector = defaultdict(lambda: defaultdict(list))
    docInfo = []
    qNo += 1
    # kw = getKeyWords(query)
    for key in query.split():
        print("Term Vectors for", key, "are being processed.")
        getInfo(key, docInfo)
        for i in docInfo:
            # stemmed = es.indices.analyze(index='sf_1000', body={"analyzer": 'tags_analyzer', "text": key})
            tv = es.termvectors(index="sf_1000", id=i, fields='text', term_statistics=True)["term_vectors"]["text"][
                "terms"].get(key, {})

            if len(tv) == 0:
                continue
            else:
                term_vector[i][key].append(tv['term_freq'])
                term_vector[i][key].append(tv['doc_freq'])
                term_vector[i][key].append(tv['ttf'])

                docLength = sum(map(
                    lambda doc_length_term: doc_length_term['term_freq'],
                    es.termvectors(index='sf_1000', id=i, fields='text')['term_vectors']['text']['terms'].values()
                ))

                term_vector[i][key].append(docLength)

        print("term_vector", term_vector)
    print("Query #", qNo, "processed.")

    diFile = open("/Users/shridatta/Documents/hw1/config/tv_sf_1000/docInfo_%s.txt" % qNo, 'wb')
    dill.dump(docInfo, diFile)
    diFile.close()



