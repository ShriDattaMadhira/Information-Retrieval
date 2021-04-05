import os
import pickle
from elasticsearch import Elasticsearch


def getStopWords(stopWords):
    slf = open("./stoplist.txt", "r")
    for line in slf:
        stopWords.append(line.strip())
    slf.close()


inlink_dict = pickle.load(open("./DATA/inlinkFile_Merged.txt", 'rb'))
outlink_dict = pickle.load(open("./DATA/outlinkFile_Merged.txt", 'rb'))

host = 'https://elastic:co7fVQl7vYqlZE3SHVnj3mwI@hw3.es.us-east-1.aws.found.io:9243'
es = Elasticsearch([host], timeout=3000)
print("ES PING:", es.ping())
response = es.indices.create(index="hw-3-empty")

stopWords = []
getStopWords(stopWords)

count = 0

path = "./DATA/DOC/"
for file in os.listdir(path):
    try:
        f = open(path + file).read()
        while f:
            doc_no_s = f.find('<DOCID>') + len("<DOCID>")
            doc_no_e = f.find('</DOCID>')
            doc_no = f[doc_no_s:doc_no_e].strip()
            # print("DOC NO:", doc_no)
            f = f[doc_no_e + len("</DOCID>"):]

            url_start = f.find('<URL>') + len("<URL>")
            url_end = f.find('</URL>')
            url = f[url_start:url_end].strip()
            f = f[url_end + len("</URL>"):]

            head_start = f.find('<HEAD>') + len("<HEAD>")
            head_end = f.find('</HEAD>')
            head = f[head_start:head_end].strip()
            f = f[head_end + len("</HEAD>"):]

            text_s = f.find('<TEXT>') + len("<TEXT>")
            text_e = f.find('</TEXT>')
            text = f[text_s:text_e].strip()
            f = f[text_e + len("</TEXT>"):].strip()
            doc_text = text.lower()
            inlinks = list(set(inlink_dict[url]))
            outlinks = list(set(outlink_dict[url]))
            ret = {
                "docid": url,
                "title": head,
                "text": doc_text,
                "inlinks": inlinks,
                "outlinks": outlinks,
                "author": "Shri Datta Madhira"
            }
            count += 1
            es.index(index='hw-3-empty', id=url, body=ret)
            print("PROCESSED DOCUMENT: ", count)
    except:
        print("Error at count:", count)
        pass

print("Error Free Documents: ", count)
