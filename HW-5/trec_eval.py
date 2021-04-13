import math
from collections import OrderedDict


def getResults(filename):
    es_res = open(filename, "r")
    for line in es_res:
        l = line.split()
        qID = l[0]
        docID = l[2]
        if qID not in usr_result_dict:
            usr_result_dict[qID] = [docID]
        else:
            usr_result_dict[qID].append(docID)
    es_res.close()


def getQrelInfo(filename):
    qrel_f = open(filename, "r")
    for line in qrel_f:
        l = line.split(' ')
        qID = l[0]
        docID = l[2]
        score = int(l[3].strip())
        if score >= 1:
            if qID not in qrel_dict:
                qrel_dict[qID] = [[docID, score]]
            else:
                qrel_dict[qID].append([docID, score])
    qrel_f.close()


def make_dicts(list_name, cut, prec):
    if cut not in list_name:
        list_name[cut] = [prec]
    else:
        list_name[cut].append(prec)
    return list_name


def printVals(list, text, k, qID):
    if k:
        for cut in k:
            if qID == '':
                print(text + str(cut) + ": " + str("{:.4f}".format(math.fsum(list[cut]) / len(list[cut]))))
            else:
                print(text + str(cut) + ": " + str("{:.4f}".format(math.fsum(list[cut]) / len(list[cut]))))
    else:
        print(text + ': ' + str("{:.4f}".format(math.fsum(list) / len(list))))


def calcPrecision(choice):
    k = [5, 10, 20, 50, 100]
    f = open("trec_eval_results.txt", "w")
    avg_prec, r_prec, ndcg = [], [], []
    Precisions, Recalls, F_Measures = {}, {}, {}
    for qID in usr_result_dict:
        # Getting Retrieved Docs from User Result.
        retrievedDocs = usr_result_dict[qID]

        # Getting Relevant Docs from QREL.
        scores = {}
        relevantDocs, rel_score = [], []
        if qID in qrel_dict:
            for l in qrel_dict[qID]:
                relevantDocs.append(l[0])
                scores[l[0]] = l[1]

        # Calculating Precision, Recall, and F-Measure.
        P_temp, R_temp, FM_temp = {}, {}, {}
        rank, num_rel_ret, sum_prec, rP = 0, 0, 0, 0
        for page in retrievedDocs:
            rank += 1
            relevantcy_flag, score = 0, 0
            if page in relevantDocs:
                relevantcy_flag = 1
                num_rel_ret += 1
                score = scores[page]
            rel_score.append(score)

            # Calculating Precision and Overall Precision (for average Precision over all queries).
            precision = num_rel_ret/rank
            if relevantcy_flag == 1:
                sum_prec += precision

            # Calculating Recall
            if len(relevantDocs) == 0:
                recall = 0
            else:
                recall = num_rel_ret/len(relevantDocs)

            # Calculating R-Precision over all the documents.
            if precision == recall:
                rP = precision  # or recall.

            # Writing the values to a file for Precision-Recall graph purposes.
            f.write(qID + ' ' + page + ' ' + str(rank) + ' ' + str(score) + ' ' + str("{:.4f}".format(precision)) + ' ' + str("{:.4f}".format(recall)) + '\n')

            if rank in k:
                Precisions = make_dicts(Precisions, rank, precision)
                Recalls = make_dicts(Recalls, rank, recall)
                P_temp = make_dicts(P_temp, rank, precision)
                R_temp = make_dicts(R_temp, rank, recall)
                f1 = 0
                if num_rel_ret > 0:
                    f1 = (2 * precision * recall) / (precision + recall)
                F_Measures = make_dicts(F_Measures, rank, f1)
                FM_temp = make_dicts(FM_temp, rank, f1)

        # Calculating Avg.Precision, R-Precision, and Normalized DCG.
        r_prec.append(rP)

        avg_precision = sum_prec/len(relevantDocs)
        avg_prec.append(avg_precision)

        list_pos, dcg = 0, 0.0
        for score in rel_score:
            list_pos += 1
            dcg += score/math.log(1+list_pos)

        list_pos, idcg = 0, 0.0
        rel_score = sorted(rel_score, reverse=True)
        for score in rel_score:
            list_pos += 1
            idcg += score/math.log(1+list_pos)

        if idcg == 0.0:
            ndcg_var = 0
        else:
            ndcg_var = dcg/idcg

        ndcg.append(ndcg_var)

        if choice == 2:
            print("=====================================================================")
            print("Query ID - ", qID)
            print("--------------------")
            print("Average Precision - " + qID + ": " + str("{:.4f}".format(avg_precision)))
            print("R Precision - " + qID + ": " + str("{:.4f}".format(rP)))
            print("nDCG - " + qID + ": " + str("{:.4f}".format(ndcg_var)))
            print("---------------------------------------------------------------------")
            print("Precision Values: ")
            printVals(P_temp, "Precision at ", k, qID)
            print("---------------------------------------------------------------------")
            print("Recall: ")
            printVals(R_temp, "Recall at ", k, qID)
            print("---------------------------------------------------------------------")
            print("F1 Values: ")
            printVals(FM_temp, "F1 at ", k, qID)
            print("=====================================================================")

    print("=====================================================================")
    printVals(avg_prec, 'Average Precision', [], '')
    printVals(r_prec, "R-Precision", [], '')
    printVals(ndcg, 'nDCG', [], '')
    print("---------------------------------------------------------------------")
    print("Precision Values: ")
    printVals(Precisions, "Precision at ", k, '')
    print("---------------------------------------------------------------------")
    print("Recall: ")
    printVals(Recalls, "Recall at ", k, '')
    print("---------------------------------------------------------------------")
    print("F1 Values: ")
    printVals(F_Measures, "F1 at ", k, '')
    print("=====================================================================")
    f.close()


usr_result_dict = OrderedDict()
qrel_dict = OrderedDict()
command = input()
params = command.split()
if len(params) == 3:
    # trec_eval qrel-file user-results-file
    getResults(params[2])
    getQrelInfo(params[1])
    calcPrecision(1)
if len(params) == 4:
    # trec_eval -q qrel-file user-results-file
    getResults(params[3])
    getQrelInfo(params[2])
    calcPrecision(2)
