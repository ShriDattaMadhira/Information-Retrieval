import csv
import math
from elasticsearch import Elasticsearch

host = 'https://elastic:co7fVQl7vYqlZE3SHVnj3mwI@hw3.es.us-east-1.aws.found.io:9243'
es = Elasticsearch([host], timeout=3000)
print("ES PING:", es.ping())


def getQueries():
    fields = ["QueryID", "AssesorID", "DocumentID", "Score"]
    csvfile = open("Qrel-Datta.csv", "a+")
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
    for q in queries:
        pages = es.search(index="hw-3-empty", doc_type="_doc", size=250,
                          body={"query": {"match": {"text": q[0]}}})
        url_scores = []
        for u in pages['hits']['hits']:
            url_scores.append([u.get('_id'), u.get('_score')])

        print(q, ":", len(url_scores))

        esres = open("es_results.txt", "a+")
        for u in url_scores:
            esres.write(q[1] + " " + "MSD" + " " + u[0] + "\n")
            print(u[0], ":", u[1])
            csvwriter.writerow([q[1], "MSD", u[0], u[1]])
        esres.close()


def merge():
    f3 = open("Qrel-Merged.txt", "w")
    with open("Qrel-Datta.csv", "r") as f1, open("Qrel-Charan.csv", "r") as f2:
        csvreader1 = csv.reader(f1)
        csvreader2 = csv.reader(f2)
        for x, y in zip(csvreader1, csvreader2):
            f3.write("%s %s %s %d\n" % (x[0], (x[1] + "," + y[1]), x[2], math.ceil((int(x[3])+int(y[3]))/2)))
    f1.close()
    f2.close()
    f3.close()


queries = [['Founding Fathers', '152101'], ['independence war causes', '152102'], ['declaration of independence', '151203']]
# getQueries()
merge()
