import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.datasets import dump_svmlight_file
import dill

file = open("./dataset_2_noStop.txt", "rb")
dataset = dill.load(file)
file.close()

df = pd.DataFrame.from_dict(dataset, orient='index')
# print(df)
new_df = df.iloc[:, [3, 4]]
# print(new_df)

x_train, x_test, y_train, y_test = train_test_split(new_df['content'], new_df['label'], test_size=0.2)

for index, v in y_train.items():
    if y_train[index] == "spam":
        y_train[index] = '1'
    else:
        y_train[index] = '0'
for index, v in y_test.items():
    if y_test[index] == 'spam':
        y_test[index] = '1'
    else:
        y_test[index] = '0'

file_given = open('./spam_given.txt').read()
spam_given = file_given.split("\n")

# Initialize the Vectorizer
vctzr = CountVectorizer(ngram_range=(1, 3), vocabulary=list(set(spam_given)), analyzer="word", min_df=0.001, max_df=0.995)
fitted_X_train = vctzr.fit_transform(x_train)
transformed_X_test = vctzr.transform(x_test)
# print(vctzr.vocabulary_)

dump_svmlight_file(fitted_X_train, y_train, './dump_given.txt')

# Logistic Regression
lr = LogisticRegression(penalty='l1', solver='liblinear')
lr.fit(fitted_X_train, y_train)
lr_prob = lr.predict_proba(transformed_X_test)
print("ROC AUC SCORE - Logistic Regression:")
print("{:.10f}".format(roc_auc_score(np.array(y_test), lr_prob[:, 1])))

# Decision Tree Classifier
dt = DecisionTreeClassifier()
dt.fit(fitted_X_train, y_train)
dt_prob = dt.predict_proba(transformed_X_test)
print("ROC AUC SCORE - Decision Tree Classifier:")
print("{:.10f}".format(roc_auc_score(np.array(y_test), dt_prob[:, 1])))

# Naive Bayes - Multinomial
mnb = MultinomialNB()
mnb.fit(fitted_X_train, y_train)
mnb_prob = mnb.predict_proba(transformed_X_test)
print("ROC AUC SCORE - Multinomial Naive Bayes:")
print("{:.10f}".format(roc_auc_score(np.array(y_test), mnb_prob[:, 1])))

logistic, dec_t, multinb = [], [], []
for i in range(len(y_test)):
    logistic.append([y_test.index[i], y_test[i], lr_prob[i][1]])
    dec_t.append([y_test.index[i], y_test[i], dt_prob[i][1]])
    multinb.append([y_test.index[i], y_test[i], mnb_prob[i][1]])
sorted(logistic, key=lambda x: x[2], reverse=True)
sorted(dec_t, key=lambda x: x[2], reverse=True)
sorted(multinb, key=lambda x: x[2], reverse=True)

logistic = logistic[0:10]
dec_t = dec_t[0:10]
multinb = multinb[0:10]

for i in range(10):
    print("TEXT for which the score is given: ", x_test[logistic[i][0]])
    print(" ")
