from shutil import copyfile

path_invfiles = "/Users/shridatta/Downloads/Info Retrieval - CS6200/hw2/config2/Unstemmed_InvFiles_Compressed/"
path_catalogfiles = "/Users/shridatta/Downloads/Info Retrieval - CS6200/hw2/config2/Unstemmed_CatalogFiles/"
invFile1 = 2

copyfile(path_catalogfiles + "catalog1.txt", path_catalogfiles + "main_catalog.txt")
copyfile(path_invfiles + "invertedIndex1.txt.gz", path_invfiles + "main_inv.txt")

while invFile1 <= 85:
    print("============================================================================================================================")
    print("Processing file# ", invFile1)

    f = open(path_invfiles + "main_inv.txt", 'r')
    data_main = f.readlines()
    f.close()
    f1 = open(path_invfiles + "invertedIndex%s.txt" % invFile1, 'r')
    data1 = f1.readlines()
    f1.close()

    merge_catalog_main = []
    c = open(path_catalogfiles + "main_catalog.txt", 'r')
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

    f1 = open(path_invfiles + "main_inv.txt", 'w')
    c1 = open(path_catalogfiles + "main_catalog.txt", 'w')
    for i in range(len(data_main)):
        offset = f1.tell()
        f1.write(data_main[i])
        c1.write(merge_catalog_main[i] + ' ' + str(offset) + ' ' + str(len(data_main[i])) + '\n')
    f1.close()
    c1.close()

    invFile1 += 1

    # for word in merge_catalog_1:
    #     print("WORD:", word)
    #     index2 = merge_catalog_1.index(word)
    #     print("INDEX 2:", index2)
    #     if word in merge_catalog_main:
    #         strr = []
    #         index1 = merge_catalog_main.index(word)
    #         print("INDEX 1:", index1)
    #         print(data[index1].rstrip())
    #         print((f1.readlines())[index2])
    #         strr = data[index1].rstrip() + "; " + (f1.readlines()[index2])
    #         data[index1] = strr
    #         # print(strr)
    #     else:
    #         merge_catalog_main.append(word)
    #         data.append((f1.readlines())[index2])
