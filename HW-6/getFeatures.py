from collections import defaultdict, OrderedDict
import csv


def getQrelData(qrel_file):
    print("Getting Qrel Data...")
    qf = open(qrel_file, 'r')
    for line in qf:
        line = line.split()
        queryID = line[0]
        documentID = line[2]
        relevanceScore = line[3]
        if int(queryID) in query_ids:
            if queryID in qrel_dict:
                if relevanceScore in qrel_dict[queryID]:
                    qrel_dict[queryID][relevanceScore].append(documentID)
                else:
                    qrel_dict[queryID][relevanceScore] = [documentID]
            else:
                qrel_dict[queryID][relevanceScore] = [documentID]
    qf.close()


def completeDocCount():
    print("Getting remaining docs...")
    hw1 = open("/Users/shridatta/Downloads/Info Retrieval - CS6200/hw1/trec_eval/TFIDF.txt", "r")
    tfidf = hw1.readlines()
    hw1.close()
    score1 = '0'
    for q in qrel_dict:
        for line in tfidf:
            line = line.split()
            if len(qrel_dict[q][score1]) == 1000:
                break
            if line[0] == q:
                # print("Query ID", line[0], "-", q)
                if line[2] not in qrel_dict[q][score1] and line[2] not in qrel_dict[q]['1']:
                    qrel_dict[q][score1].append(line[2])


def makeScoreDicts(file_name, dict):
    print("Processing for", file_name, "...")
    path = "/Users/shridatta/Downloads/Info Retrieval - CS6200/hw1/trec_eval/" + file_name
    f1 = open(path, "r")
    temp = f1.readlines()
    f1.close()
    avg = 0
    for line in temp:
        line = line.split()
        ID = line[0] + "-" + line[2]
        dict[ID] = float(line[4])
        avg += float(line[4])
    avg = "{:.6f}".format(avg/len(temp))
    return avg, dict


def getScores():
    print("Creating the Feature Matrix...")
    f = open("nothere.txt", "w")
    count = 0
    for q in qrel_dict:
        for score in qrel_dict[q]:
            for doc in qrel_dict[q][score]:
                # flag = 0
                ID = q + "-" + doc
                if ID not in es or ID not in okapi:
                        count += 1
                        feature_dict[ID] = [(avgs[0]), (avgs[1]), (avgs[2]), (avgs[3]),
                                            (avgs[4]), (avgs[5]), 0]
                else:
                    feature_dict[ID] = [es[ID], okapi[ID], tfidf[ID], bm25[ID], laplace[ID], jm[ID], int(score)]
                # if ID not in es and ID not in okapi:
                #     feature_dict[ID] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, int(score)]
                #     # print(ID, "not in es. Score:", score)
                #     # flag = 1
                #     count += 1
                # elif ID not in es and ID in okapi:
                #     feature_dict[ID] = [0.0, okapi[ID], tfidf[ID], bm25[ID], laplace[ID], jm[ID], int(score)]
                #     # print(ID, "not in es. Score:", score)
                #     # flag = 1
                #     count += 1
                # elif ID not in okapi and ID in es:
                #     feature_dict[ID] = [es[ID], 0.0, 0.0, 0.0, 0.0, 0.0, int(score)]
                #     # print(ID, "not in okapi, tfidf, bm25, laplace, jelinek-mercer. Score:", score)
                #     # flag = 1
                #     count += 1
                # else:
                #     feature_dict[ID] = [es[ID], okapi[ID], tfidf[ID], bm25[ID], laplace[ID], jm[ID], int(score)]
    print("Number of Unavailable Documents:", count)


def writeToCSV():
    fields = ["ID", "ES Score", "OkapiTF Score", "TFIDF Score", "BM25 Score", "Laplace Score", "JM Score", "Label"]
    csvfile = open("Features_file.csv", "w")
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
    for identity in feature_dict:
        csvwriter.writerow([identity, feature_dict[identity][0], feature_dict[identity][1], feature_dict[identity][2],
                            feature_dict[identity][3], feature_dict[identity][4], feature_dict[identity][5],
                            feature_dict[identity][6]])


es, okapi, tfidf, bm25, laplace, jm = {}, {}, {}, {}, {}, {}
results_file_names = ["esbuiltin.txt", "okapiTF.txt", "TFIDF.txt", "bm25.txt", "laplace.txt", "jm.txt"]
dicts = [es, okapi, tfidf, bm25, laplace, jm]
avgs = [0.0]*6
qrel_dict = defaultdict(lambda: defaultdict(list))
feature_dict = OrderedDict()
query_ids = [85, 59, 56, 71, 64, 62, 93, 99, 58, 77, 54, 87, 94, 100, 89, 61, 95, 68, 57, 97, 98, 60, 80, 63, 91]

getQrelData("/Users/shridatta/Downloads/Info Retrieval - CS6200/hw1/trec_eval/qrels.adhoc.51-100.AP89.txt")
completeDocCount()

for i in range(6):
    avgs[i], dicts[i] = makeScoreDicts(results_file_names[i], dicts[i])

getScores()
print(len(feature_dict))
writeToCSV()

# for line in some:
#     l = line.split()
#     if ID == l[0]:
#         feature_dict[ID] = [float(l[1]), float(l[2]), float(l[3]), float(l[4]), float(l[5]),
#                             float(l[6]), int(l[7])]
#         flag = 1
#         break
# if flag == 0:

# some_file = open("./somearethere.txt", "r")
# some = some_file.readlines()
# some_file.close()


