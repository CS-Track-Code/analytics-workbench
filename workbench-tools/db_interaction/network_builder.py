import networkx as nx


def build_networks(project_list):
    complete_network = nx.Graph()

    ra_min = 100
    ra_max = 0
    ra_total = 0

    sdg_min = 100
    sdg_max = 0
    sdg_total = 0

    ne_min = 100
    ne_max = 0
    ne_total = 0

    for project in project_list:

        complete_network.add_node(project["project_name"], title=project["project_name"], group="project")

        if project["ra_results"] is not None and "top_classification_areas_with_sim" in project["ra_results"]:
            ra_count = len(project["ra_results"]["top_classification_areas_with_sim"])
            ra_total += ra_count
            ra_min = ra_count if ra_count < ra_min else ra_min
            ra_max = ra_count if ra_count > ra_max else ra_max

            for ra in project["ra_results"]["top_classification_areas_with_sim"]:
                complete_network.add_node(ra[1], title=ra[0], group="research-area")
                complete_network.add_edge(project["project_name"], ra[1])

        if project["sdg_results"] is not None and "top_classification_areas_with_sim" in project["sdg_results"]:
            sdg_count = len(project["sdg_results"]["top_classification_areas_with_sim"])
            sdg_total += sdg_count
            sdg_min = sdg_count if sdg_count < sdg_min else sdg_min
            sdg_max = sdg_count if sdg_count > sdg_max else sdg_max

            for sdg in project["sdg_results"]["top_classification_areas_with_sim"]:
                complete_network.add_node(sdg[1], title=sdg[0], group="sdg")
                complete_network.add_edge(project["project_name"], sdg[1])

        if project["ner_results"] is not None:
            ne_count = len(project["ner_results"]["ner_list"])
            ne_total += ne_count
            ne_min = ne_count if ne_count < ne_min else ne_min
            ne_max = ne_count if ne_count > ne_max else ne_max
            for ne in project["ner_results"]["ner_list"]:
                if ne[0] != project["project_name"]:
                    if ne[0] in complete_network.nodes and complete_network.nodes[ne[0]]["group"] != "named-entity":
                        pass  # TODO: connection between projects?
                    else:
                        complete_network.add_node(ne[0], title=ne[0], group="named-entity", ne_type=ne[1])
                        complete_network.add_edge(project["project_name"], ne[0])

        else:
            ne_min = 0
    if len(project_list) > 0:
        ra_avg = ra_total / len(project_list)
        sdg_avg = sdg_total / len(project_list)
        ne_avg = ne_total / len(project_list)
    else:
        ra_avg = 0
        sdg_avg = 0
        ne_avg = 0

    named_entities_in_num = {
        "minimum": ne_min,
        "maximum": ne_max,
        "average": ne_avg
    }

    research_areas_in_num = {
        "minimum": ra_min,
        "maximum": ra_max,
        "average": ra_avg
    }

    sdgs_in_num = {
        "minimum": sdg_min,
        "maximum": sdg_max,
        "average": sdg_avg
    }

    return complete_network, named_entities_in_num, research_areas_in_num, sdgs_in_num  # , vis_nodes, vis_edges

