import decimal
import math
import random
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import pickle


def entropy(pr):
    return pr * float(math.log(pr, 2))


def perplexity(te):
    return pow(2, decimal.Decimal(te))


def calc_authority():
    normalizer = 0
    total_entropy = 0
    for link in link_graph:
        link_graph[link][0] = 0
        for inlink in link_graph[link][2]:
            link_graph[link][0] += link_graph[inlink][1]
        normalizer += link_graph[link][0]*link_graph[link][0]

    normalizer = math.sqrt(normalizer)

    for link in link_graph:
        link_graph[link][0] /= normalizer
        total_entropy += entropy(link_graph[link][0])

    # return perplexity(-total_entropy)


def calc_hub():
    normalizer = 0
    total_entropy = 0
    for link in link_graph:
        link_graph[link][1] = 0
        for outlink in link_graph[link][3]:
            link_graph[link][1] += link_graph[outlink][0]
        normalizer += link_graph[link][1]*link_graph[link][1]

    normalizer = math.sqrt(normalizer)

    for link in link_graph:
        link_graph[link][1] /= normalizer
        total_entropy += entropy(link_graph[link][1])

    # return perplexity(-total_entropy)


host = 'https://elastic:co7fVQl7vYqlZE3SHVnj3mwI@hw3.es.us-east-1.aws.found.io:9243'
es = Elasticsearch([host], timeout=3000)
print("ES PING:", es.ping())
info = Search(using=es, index="hw-3-empty", doc_type="_doc")
info = info.source([])

link_graph = {}
doc_ids, root_set, base_set = set(), set(), set()
d = 200

ilg = open("inlink_graph_file.txt", "rb")
inlink_graph = pickle.load(ilg)
ilg.close()

olg = open("outlink_graph_file.txt", "rb")
outlink_graph = pickle.load(olg)
olg.close()

pages = es.search(index="hw-3-empty", doc_type="_doc", size=1000,
                  body={"query": {"match": {"text": "American Revolution"}}})
print("Processing hits...")
for h in pages['hits']['hits']:
    root_set.add(h.get('_id'))
    base_set.add(h.get('_id'))

print("Root set length:", len(root_set))
print("Base set length before:", len(base_set))

c = 0
for link in root_set:
    il_set, ol_set = set(), set()

    for inlink in list(set(inlink_graph[link])):
        il_set.add(inlink)

    for outlink in list(set(outlink_graph[link])):
        ol_set.add(outlink)
    base_set.union(ol_set)

    if len(base_set) <= 10000:
        if len(il_set) <= d:
            base_set = base_set.union(il_set)
        else:
            temp_set = set(random.sample(list(il_set), d))
            base_set.union(temp_set)

    base_set = set(base_set)

print("Base set length after:", len(base_set))

print("Generating Link Graph...")
for link in base_set:
    temp_set = set()
    for outlink in list(set(outlink_graph[link])):
        if outlink in link_graph:
            temp_set.add(outlink)
    link_graph[link] = [1.0, 1.0, set(), temp_set]

    temp_set = set()
    for inlink in list(set(inlink_graph[link])):
        if inlink in link_graph:
            temp_set.add(inlink)
    link_graph[link][2].union(temp_set)

print("Link Graph generated with length", len(link_graph))
# print(link_graph)

flag, iterations = 0, 0
prevState_auth, currState_auth, prevState_hub, currState_hub = 0, 0, 0, 0
print("Calculating Authority and Hub scores...")
while flag < 20:
    calc_authority()
    calc_hub()
    flag += 1
    # currState_auth = calc_authority()
    # currState_hub = calc_hub()
    # if abs(prevState_hub-currState_hub) < 1 and abs(prevState_auth-currState_auth) < 1:
    #     flag += 1
    # iterations += 1
    # print("Difference HUB:", abs(prevState_hub-currState_hub))
    # print("Difference AUTH:", abs(currState_auth-prevState_auth))
    # print("Iteration #", iterations, "done.")
    # prevState_auth = currState_auth
    # prevState_hub = currState_hub

with open("hits_hub_1.txt", "a+") as hhf:
    hub_sort = sorted(link_graph, key=lambda x: link_graph[x][1])
    page_count = 0
    for link in reversed(hub_sort):
        if page_count > 500:
            break
        hhf.write('%s    %f\n' % (link, link_graph[link][1]))
        page_count += 1
    hhf.close()

with open("hits_auth_1.txt", "a+") as haf:
    auth_sort = sorted(link_graph, key=lambda x: link_graph[x][0])
    page_count = 0
    for link in reversed(auth_sort):
        if page_count > 500:
            break
        haf.write('%s    %f\n' % (link, link_graph[link][0]))
        page_count += 1
    haf.close()
