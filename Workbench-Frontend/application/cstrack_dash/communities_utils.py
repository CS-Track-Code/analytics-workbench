"""This module allows the creating networks of communities and the interactions of each community
with users from another community
"""

import networkx as nx


def connections(g, node, list_communities, own_community):
    edges = []
    list_edges_node = g.edges(node)
    for c in range(0, len(list_communities)):
        if c != own_community:
            for element in list_communities[c]:
                for e in list_edges_node:
                    if e[1] == element:
                        edges.append((own_community, c))
    return edges





def get_communities_representative_graph(g, l_communities):
    n_graph = nx.Graph()
    nodes = list(range(0, len(l_communities)))
    edges = []
    #for each community
    for i in range(0, len(l_communities)):
        print("COMMUNITY", i)
        print(l_communities[i])
        #for each element in community
        for e in l_communities[i]:
            edges = connections(g, e, l_communities, i)
            print("----------- ARE THERE EDGES --------------")
            print(edges)
            if len(edges) > 0:
                n_graph.add_edges_from(edges)
    return n_graph