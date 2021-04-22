from nltk.corpus import words as nltk_words
from bs4 import BeautifulSoup
import email
from email.parser import Parser
import dill
import re

parser = Parser()


def getBody(c):
    if c.is_multipart():
        # print("c is a multipart")
        for part in c.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload()
            if part.get_content_type() == "text/html":
                soup = BeautifulSoup(part.get_payload(), 'html.parser')
                return soup.get_text()
    else:
        # print("c is not a multipart")
        # if c.get_content_type() == "text/plain":
        #     return c.get_payload()
        # if c.get_content_type() == "text/html":
        soup = BeautifulSoup(c.get_payload(), 'html.parser')
        return soup.get_text()


def clean(text):
    # p = "`!#$%&()*+/:;?@[\]^_{|}~-',."
    wrds = ""
    text = text.replace("\n", "")
    text = re.sub('\s\s+', ' ', text)
    # for x in text:
    #     if x in p:
    #         text = text.replace(x, " ")
    for w in text.strip().split():
        wrds += w.strip() + " "
    return wrds


def check(text):
    cleaned = ""
    for wrds in text.split():
        if wrds in setofwords:  # and wrds not in stopList
            cleaned += wrds + " "
    return cleaned


def getemailInfo(r):
    eMail = email.message_from_string(r)
    sub = clean(str(eMail['Subject']))  # check(clean(str(eMail['Subject'])))
    body = clean(getBody(eMail))  # check(clean(getBody(eMail)))
    return sub, body


setofwords = set(nltk_words.words())
path_data = "/Users/shridatta/Downloads/Info Retrieval - CS6200/hw7/config7/trec07p/"

stopfile = open("/Users/shridatta/Downloads/Info Retrieval - CS6200/hw1/config/miscellaneous/stoplist.txt", "r")
stopList = stopfile.readlines()
stopfile.close()

path_index = "/Users/shridatta/Downloads/Info Retrieval - CS6200/hw7/config7/trec07p/full/index"
index = open(path_index, "r")
dataset = {}
unigrams = set()
for line in index:
    l = line.split()
    path = path_data + l[1][2:]
    label = l[0]
    doc_id = path[path.find("inmail.") + len("inmail."):]
    print("Processing the Files #", doc_id, "...")
    with open(path, "r", encoding="ISO-8859-1") as f:
        raw = f.read()
        subject, content = getemailInfo(raw)

    if subject is None or not content:
        continue
    else:
        dataset[doc_id] = {"path": path, "subject": subject, "raw_content": raw, "content": content, "label": label}

file = open("./dataset_2_uncleaned.txt", "wb")
dill.dump(dataset, file)
file.close()

# line = "ham ../data/inmail.75418"
# l = line.split()
# label = l[0]
# path = path_data + l[1][2:]
# doc_id = path[path.find("inmail.") + len("inmail."):]
# print("Processing File No", doc_id, "...")
# with open(path, "r", encoding="ISO-8859-1") as f:
#     subject, content = getemailInfo(f.read())
#
# # if subject is None or not content:
# #     print("One of the two is fucked.")
#
# print("SUBJECT:", subject)
# print("CONTENT:", content)
# print("SUBJECT:", type(subject))
# print("CONTENT:", type(content))
