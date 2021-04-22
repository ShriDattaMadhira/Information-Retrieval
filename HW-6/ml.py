from operator import itemgetter
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import RobustScaler


def get_train_dataset(bds, tqs, train, test):
    temp_train, temp_test = [], []
    for item in bds.index:
        temp_q = item.strip().split('-')[0]
        if int(temp_q) in tqs:
            temp_train.append(item.strip())
        else:
            temp_test.append(item.strip())

    train = pd.DataFrame(data=bds, index=temp_train)
    test = pd.DataFrame(data=bds, index=temp_test)

    return train, test


def write_test_result(pred, iteration, test):
    f = open("./results/test%s.txt" % (iteration+1), "w")
    count = 0
    temp = []
    for item in test.index:
        items = item.split('-')
        # print(items)
        qID = items[0]
        docID = items[1] + "-" + items[2]
        temp.append([qID, docID, pred[count]])
        count += 1

    temp.sort(key=itemgetter(0, 2), reverse=True)
    for i in temp:
        score = str("{:.14f}".format(i[2]))
        f.write("%s Q0 %s %s %s Exp\n" % (i[0], i[1], str(iteration+1), score))
    f.close()


def write_train_result(pred, iteration, train):
    f = open("./results/train%s.txt" % (iteration+1), "w")
    count = 0
    temp = []
    for item in train.index:
        items = item.split('-')
        # print(items)
        qID = items[0]
        docID = items[1] + "-" + items[2]
        temp.append([qID, docID, pred[count]])
        count += 1

    temp.sort(key=itemgetter(0, 2), reverse=True)
    for i in temp:
        score = str("{:.14f}".format(i[2]))
        f.write("%s Q0 %s %s %s Exp\n" % (i[0], i[1], str(iteration+1), score))
    f.close()


column_names = ["ES Score", "OkapiTF Score", "TFIDF Score", "BM25 Score", "Laplace Score", "JM Score", "Label"]

base_dataset = pd.read_csv("./Features_file.csv", index_col=0)
print("Base Dataset:")
print(base_dataset.head())

rs = RobustScaler()  # Normalize, minmax, standard
base_dataset[column_names] = rs.fit_transform(base_dataset[column_names])
print("Robust Scaling:")
print(base_dataset.head())

train_set = pd.DataFrame()
test_set = pd.DataFrame()
queries = [85, 59, 56, 71, 64, 62, 93, 99, 58, 77, 54, 87, 94, 100, 89, 61, 95, 68, 57, 97, 98, 60, 80, 63, 91]

for i in range(5):
    print("Iteration", i+1, "...")
    train_qs, test_qs = train_test_split(queries, test_size=5)

    train_set, test_set = get_train_dataset(base_dataset, train_qs, train_set, test_set)

    # x_train: features of train dataset
    # y_train: target of train dataset
    # x_test: features of test dataset
    # y_test: target of test dataset
    x_train, y_train, x_test, y_test = train_set.iloc[:, :-1], train_set.iloc[:, -1], test_set.iloc[:, :-1], \
                                       test_set.iloc[:, -1]
    lr = LogisticRegression(max_iter=1000, solver='liblinear', C=0.01, penalty='l1')
    lr.fit(x_train, y_train)
    write_test_result(lr.predict_proba(x_test)[:, 1], i, test_set)
    write_train_result(lr.predict_proba(x_train)[:, 1], i, train_set)
