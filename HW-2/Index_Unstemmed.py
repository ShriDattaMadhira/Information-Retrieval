import os
import re
import dill
from collections import defaultdict
import gzip


def getStopWords(stopWords):
    path = "./stoplist.txt"
    sw = open(path, "r")
    for line in sw:
        stopWords.append(line.strip())
    sw.close()


def cleanText(txt):
    # t = ""
    # # Remove stop words
    # for word in txt.split():
    #     if word not in stopWords:
    #         t += word.strip().lower()

    # Removing Punctuations.
    p = "`!#$%&()*+/:;?@[\]^_{|}~-',"
    for x in txt:
        if x in p:
            txt = txt.replace(x, " ")

    # Removing '.' from unnecessary places.
    t = ""
    txt = re.sub(r'(?<!\w)[.](?!\w)', ' ', txt)
    for word in txt.split():
        if word.strip().lower() not in stopWords:
            if word.__contains__('.'):
                count = word.count('.')
                chars = word.split('.')
                for c in chars:
                    if count == 1:
                        if c.isdigit():
                            if bool(re.search(r'[0-9]\.$', word)) or bool(re.search(r'^\.[0-9]', word)):
                                word = word.replace('.', ' ')
                        else:
                            if not bool(re.search(r'^\.[0-9]', word)):
                                word = word.replace('.', ' ')
                    else:
                        if c.isdigit() or (not c.isdigit() and len(c) == 1):
                            word = re.sub(r'\.\.+', '.', word)
                        else:
                            word = re.sub(r'\.\.+', ' ', word)

            t += word.strip().lower() + " "
        else:
            continue

    return t


def getDocLen(text):
    l = 0
    for word in text.split():
        l += 1  # len(re.sub('\s+', ' ', word).strip().split(" "))
    return l


def getPositions():
    position = {}
    i = 0
    for word in text.split():
        i += 1
        tf = 0
        if word not in position:
            tf += 1
            position[word] = [i]
        else:
            position[word].append(i)

    return position


def tokenizer(text, doc_id):
    positions = getPositions()

    for term in text.split():
        if term not in tokenizer_dict:
            tokenizer_dict[term][doc_id] = positions[term]
        else:
            if doc_id not in tokenizer_dict[term]:
                tokenizer_dict[term][doc_id] = positions[term]
            else:
                continue


def create_InvIndex_Catalog_Files(token_dict, invFile_no):
    print("Processing for InvFile_No:", invFile_no)
    catalog_file = open("./Unstemmed_CatalogFiles/catalog%s.txt" % invFile_no, 'a+')
    inv_index_file = open("./Unstemmed_InvFiles/invertedIndex%s.txt" % invFile_no, 'a+')
    for term in token_dict:
        ip = []
        # To know where the file pointer is at currently.
        offset = inv_index_file.tell()

        for doc_id in token_dict[term]:
            ip.append(str(doc_id))
            ip.append(',')
            # ip.append(str(len(token_dict[term][doc_id])))  # Term Frequency = len(positions).
            # ip.append(',')
            ip.append(''.join(str(e) + " " for e in token_dict[term][doc_id]))
            ip.append(';')
        ip[len(ip) - 1] = '\n'
        ws = ''.join(ip)
        inv_index_file.write(ws)
        catalog_file.write(str(term) + ' ' + str(offset) + ' ' + str(len(ws)) + '\n')
    catalog_file.close()
    inv_index_file.close()
    with open('./Unstemmed_InvFiles/invertedIndex%s.txt' % invFile_no, 'rb') as f_in, gzip.open(
            './Unstemmed_InvFiles_Compressed/invertedIndex%s.txt.gz' % invFile_no, 'wb') as f_out:
        f_out.writelines(f_in)
    f_in.close()
    f_out.close()


tokenizer_dict = defaultdict(lambda: defaultdict(list))
stopWords = []
getStopWords(stopWords)
print(stopWords)
docInfo = {}  # Contains doc_len for each docId

vocabSize = 0  # Total number of distinct terms in the document collection. - 13787417
totalCF = 0  # Total number of terms in the document collection. - 19134796
docCount = 0
docId = 0
invFileNo = 1
path = "/Users/shridatta/Downloads/Info Retrieval - CS6200/hw1/config/ap89_collection/"
for file in os.listdir(path):
    if file != "readme":
        f = open(path + file).read()
        while "<DOC>" in f:
            docId += 1
            print("Processing for DOCID:", docId)
            docCount += 1
            doc_end = f.find('</DOC>')
            sub = f[:doc_end]
            # Getting Document Number.
            doc_no_s = sub.find('<DOCNO>') + len("<DOCNO>")
            doc_no_e = sub.find('</DOCNO>')
            doc_no = sub[doc_no_s:doc_no_e].strip()
            text, txt = "", ""
            while "<TEXT>" in sub:
                text_s = sub.find('<TEXT>') + len("<TEXT>")
                text_e = sub.find('</TEXT>')
                txt += sub[text_s:text_e].strip() + "\n"
                sub = sub[text_e + len("</TEXT>"):]
            f = f[doc_end + len("</DOC>"):]

            # Cleaning the text for each document
            text = cleanText(txt)
            # print(text)

            # Getting document length for use in retrieval models.
            # doc_len = getDocLen(text)
            # print(doc_len)
            # docInfo[docId] = doc_len

            # Tokenizing the document.
            tokenizer(text, docId)

            # totalCF += len(text.split())

            # Checking if docCount is 1000. To create Catalog files and Inverted Index files.
            # We will also re-initialize tokenizer_dict if we pass 1000 to get the new tokens.
            if docCount == 1000:
                create_InvIndex_Catalog_Files(tokenizer_dict, invFileNo)
                # vocabSize += len(tokenizer_dict.keys())
                tokenizer_dict = defaultdict(lambda: defaultdict(list))
                invFileNo += 1
                docCount = 0
            print("======================================================================================")

if invFileNo == 85:
    create_InvIndex_Catalog_Files(tokenizer_dict, invFileNo)

docInfo_path = "./doc_len.txt"
di = open(docInfo_path, 'wb')
dill.dump(docInfo, di)
di.close()
