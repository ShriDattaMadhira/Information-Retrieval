from shutil import copyfile

path_invfiles = "/Users/shridatta/Downloads/Info Retrieval - CS6200/hw2/config2/Stemmed_InvFiles_wo-dfttf/"
path_catalogfiles = "/Users/shridatta/Downloads/Info Retrieval - CS6200/hw2/config2/Stemmed_CatalogFiles_wo-dfttf/"
invFile1 = 2

copyfile(path_catalogfiles + "catalog1.txt", path_catalogfiles + "main_catalog_stemmed.txt")
copyfile(path_invfiles + "invertedIndex1.txt", path_invfiles + "main_inv_stemmed.txt")

while invFile1 <= 85:
    print(
        "============================================================================================================================")
    print("Processing file# ", invFile1)

    f = open(path_invfiles + "main_inv_stemmed.txt", 'r')
    data_main = f.readlines()
    f.close()
    f1 = open(path_invfiles + "invertedIndex%s.txt" % invFile1, 'r')
    data1 = f1.readlines()
    f1.close()

    merge_catalog_main = []
    c = open(path_catalogfiles + "main_catalog_stemmed.txt", 'r')
    for line in c:
        merge_catalog_main.append(line.split()[0])
    c.close()

    merge_catalog_1 = []
    c1 = open(path_catalogfiles + "catalog%s.txt" % invFile1, 'r')
    for line in c1:
        merge_catalog_1.append(line.split()[0])
    c1.close()

    # word = "dribben"
    for word in merge_catalog_1:
        index1 = merge_catalog_1.index(word)
        if word in merge_catalog_main:
            index_main = merge_catalog_main.index(word)
            # print(data_main[index_main])
            s = data_main[index_main].rstrip() + "; " + data1[index1].rstrip() + '\n'
            data_main[index_main] = s
        else:
            merge_catalog_main.append(word)
            data_main.append(data1[index1])

    f1 = open(path_invfiles + "main_inv_stemmed.txt", 'w')
    c1 = open(path_catalogfiles + "main_catalog_stemmed.txt", 'w')
    for i in range(len(data_main)):
        offset = f1.tell()
        f1.write(data_main[i])
        c1.write(merge_catalog_main[i] + ' ' + str(offset) + ' ' + str(len(data_main[i])) + '\n')
    f1.close()
    c1.close()

    invFile1 += 1
