import decimal
import math


def create_link_graph(lines):
    for line in lines:
        l = line.strip().split()
        if l[0] not in link_graph:
            link_graph[l[0]] = [float(1 / N), list(set(l[1:])), 0]
        else:
            link_graph[l[0]][1] = list(set(l[1:]))
            link_graph[l[0]][1] = set(link_graph[l[0]][1])

        for page in list(set(l[1:])):
            if page not in link_graph:
                link_graph[page] = [float(1 / N), [], 1]
            else:
                link_graph[page][2] += 1


def get_sink_nodes():
    for key, val in link_graph.items():
        if val[2] == 0:
            sink_nodes.add(key)


def entropy(r):
    return r * float(math.log(r, 2))


def perplexity(te):
    return pow(2, decimal.Decimal(te))


def calc_page_rank(sn):
    total_sink_pr = 0
    total_entropy = 0
    for n in sn:
        total_sink_pr += link_graph[n][0]

    for key in link_graph:
        newPR = (1 - d) / N
        newPR += d * total_sink_pr / N
        for il in link_graph[key][1]:
            newPR += d * link_graph[il][0] / link_graph[il][2]
        link_graph[key][0] = newPR
        total_entropy += entropy(newPR)

    return perplexity(-total_entropy)


wt2g = open("./wt2g.txt", 'r')
wt2g_lines = wt2g.readlines()
wt2g.close()
N = len(wt2g_lines)

link_graph = {}
create_link_graph(wt2g_lines)
# print(len(link_graph.keys()))

sink_nodes = set()
get_sink_nodes()
# print(sink_nodes)
# print(len(sink_nodes))

d, iterations, prevState, currState = 0.85, 0, 0, 0
flag = 0
while flag < 4:
    print("Iteration", iterations + 1, "is starting...")
    currState = calc_page_rank(sink_nodes)
    if abs(currState - prevState) < 1:
        flag += 1
    iterations += 1
    print("Iteration", iterations, "done.", "prevState:", prevState, "currState:", currState)
    prevState = currState
print("Total number of iterations:", iterations)

with open("page_rank_wt2g.txt", "a+") as prf:
    rank_sort = sorted(link_graph, key=lambda x: link_graph[x][0])
    page_count = 0
    for page in reversed(rank_sort):
        if page_count >= 500:
            break
        prf.write('%s %.20f %d %d\n' % (page, link_graph[page][0], link_graph[page][2], len(link_graph[page][1])))
        page_count += 1
    prf.close()
