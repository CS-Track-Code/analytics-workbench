import pandas as pd
import re
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import networkx as nx
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from os import path
from PIL import Image
from collections import Counter
import string
import nltk
from nltk.corpus import stopwords
import matplotlib.dates as mdates
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# stop_words para emplear en filtrados:

stop_words = ['#citizenscience', 'citizenscience', 'rt', 'citizen', 'science', 'citsci', 'cienciaciudadana']

# Función para grafica de barras:

def plotbarchart(numberbars, x, y, title, xlabel, ylabel):
    sns.set()
    plt.figure(figsize=(10, 8))
    plt.bar(x=x[:numberbars], height=y[:numberbars], color='lightsteelblue')
    plt.xlabel(xlabel, fontsize=15)
    plt.ylabel(ylabel, fontsize=15)
    plt.xticks(rotation=45)
    plt.title(title, fontsize=20, fontweight='bold')
    plt.tight_layout()
    plt.show()

# Función para obtener los subgrafos con NetworkX:

def get_subgraphs(graph):
    import networkx as nx
    components = list(nx.connected_components(graph))
    list_subgraphs = []
    for component in components:
        list_subgraphs.append(graph.subgraph(component))

    return list_subgraphs

# Función para convertir a direct graph los subgrafos:

def make_weightedDiGraph(ejes):
    edges_tupla = [tuple(x) for x in ejes]
    G = nx.DiGraph((x, y, {'weight': v}) for (x, y), v in Counter(edges_tupla).items())
    return G

def direct_subgraphs(subgraphs):
    list_directsubgraphs = []
    for i in range(len(subgraphs)):
        list_directsubgraphs.append(subgraphs[i].to_directed())

    return list_directsubgraphs

# Función para filtrar usando el topic que nos interese:

def filter_by_topic(df, keywords, stopwords):
    if keywords:
        df = df[df['Texto'].str.contains("|".join(keywords), case=False).any(level=0)]
        if stopwords:
            df = df[~df['Texto'].str.contains("|".join(stopwords), case=False).any(level=0)]
        df.to_csv("learning.csv")
    return df

# Función para filtrar por interés:

def filter_by_interest(df, interest):
    if interest:
        df = df[df['Marca']==interest]
    return df

# Calcular grafo de citas:

def get_cites(filename, keywords=None, stopwords=None, interest=None):
    df = pd.read_csv(filename, sep=';', encoding='latin-1', error_bad_lines=False)
    df = df.drop([78202], axis=0)
    df = filter_by_interest(df, interest)
    df = filter_by_topic(df, keywords, stopwords)
    dfMentions = df[['Usuario', 'Texto']].copy()
    dfMentions = dfMentions.dropna()
    dfEliminarRTs = dfMentions[dfMentions['Texto'].str.match('RT @')]
    dfMentions = dfMentions.drop(dfEliminarRTs.index)
    mentionsSubset = dfMentions[['Usuario', 'Texto']]
    mentionsList = [list(x) for x in mentionsSubset.to_numpy()]
    return mentionsList



# Calcular grafos de RT:

def get_retweets(df, keywords=None, stopwords=None, interest=None):
    dfRT = df[['Usuario', 'Texto', 'Fecha']].copy()  # Se copia a un dataframe de trabajo
    idx = dfRT['Texto'].str.contains('RT @', na=False)
    dfRT = dfRT[idx]  # Se seleccionan sólo las filas con RT
    subset = dfRT[['Usuario', 'Texto']]  # Se descarta la fecha
    retweetEdges = [list(x) for x in subset.to_numpy()]  # Se transforma en una lista
    return retweetEdges

# Función para extraer edges de rts y citas:

def get_edges(values):
    edges = []
    for row in values:
        reg = re.search('@(\w+)', row[1])
        if reg:
            matchRT = reg.group(1)  # Se extrae la primera mención que hace referencia a la cuenta retuiteada
            # row[1] = hashlib.md5(match.encode()).hexdigest()
            row[1] = matchRT  # Convierte el nombre de la cuenta en hash y lo asigna al elemento
            edges.append(row)
    return edges


## Código para crear gráfica de barras  de Hashtags más usados en los retuits:
# Seleccionamos las filas solo con RTs y creamos al final una lista que contiene todos los textos

def get_hashtagsRT(df_loaded, keywords=None, stopwords=None, interest=None):
    df = filter_by_interest(df_loaded, interest)
    df = filter_by_topic(df, keywords, stopwords)
    dfHashtagsRT = df[['Usuario', 'Texto']].copy()
    dfHashtagsRT = dfHashtagsRT.dropna()
    dfHashtagsRT = dfHashtagsRT[dfHashtagsRT['Texto'].str.match('RT @')]
    listHashtagsRT = dfHashtagsRT['Texto'].to_numpy()
    return listHashtagsRT

# Obtenemos los hashtags usados en esos textos

def get_edgesHashRT(values):
    edges = []
    for row in values:
        match = re.findall('#(\w+)', row)
        for hashtag in match:
            edges.append(hashtag)
    return edges

# Organizamos los hashtags en orden de más usados a menos usados y creamos una lista con la cantidad de veces que aparecen
def prepare_hashtags(list_h):
    print("This is the list")
    stop_words = ['#citizenscience', 'citizenscience', 'rt', 'citizen', 'science', 'citsci', 'cienciaciudadana']
    list_x = [x.lower() for x in list_h]
    list_x = [word for word in list_x if word not in stop_words]
    list_x = np.unique(list_x, return_counts=True)
    list_x = sorted((zip(list_x[1], list_x[0])), reverse=True)
    un = []
    unzipped = zip(*list_x)
    for v1 in unzipped:
        un.append(list(v1))
    """print("THIS IS UN")
    print(un)"""
    sortedNumberHashtags, sortedHashtagsRT = un[0], un[1]
    return sortedNumberHashtags, sortedHashtagsRT


# Código para calcular el grafo de Hashtags dentro de los retuits

def get_hashtagsRT2(filename, keywords=None, stopwords=None, interest=None):
    df = pd.read_csv(filename, sep=';', encoding='latin-1', error_bad_lines=False)
    df = filter_by_interest(df, interest)
    df = filter_by_topic(df, keywords, stopwords)
    dfHashtagsRT = df[['Usuario', 'Texto']]
    idx = dfHashtagsRT['Texto'].str.match('RT @', na=False)
    dfHashtagsRT = dfHashtagsRT[idx]
    listHashtagsRT = [list(x) for x in dfHashtagsRT.to_numpy()]
    return listHashtagsRT


def get_edgesHashRT2(values):
    edges = []
    for row in values:
        match = re.search('#(\w+)', row[1])
        if match:
            matchHashRT = match.group(1)
            row[1] = matchHashRT
            edges.append(row)
    return edges

# Combinación de los ejes de RTs y Citas:

def combined_edges(x,y):
    combined_edges = x + y
    return combined_edges

## Código para calcular grafo de hashtags relacionados fuera de RTs. Este grafo opretende mostrar que
##hashtags estan interrlacionados entre si.

def get_hashtagsmain(df_t, keywords=None, stopwords=None, interest=None):
    df = filter_by_interest(df_t, interest)
    df = filter_by_topic(df, keywords, stopwords)
    dfMainHashtags = df[['Usuario', 'Texto']].copy()
    dfMainHashtags = dfMainHashtags.dropna()
    idx = dfMainHashtags[dfMainHashtags['Texto'].str.match('RT @')]
    dfMainHashtags = dfMainHashtags.drop(idx.index)
    subset = dfMainHashtags['Texto']
    listMainHashtags = subset.to_numpy()
    return listMainHashtags

def mainHashtags(values):
    stop_words = ['#citizenscience', 'citizenscience', 'rt', 'citizen', 'science', 'citsci', 'cienciaciudadana']
    mainHashtags = []
    aristasHashtags = []
    for row in values:
        match = re.findall('#(\w+)', row.lower())
        length = len(match)
    try:
        match = [word for word in match if word not in stop_words]
    except ValueError:
        pass
    for index,hashtag in enumerate(match):
        mainHashtags.append(hashtag)
        if index | (length-2):
            nextHashtags = match[index+1:length-1]
            for nextHashtags in nextHashtags:
                aristasHashtags.append([hashtag,nextHashtags])
    return aristasHashtags

def prepare_hashtags2(list):
    mainHashtags = np.unique(list,return_counts=True)
    mainHashtags = sorted((zip(mainHashtags[1], mainHashtags[0])), reverse=True)
    sortedNumberHashtags, sortedMainHashtags = zip(*mainHashtags)
    hashtagsOnce = [t[1] for t in mainHashtags if t[0] == 1]
    hashtagsFinales = [hashtag for hashtag in list if hashtag[0] not in hashtagsOnce]
    hashtagsFinales = [hashtag for hashtag in hashtagsFinales if hashtag[1] not in hashtagsOnce]
    return hashtagsFinales

# Creación de grafo hashtags más utilizados (relacionado con usuario):

def get_hashtagsmain2(filename, keywords=None, stopwords=None, interest=None):
    df = pd.read_csv(filename, sep=';', encoding='latin-1', error_bad_lines=False)
    df = df.drop([78202], axis=0)
    df = filter_by_interest(df, interest)
    df = filter_by_topic(df, keywords, stopwords)
    dfMainHashtags = df[['Usuario', 'Texto']].copy()
    dfMainHashtags = dfMainHashtags.dropna()
    idx = dfMainHashtags[dfMainHashtags['Texto'].str.match('RT @')]
    dfMainHashtags = dfMainHashtags.drop(idx.index)
    subset = dfMainHashtags[['Usuario','Texto']]
    listMainHashtags = [list(x) for x in subset.to_numpy()]
    return listMainHashtags

def get_edgesmain2(values):
    stop_words = [['citizenscience', 'rt', 'citizen', 'science', 'citsci', 'cienciaciudadana','CitizenScience']]
    edges = []
    for row in values:
        match = re.search('#(\w+)', row[1])
        if match:
            matchhash = match.group(1)
            row[1] = matchhash
            edges.append(row)
            edges = [i for i in edges if i[1] != stop_words]
    return edges

# Creación de gráfica hashtags más usados fuera de RTs (usar get_hashtagsmain())

def get_edgesMain(values):
    edges = []
    for row in values:
        match = re.findall('#(\w+)', row.lower())
        for hashtag in match:
            edges.append(hashtag)
    return edges

# Hashtags del Bot:
botwords=['airpollution', 'luftdaten', 'fijnstof', 'waalre', 'pm2', 'pm10']

def prepare_hashtagsmain(list_h, stopwords=None):
    print(list_h)
    stop_words = ['#citizenscience', 'citizenscience', 'rt', 'citizen', 'science', 'citsci', 'cienciaciudadana', 'machinelearning', 'ml', 'ai', 'deeplearning' ]
    if stopwords:
        stop_words = stop_words + stopwords
    list_x = [x.lower() for x in list_h]
    list_x = [word for word in list_x if word.strip() not in stop_words]
    print(list_x)
    mainHashtags = np.unique(list_x,return_counts=True)
    mainHashtags = sorted((zip(mainHashtags[1], mainHashtags[0])), reverse=True)
    un = []
    unzipped = zip(*mainHashtags)
    for v1 in unzipped:
        un.append(list(v1))
    print("THIS IS UN")
    print(un)
    sortedNumberHashtags, sortedMainHashtags = un[0], un[1]
    return sortedNumberHashtags,sortedMainHashtags


def get_prop_type(value, key=None):
    """
    Performs typing and value conversion for the graph_tool PropertyMap class.
    If a key is provided, it also ensures the key is in a format that can be
    used with the PropertyMap. Returns a tuple, (type name, value, key)
    """

    # Deal with the value
    if isinstance(value, bool):
        tname = 'bool'

    elif isinstance(value, int):
        tname = 'float'
        value = float(value)

    elif isinstance(value, float):
        tname = 'float'

    elif isinstance(value, dict):
        tname = 'object'

    else:
        tname = 'string'
        value = str(value)

    return tname, value, key


def nx2gt(nxG):
    """
    Converts a networkx graph to a graph-tool graph.
    """
    # Phase 0: Create a directed or undirected graph-tool Graph
    gtG = gt.Graph(directed=nxG.is_directed())

    # Add the Graph properties as "internal properties"
    for key, value in nxG.graph.items():
        # Convert the value and key into a type for graph-tool
        tname, value, key = get_prop_type(value, key)

        prop = gtG.new_graph_property(tname)  # Create the PropertyMap
        gtG.graph_properties[key] = prop      # Set the PropertyMap
        gtG.graph_properties[key] = value     # Set the actual value

    # Phase 1: Add the vertex and edge property maps
    # Go through all nodes and edges and add seen properties
    # Add the node properties first
    nprops = set()  # cache keys to only add properties once
    for node, data in nxG.nodes(data=True):

        # Go through all the properties if not seen and add them.
        for key, val in data.items():
            if key in nprops:
                continue  # Skip properties already added

            # Convert the value and key into a type for graph-tool
            tname, _, key = get_prop_type(val, key)

            prop = gtG.new_vertex_property(tname)  # Create the PropertyMap
            gtG.vertex_properties[key] = prop      # Set the PropertyMap

            # Add the key to the already seen properties
            nprops.add(key)

    # Also add the node id: in NetworkX a node can be any hashable type, but
    # in graph-tool node are defined as indices. So we capture any strings
    # in a special PropertyMap called 'id' -- modify as needed!
    gtG.vertex_properties['id'] = gtG.new_vertex_property('string')

    # Add the edge properties second
    eprops = set()  # cache keys to only add properties once
    for src, dst, data in nxG.edges(data=True):

        # Go through all the edge properties if not seen and add them.
        for key, val in data.items():
            if key in eprops:
                continue  # Skip properties already added

            # Convert the value and key into a type for graph-tool
            tname, _, key = get_prop_type(val, key)

            prop = gtG.new_edge_property(tname)  # Create the PropertyMap
            gtG.edge_properties[key] = prop      # Set the PropertyMap

            # Add the key to the already seen properties
            eprops.add(key)

    # Phase 2: Actually add all the nodes and vertices with their properties
    # Add the nodes
    vertices = {}  # vertex mapping for tracking edges later
    for node, data in nxG.nodes(data=True):

        # Create the vertex and annotate for our edges later
        v = gtG.add_vertex()
        vertices[node] = v

        # Set the vertex properties, not forgetting the id property
        data['id'] = str(node)
        for key, value in data.items():
            gtG.vp[key][v] = value  # vp is short for vertex_properties

    # Add the edges
    for src, dst, data in nxG.edges(data=True):

        # Look up the vertex structs from our vertices mapping and add edge.
        e = gtG.add_edge(vertices[src], vertices[dst])

        # Add the edge properties
        for key, value in data.items():
            gtG.ep[key][e] = value  # ep is short for edge_properties

    # Done, finally!
    return gtG

# Función para extraer los valores de degree,outdegree, eigenvector y betweenness y crear un csv:

def get_degrees(G):
    import networkit as nk
    from operator import itemgetter
    n_g = nk.nxadapter.nx2nk(G)
    idmap = dict((u, id) for (id, u) in zip(G.nodes(), range(G.number_of_nodes())))
    btwn = nk.centrality.Betweenness(n_g)
    ec = nk.centrality.EigenvectorCentrality(n_g)
    ec.run()
    btwn.run()
    bt_results = sorted(btwn.ranking(), key=itemgetter(0))
    bt_results = [round(value,4) for id_, value in bt_results]
    ec_results = sorted(ec.ranking(), key=itemgetter(0))
    ec_results = [round(value,4) for id_, value in ec_results]
    names = []
    in_degrees = []
    out_degrees = []
    nodes = n_g.iterNodes()
    for key in nodes:
        names.append(idmap[key])
        in_degrees.append(n_g.degreeIn(key))
        out_degrees.append(n_g.degreeOut(key))
    return pd.DataFrame({"Name": names, "InD.": in_degrees, "OutD.": out_degrees, "Eigen C.": ec_results, "Betweenness C": bt_results})

def csv_degval(Digraph, filename):
    list_values = []
    outdegrees2 = dict(Digraph.out_degree())
    indegrees = dict(Digraph.in_degree())
    centrality = dict(nx.eigenvector_centrality(Digraph))
    betweenness = dict(nx.betweenness_centrality(Digraph))
    indegtupl = sorted([(k, v) for k, v in indegrees.items()], key=lambda x:x[1], reverse=True)
    indegtupl = indegtupl[0:10]
    names = [i[0] for i in indegtupl]
    outdegtupl = sorted([(k,v) for k,v in outdegrees2.items()], key=lambda x:x[1], reverse=True)
    centraltupl = sorted([(k,v) for k,v in centrality.items()], key=lambda x:x[1], reverse=True)
    betwentupl = sorted([(k,v) for k,v in betweenness.items()], key=lambda x:x[1], reverse=True)
    for name in names:
        pos_indeg = [y[0] for y in indegtupl].index(name)
        rank_indeg = pos_indeg + 1
        indeg_val = indegtupl[pos_indeg][1]
        pos_outdeg = [y[0] for y in outdegtupl].index(name)
        rank_outdeg = pos_outdeg + 1
        outdeg_val = outdegtupl[pos_outdeg][1]
        pos_central = [y[0] for y in centraltupl].index(name)
        rank_central = pos_central + 1
        central_val = centraltupl[pos_central][1]
        central_val = round(centraltupl[pos_central][1],6)
        pos_between = [y[0] for y in betwentupl].index(name)
        rank_between = pos_between + 1
        between_val = round(betwentupl[pos_between][1], 6)
        list_values.append((name, indeg_val, rank_indeg, outdeg_val, rank_outdeg, central_val, rank_central,
                        between_val, rank_between))
    df = pd.DataFrame(list_values,
                      columns=['Name', 'Indegree', 'R.In', 'Outdegree', 'R.Out', 'Eigenvector', 'R.EI', 'Betweenness',
                               'R.Bet'])
    return df

## Funciones para obtener los elementos de la two mode:

def get_twomodeRT(full_df, keywords=None, stopwords=None, interest=None):
    df = filter_by_interest(full_df, interest)
    df = filter_by_topic(df, keywords, stopwords)
    dfRT = df[['Usuario', 'Texto']].copy()
    idx = dfRT['Texto'].str.contains('RT @', na=False)
    dfRT = dfRT[idx]
    subset = dfRT[['Usuario', 'Texto']]
    u = list(subset['Usuario'])
    v = list(subset['Texto'])
    edges = [tuple(x) for x in subset.to_numpy()]
    G = nx.Graph()
    G.add_nodes_from(set(u), bipartite=0)
    G.add_nodes_from(set(v), bipartite=1)
    G.add_edges_from(edges)
    print("Número nodos:", len(G.nodes))
    if len(G.nodes) >= 10000:
        G = nx.k_core(G, k=3)
    elif len(G.nodes) >= 4000:
        G = nx.k_core(G, k=2)
    else:
        G = nx.k_core(G, k=1)

    counter = Counter(list((nx.core_number(G).values())))
    print(counter)
    pos = {}

    pos.update((node, (1, index)) for index, node in enumerate(set(u)))
    pos.update((node, (2, index)) for index, node in enumerate(set(v)))

    return G
# Obtención de los elementos u,v y los edges que los unen para usuario y texto en los retuits:

def get_uv_edgesRT(filename, keywords=None, stopwords=None, interest=None):
    edges = []
    df = pd.read_csv(filename, sep=';', error_bad_lines=False)
    df = filter_by_topic(df, keywords, stopwords)
    df = filter_by_interest(df, interest)
    dfRT = df[['Usuario', 'Texto']].copy()
    idx = dfRT['Texto'].str.contains('RT @', na=False)
    dfRT = dfRT[idx]
    subset = dfRT[['Usuario', 'Texto']]
    u = list(subset['Usuario'])
    v = list(subset['Texto'])
    edges = [tuple(x) for x in subset.to_numpy()]
    return edges, u, v

# Obtención de los elemetnos u,v y los edges para los hashtags fuera de los retuits:

def get_uv_HashMain(filename, keywords=None, stopwords=None, interest=None):
    edges = []
    df = pd.read_csv(filename, sep=';', error_bad_lines=False, encoding='utf-8')
    df = filter_by_topic(df, keywords, stopwords)
    df = filter_by_interest(df, interest)
    dfMain = df[['Usuario', 'Texto']].copy()
    dfMain = dfMain.dropna()
    dfEliminarRTs = dfMain[dfMain['Texto'].str.match('RT @')]
    dfMain = dfMain.drop(dfEliminarRTs.index)
    subset = dfMain[['Usuario', 'Texto']]
    u = list(subset['Usuario'])
    listHT = [list(x) for x in subset.to_numpy()]
    stop_words = [['citizenscience', 'rt', 'citizen', 'science', 'citsci', 'cienciaciudadana','CitizenScience']]
    for row in listHT:
        match = re.search('#(\w+)', row[1])
        if match:
            matchhash = match.group(1)
            row[1] = matchhash
            edges.append(row)
            edges = [i for i in edges if i[1] != stop_words]
    v = [x[1] for x in edges]
    return edges, u, v

def getuv_htRT(filename, keywords=None, stopwords=None, interest=None, filter_hashtags=None):
    edges = []
    stop_words = ['CitizenScience', 'citizenScience','citizenscience', 'rt', 'citizen', 'science', 'citsci', 'cienciaciudadana', '#CitizenScience']
    df = pd.read_csv(filename, sep=';', error_bad_lines=False, encoding='utf-8')
    df = filter_by_topic(df, keywords, stopwords)
    df = filter_by_interest(df, interest)
    df = df[['Usuario', 'Texto']].copy()
    df = df.dropna()
    idx = df['Texto'].str.contains('RT @', na=False)
    dfRT = df[idx]  # Se seleccionan sólo las filas con RT
    subset = dfRT[['Usuario', 'Texto']]
    listHT = [list(x) for x in subset.to_numpy()]
    for row in listHT:
        match = re.search('#(\w+)', row[1])
        if match:
            matchhash = match.group(1)
            row[1] = matchhash
            edges.append(row)
    if filter_hashtags == True:
        filter_edges = []
        for edge in edges:
           stop = False
           for word in edge:
               #print(word, word.lower() in stop_words)
                if word.lower() in stop_words:
                    stop = True
           if not stop:
               filter_edges.append(edge)

    else:
        pass
    u = [x[0] for x in filter_edges]
    v = [x[1] for x in filter_edges]
    return filter_edges, u, v


# Wordcloud function for main hashtags:

def wordcloudmain(df, keywords=None, stopwords=None, interest=None ):
    hashtags =[]
    stop_words = ['citizenscience', 'rt', 'citizen', 'science', 'citsci', 'cienciaciudadana', 'CitizenScience']
    df = filter_by_interest(df, interest)
    df = filter_by_topic(df, keywords, stopwords)
    df = df[['Usuario', 'Texto']]
    df = df.dropna()
    idx = df[df['Texto'].str.match('RT @')]
    df = df.drop(idx.index)
    subset = df['Texto']
    for row in subset:
        match = re.findall('#(\w+)', row.lower())
        for hashtag in match:
            hashtags.append(hashtag)
    unique_string = (' ').join(hashtags)
    wordcloud = WordCloud(width=900, height=900, background_color='white', stopwords=stop_words,
                          min_font_size=10, max_words=10405, collocations=False, colormap='winter').generate(unique_string)
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig("wc.png")

# Wordcloud for main hashtags plotted inside a logo:

def transform_format(val):
    if val == 0:
        return 255
    else:
        return val


def wordcloud_mainhtlogo(filename, keywords=None, stopwords=None, interest=None, image=None):
    hashtags =[]
    stop_words = ['citizenscience', 'rt', 'citizen', 'science', 'citsci', 'cienciaciudadana', 'CitizenScience']
    df = pd.read_csv(filename, sep=';', encoding='latin-1', error_bad_lines=False)
    df = df = filter_by_interest(df, interest)
    df = filter_by_topic(df, keywords, stopwords)
    df = df[['Usuario', 'Texto']]
    df = df.dropna()
    idx = df[df['Texto'].str.match('RT @')]
    df = df.drop(idx.index)
    subset = df['Texto']
    for row in subset:
        match = re.findall('#(\w+)', row.lower())
        for hashtag in match:
            hashtags.append(hashtag)
    unique_string = (' ').join(hashtags)
    logo = np.array(Image.open(image))
    transformed_logo = np.ndarray((logo.shape[0], logo.shape[1]), np.int32)

    for i in range(len(logo)):
        transformed_logo[i] = list(map(transform_format, logo[i]))

    wc = WordCloud(width = 900, height = 900,
                background_color ='ghostwhite',
                stopwords = stop_words,
                min_font_size = 5, max_font_size=30, max_words=10405, collocations=False,mask=transformed_logo,
          contour_width=2, contour_color='cornflowerblue',mode='RGB', colormap='summer').generate(unique_string)

    plt.figure(figsize=[25, 10])
    plt.imshow(wc)
    plt.axis("off")
    plt.show()


# Wordlcoud for hashtags in the RTs:

def wordcloudRT(filename, keywords=None, stopwords=None, interest=None ):
    hashtags =[]
    stop_words = ['citizenscience', 'rt', 'citizen', 'science', 'citsci', 'cienciaciudadana', 'CitizenScience']
    df = pd.read_csv(filename, sep=';', encoding='latin-1', error_bad_lines=False)
    df = df = filter_by_interest(df, interest)
    df = filter_by_topic(df, keywords, stopwords)
    df = df[['Usuario', 'Texto']]
    df = df.dropna()
    idx = df['Texto'].str.contains('RT @', na=False)
    df = df[idx]
    subset = df['Texto']
    for row in subset:
        match = re.findall('#(\w+)', row.lower())
        for hashtag in match:
            hashtags.append(hashtag)
    unique_string = (' ').join(hashtags)
    wordcloud = WordCloud(width=900, height=900, background_color='white', stopwords=stop_words,
                          min_font_size=10, max_words=10405, collocations=False, colormap='winter').generate(unique_string)
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.show()

def wordcloudRT_logo(filename, keywords=None, stopwords=None, interest=None, image=None):
    hashtags = []
    stop_words = ['citizenscience', 'rt', 'citizen', 'science', 'citsci', 'cienciaciudadana', 'CitizenScience']
    df = pd.read_csv(filename, sep=';', encoding='latin-1', error_bad_lines=False)
    df = df = filter_by_interest(df, interest)
    df = filter_by_topic(df, keywords, stopwords)
    df = df[['Usuario', 'Texto']]
    df = df.dropna()
    idx = df['Texto'].str.contains('RT @', na=False)
    df = df[idx]
    subset = df['Texto']
    for row in subset:
        match = re.findall('#(\w+)', row.lower())
        for hashtag in match:
            hashtags.append(hashtag)
    unique_string = (' ').join(hashtags)

    logo = np.array(Image.open(image))
    transformed_logo = np.ndarray((logo.shape[0], logo.shape[1]), np.int32)

    for i in range(len(logo)):
        transformed_logo[i] = list(map(transform_format, logo[i]))

    wc = WordCloud(width=900, height=900,
                   background_color='ghostwhite',
                   stopwords=stop_words,
                   min_font_size=5, max_font_size=30, max_words=10405, collocations=False, mask=transformed_logo,
                   contour_width=2, contour_color='cornflowerblue', mode='RGB', colormap='summer').generate(
        unique_string)

    plt.figure(figsize=[25, 10])
    plt.imshow(wc)
    plt.axis("off")
    plt.show()


# Cálculo de las palabras más usadas:
# La función emplea la columna texto y podemos añadir un número n que indica cuantas palabras

def most_common(filename,number=None):
    df = pd.read_csv(filename, sep=';', encoding='latin-1', error_bad_lines=False)
    subset = df['Texto']
    subset = subset.dropna()
    # Definimos stopwords en varios idiomas y símbolos que queremos eliminar del resultado
    s = stopwords.words('english')
    e = stopwords.words('spanish')
    r = STOPWORDS
    d = stopwords.words('german')
    p = string.punctuation
    new_elements = ('\\n', 'rt', '?', '¿', '&', 'that?s', '??', '-', '???')
    s.extend(new_elements)
    s.extend(e)
    s.extend(r)
    s.extend(d)
    s.extend(p)
    s = set(s)
    # Calculamos la frecuencia de las palabras
    word_freq = Counter(" ".join(subset).lower().split())
    for word in s:
        del word_freq[word]
    return word_freq.most_common(number)

# Top palabras más usadas en wordcloud:

def most_commonwc(filename):
    df = pd.read_csv(filename, sep=';', encoding='latin-1', error_bad_lines=False)
    subset = df['Texto']
    subset = subset.dropna()
    s = stopwords.words('english')
    e = stopwords.words('spanish')
    r = STOPWORDS
    d = stopwords.words('german')
    p = string.punctuation
    new_elements = ('\\n', 'rt', '?', '¿', '&', 'that?s', '??', '-','the', 'to')
    s.extend(new_elements)
    s.extend(e)
    s.extend(r)
    s.extend(d)
    s.extend(p)
    stopset = set(s)
    word_freq = Counter(" ".join(subset).lower().split())
    for word in s:
        del word_freq[word]
    wordcloud = WordCloud(width=900, height=900, background_color='white', stopwords=stopset,
                          min_font_size=10, max_words=10405, collocations=False,
                          colormap='winter').generate_from_frequencies(word_freq)
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.show()

# Gráficos temporales
# Función para seleccionar Usuario,Texto y Fecha en el df y eliminar RTs:

def Maindf(filename, keywords=None, stopwords=None, interest=None):
    df = pd.read_csv(filename, sep=';', encoding='utf-8', error_bad_lines=False)
    df = filter_by_interest(df, interest)
    df = filter_by_topic(df, keywords, stopwords)
    dfMain= df[['Usuario', 'Texto', 'Fecha']].copy()
    dfMain = dfMain.dropna()
    dfEliminarRTs = dfMain[dfMain['Texto'].str.match('RT @')]
    dfMain = dfMain.drop(dfEliminarRTs.index)
    dfMain = dfMain[dfMain['Fecha'].str.match('[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]\s[0-9]')]
    return dfMain

# Función para seleccionar Usuario, Texto y Fecha en los RTs:

def dfRT(filename, keywords=None, stopwords=None, interest=None):
    df = pd.read_csv(filename, sep=';', encoding='latin-1', error_bad_lines=False)
    df = filter_by_interest(df, interest)
    df = filter_by_topic(df, keywords, stopwords)
    dfRT = df[['Usuario', 'Texto', 'Fecha']].copy()
    dfRT = dfRT.dropna()
    dfRT = dfRT[dfRT['Fecha'].str.match('[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]\s[0-9]')]
    idx = dfRT['Texto'].str.contains('RT @', na=False)
    dfRT = dfRT[idx]
    return dfRT

#Función para extraer los días:
def getDays(df):
    df = df['Fecha']
    days = pd.unique(df)
    days.sort()
    return days

# Función para graficar uso de hashtags en el tiempo:

def plottemporalserie(days, df, elements, title):
    numHashtag = []
    for hashtag in elements[:5]:
        numPerDay = []
        for day in days:
            dfOneDay = df[df['Fecha'] == day]
            count = dfOneDay['Texto'].str.contains(hashtag, case=False).sum()
            numPerDay.append(count)
        numHashtag.append(numPerDay)

    sns.reset_orig()
    fig = plt.figure(figsize=(9, 6))

    colours = ["red", "blue", "green", "orange", "magenta"]

    i = 0
    for hashtag in elements[:5]:
        plt.plot_date(days, numHashtag[i], colours[i], label=hashtag)
        i += 1

        # Se fija el titulo y etiquetas
    plt.title(title, fontsize=20, fontweight='bold')
    plt.xlabel("Fecha", fontsize=15)
    plt.ylabel("Número de veces", fontsize=15)
    plt.xticks(rotation=45)
    plt.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", borderaxespad=0)

    fig.autofmt_xdate()
    plt.show()


def sentiment_analyser(df_entry,keywords=None, stopwords=None, keywords2=None, stopwords2=None, interest=None):
    analyser = SentimentIntensityAnalyzer()
    df = filter_by_interest(df_entry, interest)
    df = filter_by_topic(df, keywords, stopwords)
    df = df[['Texto', 'Usuario']]
    df = df.dropna()
    Users = df['Usuario']
    Texto = df['Texto']
    sentences = Texto
    list_of_dicts = []
    for sentence in sentences:
        adict = analyser.polarity_scores(sentence)
        print(adict)
        list_of_dicts.append(adict)
    df_sentiment = pd.DataFrame(list_of_dicts)
    df_sentiment['Usuario'] = Users
    df_sentiment['Texto'] = Texto
    return df_sentiment
start_time = time.time()

