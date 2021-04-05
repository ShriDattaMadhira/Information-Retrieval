import pickle
import math
import decimal


def entropy(pr):
    return pr * float(math.log(pr, 2))


def perplexity(te):
    return pow(2, decimal.Decimal(te))


def calc_page_rank(sn):
    total_sink_pr = 0
    total_entropy = 0
    for n in sn:
        total_sink_pr += pages[n]

    for page in pages:
        if page not in sink_nodes:
            newPR = (1-d)/N
            newPR += d*total_sink_pr/N
            try:
                for il in inlink_graph[page]:
                    newPR += d*pages[il]/len(outlink_graph[il])
            except:
                pass
            total_entropy += entropy(newPR)
            pages[page] = newPR

    return perplexity(-total_entropy)


ilg = open("inlink_graph_file.txt", "rb")
inlink_graph = pickle.load(ilg)
ilg.close()

olg = open("outlink_graph_file.txt", "rb")
outlink_graph = pickle.load(olg)
olg.close()

snf = open("sink_nodes_file.txt", "rb")
sink_nodes = pickle.load(snf)
snf.close()

pages = {}
for link in inlink_graph.keys():
    pages[link] = 1/61882

N, d, flag, iterations, prevState, currState = 61882, 0.85, 0, 0, 0, 0
while flag < 3:
    print("Iteration", iterations+1, "is starting...")
    currState = calc_page_rank(sink_nodes)
    if abs(currState-prevState) < 1:
        flag += 1
    iterations += 1
    print("Iteration", iterations, "done.", "prevState:", prevState, "currState:", currState)
    prevState = currState
print("Total number of iterations:", iterations)

with open("page_rank.txt", "a+") as prf:
    rank_sort = sorted(pages, key=lambda x: pages[x])
    page_count = 0
    for page in reversed(rank_sort):
        if page_count > 500:
            break
        prf.write('%s %.10f %d %d\n' % (page, pages[page], len(outlink_graph[page]), len(inlink_graph[page])))
        page_count += 1
    prf.close()
