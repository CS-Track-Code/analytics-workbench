import time
import networkx as nx
from networkx.algorithms import bipartite
import numpy
import pandas as pd
import operator
import pyvis

from db_interaction import network_builder


class Safe:
    def __init__(self, set_save_time, mongo_interface):
        self.mongo_int = mongo_interface
        self.complete_project_list = self.mongo_int.get_projects_with_user_generated_data()
        self.analyzed_projects = None
        self.tba_projects = None
        self.time_of_project_list = time.time()
        self.complete_network = None
        self.named_entities_in_num = None
        self.research_areas_in_num = None
        self.sdgs_in_num = None
        self.time_of_networks = time.time()
        self.max_time = set_save_time

        self.build_networks()

        self.time_ra_counter = time.time()
        self.ra_labels_and_counter = None
        self.sdg_labels_and_counter = None
        self.ne_labels_and_counter = None

        self.build_ra_occurance_counter()
        self.build_sdg_occurance_counter()
        self.build_ne_occurance_counter()

    def get_complete_project_list(self):
        if time.time() - self.time_of_project_list > self.max_time or self.complete_project_list is None:
            self.complete_project_list = self.mongo_int.get_projects_with_user_generated_data()
            self.time_of_project_list = time.time()
        return self.complete_project_list

    def split_lists(self):
        if time.time() - self.time_of_project_list > self.max_time or self.analyzed_projects is None:
            all_projects = self.get_complete_project_list()
            analyzed_projects = []
            tba_projects = []
            for project in all_projects:
                if project["ra_results"] is None and project["sdg_results"] is None and project["ner_results"] is None:
                    tba_projects.append(project)
                else:
                    analyzed_projects.append(project)

            self.analyzed_projects = analyzed_projects
            self.tba_projects = tba_projects

    def check_if_current(self):
        print(time.time() - self.time_of_networks)
        if time.time() - self.time_of_networks > self.max_time:
            self.get_complete_project_list()
            self.split_lists()
            self.build_networks()
            self.build_ra_occurance_counter()
            self.build_sdg_occurance_counter()
            self.build_ne_occurance_counter()
        else:
            print(" - not new")

    def build_networks(self):
        self.split_lists()
        complete_network, named_entities_in_num, research_areas_in_num, sdgs_in_num = \
            network_builder.build_networks(self.analyzed_projects)
        self.complete_network = complete_network

        self.named_entities_in_num = named_entities_in_num
        self.research_areas_in_num = research_areas_in_num
        self.sdgs_in_num = sdgs_in_num

        self.time_of_networks = time.time()

    def build_ra_occurance_counter(self):
        ra_occurances = {}
        self.split_lists()
        for project in self.analyzed_projects:
            if project["ra_results"] is not None and "top_classification_areas_with_sim" in project["ra_results"]:
                for ra in project["ra_results"]["top_classification_areas_with_sim"]:
                    if ra[1] in ra_occurances:
                        ra_occurances[ra[1]] += 1
                    else:
                        ra_occurances[ra[1]] = 1

        labels = []
        values = []
        for k, v in sorted(ra_occurances.items(), key=lambda item: item[1])[-20:]:
            labels.append(k)
            values.append(v)

        self.ra_labels_and_counter = {
            "labels": labels,
            "values": values
        }

    def build_sdg_occurance_counter(self):
        sdg_occurances = {}
        self.split_lists()
        for project in self.analyzed_projects:
            if project["sdg_results"] is not None and "top_classification_areas_with_sim" in project["sdg_results"]:
                for sdg in project["sdg_results"]["top_classification_areas_with_sim"]:
                    if sdg[1] in sdg_occurances:
                        sdg_occurances[sdg[1]] += 1
                    else:
                        sdg_occurances[sdg[1]] = 1

        labels = []
        values = []
        for k, v in sorted(sdg_occurances.items(), key=lambda item: item[1])[-20:]:
            labels.append(k)
            values.append(v)

        self.sdg_labels_and_counter = {
            "labels": labels,
            "values": values
        }

    def build_ne_occurance_counter(self):
        ne_occurances = {}
        self.split_lists()
        for project in self.analyzed_projects:
            if project["ner_results"] is not None and "ner_list" in project["ner_results"]:
                ne_of_project = []
                for ne in project["ner_results"]["ner_list"]:
                    if ne[0] not in ne_of_project:
                        ne_of_project.append(ne[0])
                        if ne[0] in ne_occurances:
                            ne_occurances[ne[0]] += 1
                        else:
                            ne_occurances[ne[0]] = 1

        labels = []
        values = []
        for k, v in sorted(ne_occurances.items(), key=lambda item: item[1])[-20:]:
            labels.append(k)
            values.append(v)

        self.ne_labels_and_counter = {
            "labels": labels,
            "values": values
        }

    def get_complete_network(self):
        self.check_if_current()
        return self.complete_network

    def get_project_name_list(self):
        list = []
        self.split_lists()
        for project in self.analyzed_projects:
            list.append(project["project_name"])
        return list

    def get_tba_project_names(self):
        list = []
        self.split_lists()
        for project in self.tba_projects:
            list.append(project["project_name"])
        return list

    def get_project_recommendations(self, fave_list=[], modified_list=[], visited_list=[], new_first=True):
        network = self.get_complete_network()
        nodes = network.nodes
        project_nodes = [node for node in nodes if network.nodes[node]["group"]=="project"]

        if fave_list == modified_list == visited_list is None:
            ppr = nx.pagerank(self.get_complete_network())
        else:
            personalization = {}
            for project in visited_list:
                personalization[project] = 1
            for project in modified_list:
                personalization[project] = 2
            for project in fave_list:
                personalization[project] = 3

            ppr = nx.pagerank(self.get_complete_network(), personalization=personalization)

        ppr_sort = sorted(ppr.items(), key=operator.itemgetter(1), reverse=True)
        ppr_filtered = [node for node in ppr_sort if node[0] in project_nodes]

        if new_first:
            ppr_new = []
            ppr_old = []

            for project in ppr_filtered:
                if project[0] in visited_list + modified_list + fave_list:
                    ppr_old.append(project)
                else:
                    ppr_new.append(project)
            ppr_filtered = ppr_new + ppr_old

        return ppr_filtered

    def get_project_count(self):
        return len(self.analyzed_projects)

    def get_numbers_of_ra_sdg_ne(self):
        return self.research_areas_in_num, self.sdgs_in_num, self.named_entities_in_num

    def get_ra_occurances(self):
        return self.ra_labels_and_counter

    def get_sdg_occurances(self):
        return self.sdg_labels_and_counter

    def get_ne_occurances(self):
        return self.ne_labels_and_counter

    def get_folded_project_network(self):
        top_nodes = {n for n, d in self.complete_network.nodes(data=True) if d["group"] == "project"}
        project_nodes, ne_ra_nodes = bipartite.sets(self.complete_network, top_nodes)
        bipartite_mat = bipartite.biadjacency_matrix(self.complete_network, project_nodes, ne_ra_nodes)
        bipartite_mat = bipartite_mat.toarray()
        b_mat_trans = bipartite_mat.transpose()
        mul1 = numpy.matmul(bipartite_mat, b_mat_trans)
        numpy.fill_diagonal(mul1, 0)
        network_data_frame = pd.DataFrame(mul1, index=project_nodes, columns=project_nodes)
        folded_network = nx.from_pandas_adjacency(network_data_frame)
        return folded_network

    def convert_network_to_vis(self, network_graph):
        for node in network_graph.nodes:
            network_graph.nodes[node]["size"] = 5 + 0.2 * network_graph.degree[node]

        ntG = pyvis.network.Network('1000px', '1000px')
        ntG.from_nx(network_graph)

        nodes, edges, head, height, width, options = ntG.get_network_data()
        for i in range(len(nodes)):
            nodes[i]["title"]=nodes[i]["label"]

        vis = {
            "nodes": nodes,
            "edges": edges,
            "options": options.replace("\n", "").replace("  ", "")
        }
        return vis

    def get_leafless_network(self):
        network = self.complete_network.copy()
        remove_nodes = []
        for node, data in network.nodes(data=True):
            if len([n for n in network.neighbors(node)]) < 2 and data["group"] != "project":
                remove_nodes.append(node)
        for node in remove_nodes:
            network.remove_node(node)
        return network

