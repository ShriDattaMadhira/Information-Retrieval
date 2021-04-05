from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import pickle

host = 'https://elastic:co7fVQl7vYqlZE3SHVnj3mwI@hw3.es.us-east-1.aws.found.io:9243'
es = Elasticsearch([host], timeout=3000)
print("ES PING:", es.ping())
info = Search(using=es, index="hw-3-empty", doc_type="_doc")
info = info.source([])


def doc_id_process(identity):
    # for id in ids:
    # out_links = set()
    s = es.get(index="hw-3-empty", doc_type="_doc", id=identity.strip())
    il = s['_source'].get('inlinks')
    inlink_graph[identity] = list(set(il))
    ol = s['_source'].get('outlinks')
    outlink_graph[identity] = list(set(ol))


outlink_graph, inlink_graph, temp = {}, {}, {}
sink_nodes, doc_ids = set(), set()
count = 0

for i in info.scan():
    if i.meta.id not in doc_ids:
        count += 1
        print("Processing #", count, "ID:", i.meta.id)
        doc_id_process(i.meta.id)
        doc_ids.add(i.meta.id)

for out_link in outlink_graph:
    if len(outlink_graph[out_link]) == 0:
        sink_nodes.add(out_link)

print("Length of Sink Nodes: ", len(sink_nodes))
print("Length of Outlink Graph: ", len(outlink_graph.keys()))
print("Length of Inlink Graph: ", len(inlink_graph.keys()))

ilg = open("inlink_graph_file.txt", "wb")
pickle.dump(inlink_graph, ilg)
ilg.close()

olg = open("outlink_graph_file.txt", "wb")
pickle.dump(outlink_graph, olg)
olg.close()

snf = open("sink_nodes_file.txt", "wb")
pickle.dump(sink_nodes, snf)
snf.close()
