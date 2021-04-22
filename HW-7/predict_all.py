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


def feature_importance_print(top):
    for (coef_1, fn_1) in top:
        print("\t%.4f\t%-15s\t" % (coef_1, fn_1))


# Getting Data
file = open("./dataset_2_noStop.txt", "rb")
dataset = dill.load(file)
file.close()

df = pd.DataFrame.from_dict(dataset, orient='index')
new_df = df.iloc[:, [3, 4]]

# Splitting into train and test
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

# Initializing Vectorizer
vctzr = CountVectorizer(analyzer="word", min_df=0.001, max_df=0.995)
fitted_X_train = vctzr.fit_transform(x_train)
transformed_X_test = vctzr.transform(x_test)
# print(vctzr.vocabulary_)

# Saving to a file.
dump_svmlight_file(fitted_X_train, y_train, './dump.txt')

# Logistic Regression
lr = LogisticRegression(penalty='l1', solver='liblinear', C=0.01)
lr.fit(fitted_X_train, y_train)
predicted_prob = lr.predict_proba(transformed_X_test)
print("ROC AUC SCORE - Logistic Regression:")
print("{:.10f}".format(roc_auc_score(np.array(y_test), predicted_prob[:, 1])))

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

feature_names = vctzr.get_feature_names()
print("Top features for Logistic Regression")
feature_importance_print(sorted(zip(lr.coef_[0], feature_names), reverse=True)[:10])
print("Top features for Decision Tree Classifier")
feature_importance_print(sorted(zip(dt.feature_importances_, feature_names), reverse=True)[:10])
print("Top features for Naive Bayes Classifier")
feature_importance_print(sorted(zip(mnb.coef_[0], feature_names), reverse=True)[0:10])
