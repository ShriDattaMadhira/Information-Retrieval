import os
from elasticsearch import Elasticsearch

es = Elasticsearch()

def getStopWords(stopWords):
    path = "/Users/shridatta/Documents/hw1/config/stoplist.txt"
    f = open(path, "r")
    for line in f:
        stopWords.append(line.strip())
    f.close()


stopWords = []
getStopWords(stopWords)

request_body = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1,
        "analysis": {
            "filter": {
                "english_stop": {
                    "type": "stop",
                    "stopwords": stopWords
                },
                "my_stemmer": {
                    "type": "stemmer",
                    "language": "english"
                }
            },
            "analyzer": {
                "tags_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "english_stop", "my_stemmer"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "text": {
                "type": "text",
                "fielddata": True,
                "analyzer": "tags_analyzer",
                "index_options": "positions"
            }
        }
    }
}
response = es.indices.create(index="sf_1000", body=request_body)

path = "/Users/shridatta/Documents/hw1/config/ap89_collection/"
for file in os.listdir(path):
    if file != 'readme':
        f = open(path + file).read()
        while "<DOC>" in f:
            # print("In while <DOC>")
            doc_end = f.find('</DOC>')
            sub = f[:doc_end]
            doc_no_s = sub.find('<DOCNO>') + len("<DOCNO>")
            doc_no_e = sub.find('</DOCNO>')
            doc_no = sub[doc_no_s:doc_no_e].strip()
            text = ""
            while "<TEXT>" in sub:
                # print("In while <TEXT>")
                text_s = sub.find('<TEXT>') + len("<TEXT>")
                text_e = sub.find('</TEXT>')
                text = text + sub[text_s:text_e].strip() + "\n"
                sub = sub[text_e + len("</TEXT>"):]
            f = f[doc_end + len("</DOC>"):]
            doc_text = text.lower()
            # count += 1
            print(doc_no)
            ret = {
                "text": doc_text
            }
            es.index(index='sf_1000', id=doc_no, body=ret)