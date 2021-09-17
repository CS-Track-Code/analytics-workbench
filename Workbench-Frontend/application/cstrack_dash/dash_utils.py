"""  This module is used mainly to generate Dash components, such as filters or figures.
It also provides some extra functionality to anonymize usernames and accessing data located in a database.

"""


import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
import re
import networkx as nx
import pymongo
import plotly.graph_objects as go
import networkit as nk
import hashlib
from collections import Counter
from datetime import date
from functools import lru_cache

try:
    import generate_utils as utils
    import config
except ModuleNotFoundError:
    import application.cstrack_dash.generate_utils as utils
    import application.cstrack_dash.config as config


def get_hash_name_list(nodes):
    """Function to anonymize a list of users.

    :param nodes: list with the user names
    :return: list with the user names anonymized
    """
    dict_names = {}
    for node in nodes:
        dict_names[node] = hashlib.md5(str(node).encode()).hexdigest()

    return dict_names


def get_community_graph(g, communities, i=0):
    """
    Function to create a graph given a list of users (communities) that are connected.

    :param g: The graph that contains the information of the whole network
    :param communities: A list of communities. Each community contains a list of user names
    :param i: The community for which we want to create a graph
    :return: The graph that represents the requested community
    """
    c = nx.DiGraph()
    for node in communities[i]:
        list_edges = g.edges(node)
        list_edges = [edge for edge in list_edges if edge[1] in communities[i]]
        c.add_edges_from(list_edges)
    dict_names = get_hash_name_list(c.nodes)
    #c = nx.relabel_nodes(c, dict_names)
    return c

def get_communities(g, algorithm="louvain"):
    """
    Function to calculate the communities of a given network.

    :param g: Graph that represents the network
    :param algorithm: The algorithm to create the communities (louvain or propagation)
    :return: A list of communities. Each community is represented as a list of user names
    """
    n_g = nk.nxadapter.nx2nk(g)
    idmap = dict((u, id) for (id, u) in zip(g.nodes(), range(g.number_of_nodes())))
    if algorithm == "louvain":
        communities = nk.community.detectCommunities(n_g)
    else:
        communities = nk.community.detectCommunities(n_g, algo=nk.community.PLP(n_g))
    list_communities = []
    for i in range(0, communities.numberOfSubsets()):
        list_members = []
        for member in communities.getMembers(i):
            list_members.append(idmap[member])
        if len(list_members) > 5:
            list_communities.append(list_members)
    list_communities = [community for community in list_communities if len(community) > 10]
    return list_communities

def kcore_graph(df, keywords=None, stopwords=None, interest=None, anonymize=False):
    """
    Given a dataframe with tweets, users... creates a graph of retweets.

    :param df: The dataframe containing the information
    :param keywords: A list of words to get the tweets that contain those words
    :param stopwords: A list of words to remove tweets that contain those words
    :param interest: The interest (Lynguo filter)
    :param anonymize: False if we want to get the user names and false if we want to anonymize them
    :return: The graph
    """
    df = utils.filter_by_interest(df, interest)
    df = utils.filter_by_topic(df, keywords, stopwords)
    dfRT = df[['Usuario', 'Texto']]
    idx = dfRT['Texto'].str.contains('RT @', na=False)
    dfRT = dfRT[idx]
    rt_edges_list = [list(x) for x in dfRT.to_numpy()]

    edges = []
    for row in rt_edges_list:
        reg = re.search('@(\w+)', row[1])
        if reg:
            matchRT = reg.group(1)
            row[1] = matchRT
            #row[1] = hashlib.md5(matchRT.encode()).hexdigest()
            edges.append(row)

    G = utils.make_weightedDiGraph(edges)
    G.remove_edges_from(nx.selfloop_edges(G))
    core_number = nx.core_number(G)
    values = list(core_number.values())
    degree_count = Counter(values)
    G_kcore = nx.k_core(G, k=2)
    if anonymize:
        dict_labels = get_hash_name_list(G_kcore.nodes)
        G_kcore = nx.relabel_nodes(G_kcore, mapping=dict_labels)
    print(len(G_kcore.nodes))
    """G_kcore_undirected = nx.to_undirected(G_kcore)
    subgraphs = utils.get_subgraphs(G_kcore_undirected)
    subgraphs = [graph for graph in subgraphs if len(graph.nodes) > 5]
    subgraphs = utils.direct_subgraphs(subgraphs)"""

    return G_kcore


def get_single_counts(df):
    """
    Given a dataframe with the columns Date and Number it counts the increment (Tweets and Follows). For instance,
    having 10-03-2021, 11-03-2021 as Dates and 10, 12 as counts it will return (10-03-2021, 10; 11-03-2021, 2).

    :param df: A dataframe that must have the columns Date and Number
    :return: A dataframe counting the increments
    """
    base_count = df.iloc[0]["Number"]
    result = []
    for i, data in df.iterrows():
        count = data["Number"] - base_count
        base_count = data["Number"]
        result.append({"Date": data["Date"], "Number": count})
    return pd.DataFrame(result)


def acumulate_retweets(df):
    """
    Given a dataframe with the columns Number and Date it accumulates the number (Counting total retweets).

    :param df: A dataframe with the columns Date and Number
    :return: A dataframe with the accumulated result per date.
    """
    base_count = df.iloc[0]["Number"]
    result = []
    for i, data in df.iterrows():
        count = data["Number"] + base_count
        base_count = count
        result.append({"Date": data["Date"], "Number": count})
    return pd.DataFrame(result)


def get_figure(df):
    """
    Given a dataframe where the appearance of each hashtag is counted, it creates a barplot to represent the results.

    :param df: A dataframe with the columns Hashtags and Count
    :return: A barplot representing the dataframe
    """
    fig = px.bar(df, x="Hashtags", y="Count", barmode="group")
    fig.update_xaxes(tickangle=90)
    return fig


def get_temporal_figure(df, n_hashtags=5):
    """
    Given a dataframe that contains the number of appearances of each hashtag in each day it creates a time series
    figure to represent the results.

    :param df: A dataframe with the name of the hastags, the date, and the number of appearances
    :param n_hashtags: The number of hashtags that are wanted to be shown
    :return: A time series figure representing the dataframe
    """
    fig = px.line(df, x='date', y=df.columns[:n_hashtags])
    fig.update_layout(xaxis_tick0=df['date'][0], xaxis_dtick=86400000 * 15)
    return fig


def get_cstrack_graph(df, type, title):
    """
    A function to create the different graphs for the cstrackproject twitter account.

    :param df: A dataframe with the data
    :param type: The type of graph that is wanted to be drawn (Retweets, Tweets, Followers)
    :param title: The title of the graph
    :return: A figure representing the results according to the given parameters.
    """
    df_retweets = df[df["Type"] == type]
    if type == "Retweets":
        df_retweets = df_retweets.groupby(["Date"], as_index=False)["Number"].sum()
        df_retweets["Date"] = pd.to_datetime(df_retweets['Date'], format="%d/%m/%Y")
        df_retweets = df_retweets.sort_values(by="Date")
        df_accumulated = acumulate_retweets(df_retweets)
        fig = px.line(df_accumulated, x="Date", y="Number", title=title)
        fig.add_trace(go.Scatter(x=df_retweets["Date"].tolist(), y=df_accumulated["Number"].tolist(),
                                 mode="markers", textposition="top center", name="Retweets per day",
                                 text=df_retweets["Number"].tolist()))
    elif type == "Tweets":
        print(df_retweets.dtypes)
        df_retweets["Date"] = pd.to_datetime(df_retweets['Date'], format="%d/%m/%Y").dt.date
        df_retweets = df_retweets.sort_values(by="Date")
        df_retweets = get_single_counts(df_retweets.drop_duplicates(subset=["Date"])).iloc[1:]
        fig = px.line(df_retweets, x="Date", y="Number", title=title)
    if type == "Followers":
        single_follow_count = get_single_counts(df_retweets)
        fig = px.line(df_retweets, x="Date", y="Number", title=title)
        fig.add_trace(go.Scatter(x=df_retweets["Date"].tolist(), y=df_retweets["Number"].tolist(),
                                 mode="markers+text", textposition="top center", name="New followers",
                                 text=single_follow_count["Number"].tolist()))

    return fig


def get_df_ts(df, days, hashtags):
    """
    Given a DataFrame, a list of days and a list of hashtags it returns a Dataframe with the appearance of each hashtag
    each day

    :param df: Input Dataframe
    :param days: A list of dates
    :param elements: A list of hashtags
    :return: DataFrame with the count for each hashtag each day
    """
    numHashtag = []
    for hashtag in hashtags[:100]:
        numPerDay = []
        for day in days:
            dfOneDay = df[df['Fecha'] == day]
            count = dfOneDay['Texto'].str.contains(hashtag, case=False).sum()
            numPerDay.append(count)
        numHashtag.append(numPerDay)
    ts_df = pd.DataFrame()
    for i in range(0, len(numHashtag)):
        ts_df[hashtags[i]] = numHashtag[i]
    ts_df = ts_df.assign(date=days)
    return ts_df


def get_rt_hashtags(df, keywords=None, stopwords=None, n_hashtags=10):
    """
    Given a DataFrame with Tweets it returns a DataFrame with the Hashtags and the number of times (Count) they have
    been retweeted

    :param df: A DataFrame with all the tweets
    :param keywords: A list of words to filter the tweets
    :param stopwords:  A list of words to filter the tweets
    :param n_hashtags:  Number of hashtags to get
    :return: A DataFrame counting the hashtags and the number of times they have been retweeted
    """
    listHashtagsRT2 = utils.get_hashtagsRT(df, keywords=keywords, stopwords=stopwords)
    edges = utils.get_edgesHashRT(listHashtagsRT2)
    # Con las stopwords eliminamos el bot:
    sortedNumberHashtags, sortedHashtagsmain = utils.prepare_hashtags(edges)
    df_hashtags = pd.DataFrame(list(zip(sortedHashtagsmain, sortedNumberHashtags)), columns=["Hashtags", "Count"])
    return df_hashtags


def get_all_hashtags(df, keywords=None, stopwords=None):
    """
    Given a DataFrame with Tweets it returns a DataFrame with the Hashtags and the number of times (Count) they appear.

    :param df: A DataFrame with all the tweets
    :param keywords: A list of words to filter the tweets
    :param stopwords:  A list of words to filter the tweets
    :return: A DataFrame counting the hashtags and the number of times they have appeared.
    """
    hashmain = utils.get_hashtagsmain(df, keywords=keywords, stopwords=stopwords)
    edges = utils.get_edgesMain(hashmain)
    # Con las stopwords eliminamos el bot:
    sortedNumberHashtags, sortedHashtagsmain = utils.prepare_hashtagsmain(edges, stopwords=stopwords)
    df_hashtags = pd.DataFrame(list(zip(sortedHashtagsmain, sortedNumberHashtags)), columns=["Hashtags", "Count"])
    return df_hashtags


def get_all_temporalseries(df, keywords=None):
    """
    Given a DataFrame containing all the tweets the function returns a DataFrame with the hashtags and dates, a list
    of dates and the hashtags sorted by number of appearances

    :param df: DataFrame with all the tweets
    :param keywords: Keywords to filter the DataFrame
    :return: DataFrame with hastags and dates, a list of days and hashtags sorted by appearance
    """
    df = df[['Usuario', 'Texto', 'Fecha']].copy()
    df = df.dropna()
    df = df[df['Fecha'].str.match('[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]\s[0-9][0-9]:[0-9][0-9]:[0-9][0-9]')]
    df["Fecha"] = pd.to_datetime(df['Fecha'], format="%Y-%m-%d %H:%M:%S").dt.date
    days = utils.getDays(df)
    listHt = utils.get_hashtagsmain(df, keywords=keywords)
    edges = utils.get_edgesMain(listHt)
    sortedNH, sortedMH = utils.prepare_hashtagsmain(edges)
    return df, days, sortedMH


def get_rt_temporalseries(df, keywords=None):
    """
    Given a DataFrame containing all the tweets the function returns a DataFrame with the retweeted hashtags and dates, a list
    of dates and the hashtags sorted by number of appearances

    :param df: DataFrame with all the tweets
    :param k: Keywords to filter the DataFrame
    :return: DataFrame with hashtags and dates, a list of days and hashtags sorted by appearance
    """
    df = df[['Usuario', 'Texto', 'Fecha']].copy()
    df = df.dropna()
    df = df[df['Fecha'].str.match('[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]\s[0-9][0-9]:[0-9][0-9]:[0-9][0-9]')]
    df["Fecha"] = pd.to_datetime(df['Fecha'], format="%Y-%m-%d %H:%M:%S").dt.date
    dias = utils.getDays(df)
    listHt = utils.get_hashtagsRT(df, keywords=keywords)
    edges = utils.get_edgesHashRT(listHt)
    sortedNH, sortedMH = utils.prepare_hashtags(edges)
    return df, dias, sortedMH


def wordcloudmain(df, save_url="./assets/"):
    """
    Given a DataFrame with all the tweets the function creates a Wordcloud with the words that appear the most.

    :param df:  A DataFrame with all the tweets
    :param keywords: A  list of words to filter the DataFrame
    :param stopwords: A list of words to filter the DataFrame
    :param interest: The interest to filter the DataFrame (Lynguo)
    """
    hashtags = []
    stop_words = ['citizenscience', 'rt', 'citizen', 'science', 'citsci', 'cienciaciudadana', 'CitizenScience']
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
    wordcloud = WordCloud(width=900, height=600, background_color='white', stopwords=stop_words,
                          min_font_size=10, max_words=10405, collocations=False, colormap='winter').generate(
        unique_string)
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(save_url + "wc2.png")


def get_graph_rt(df):
    """
    Given a Dataframe with Tweets and users it creates a Graph of retweets

    :param df: A Dataframe containing the tweets and users
    :return: A graph representing the network of retweets
    """
    retweetList = utils.get_retweets(df)
    retweetEdges = utils.get_edges(retweetList)
    G = nx.Graph()
    G.add_edges_from(retweetEdges)
    return G


def get_degrees(df):
    """
    Given a DataFrame with tweets and users it calculates different centrality measures.

    :param df: A DataFrame with tweets and users
    :return: A Dataframe with the centrality measures of the users
    """
    from operator import itemgetter
    import datetime
    start = datetime.datetime.now()
    retweetList = utils.get_retweets(df)
    retweetEdges = utils.get_edges(retweetList)
    G = nx.DiGraph()
    G.add_edges_from(retweetEdges)
    print("FINALIZA,", datetime.datetime.now() - start)
    return utils.get_degrees(G)


def get_twitter_info_df():
    """
    A function to return the cstrackproject Twitter user stats

    :return: A Dataframe with information about followers, retweets and tweets
    """
    db = pymongo.MongoClient(host=config.MONGODB_CONNECTION, port=21000)
    twitter_data = db["cstrack"]["cstrack_stats"]
    twitter_dict_list = list(twitter_data.find())
    df = pd.DataFrame(twitter_dict_list)
    df = df.dropna()
    df["Date"] = pd.to_datetime(df['Date'], format="%d/%m/%Y %H:%M", errors="ignore")
    df["Date"] = pd.to_datetime(df['Date'], format="%d/%m/%Y", errors="ignore")
    return df

def get_two_mode_graph(df, keywords=None):
    """
    Given a DataFrame containing all the tweets the function returns a two-mode graph connecting users with tweets

    :param df:  A DataFrame with all the information
    :param keywords: A list of words to filter the DataFrame
    :return: A two-mode graph connecting users with tweets
    """
    return utils.get_twomodeRT(df, keywords)

def get_controls_community2(communities):
    """
    Given a list of communities, being each community a list of users, the function creates the filtering options for
    the Dash visualization.

    :param communities: A list of communities, being each community a list of usernames
    :return: The filtering options for the Dash visualization.
    """
    dropdown_options = []
    dropdown_options.append({"label": "all", "value": "all"})
    for i in range(0, len(communities)):
        dropdown_options.append({"label": str(i), "value": i})

    controls = dbc.Form(
        [
            dbc.FormGroup(
                [
                    dbc.Label("Community:"),
                    dcc.Dropdown(
                        id="com_number2",
                        options=dropdown_options,
                        value="all",
                        clearable=False,
                        style = {"margin-left": "2px"}
                    )
                ],
                className="mr-3",
            ),
            dbc.FormGroup(
                [
                    dbc.Label("Algorithm:"),
                    dcc.Dropdown(
                        id="com_algorithm2",
                        options=[{"label": "Louvain", "value": "louvain"}, {"label": "Label propagation", "value": "propagation"}],
                        value="louvain",
                        clearable=False,
                        style={"width": "200px", "margin-left": "2px"}
                    )
                ],
            ),
        ],
        inline=True
    )
    return controls

def get_controls_activity():
    """
    Function to create the filtering options for the Geomap visualizations in Dash

    :return: The filtering options for the Geomap visualizations.
    """
    controls = dbc.Form(
        [
            dbc.FormGroup(
                [
                    dbc.Label("Activity:"),
                    dcc.Dropdown(
                        id="activity_type",
                        options=[{"label": "Tweets", "value": "tweets"}, {"label": "Followers", "value": "followers"}],
                        value="tweets",
                        clearable=False,
                        style={"width": "200px", "margin-left": "2px"}
                    )
                ],
            ),
        ],
        inline=True
    )
    return controls

def get_controls_rt(number_id, keyword_id):
    """
    Given two ids, the function creates the filtering options for several Dash Visualizations

    :param number_id: Id for the number input
    :param keyword_id: Id for the text input
    :return: The filtering options for the Dash visualization.
    """
    today = date.today()

    controls = dbc.Form(
        [
            dbc.Row([
                dbc.Col(
                    dbc.FormGroup(
                        [
                            dbc.Label("Number hashtags:"),
                            dbc.Input(id=number_id, style={"width": "100px"}, n_submit=0, min=1,
                                      type="number", value=10, debounce=True),
                        ]
                    ), md=4),
                dbc.Col(
                    dbc.FormGroup(
                        [
                            dbc.Label("Keywords:"),
                            dbc.Input(id=keyword_id, n_submit=0, type="text", value="", debounce=True),
                        ],
                    )),
                dbc.Col(
                    dbc.FormGroup(
                        [
                            dbc.Label("Keywords:"),
                            get_topic_file(keyword_id + "-upload")
                        ],
                    ))
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.FormGroup(
                        [
                            dbc.Label("Dates:"),
                            dcc.DatePickerRange(
                                id='sessions_date',
                                min_date_allowed=(2020, 9, 29),
                                max_date_allowed=(today.year, today.month, today.day),
                                display_format="DD-MM-Y",
                                clearable=True
                            ),
                        ]
                    ),
                ])
            ])
        ],
    )
    return controls

def get_controls_rt_g(keyword_id):
    """
    Given and id it creates the filtering options for the graph of retweets in Dash

    :param keyword_id: Id of the text input
    :return: The filtering options for the graph of retweets
    """
    controls = dbc.Form(
        [
            dbc.FormGroup(
                [
                    dbc.Label("Keywords:"),
                    dbc.Input(id=keyword_id, n_submit=0, type="text", value="", debounce=True),
                ],
                className="mr-3"
            ),
            dbc.FormGroup(
                [
                    dbc.Label("Topics:"),
                    get_topic_file(keyword_id + "-upload")
                ],
            ),
        ],
        inline=True
    )
    return controls

def get_topic_file(id):
    """
    Given an id it creates a dropbox to upload a file containing keywords (One keyword in each line)

    :param id: The id of the button
    :return: The button to upload a file
    """
    upload_html = dcc.Upload(
        id=id,
        children=html.Div([
            'Upload ',
            html.A('File')
        ]),
        style={
            'width': '100%',
            'height': "calc(1.5em + .75rem + 2px)",
            'lineHeight': '35px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
        },
        # Allow multiple files to be uploaded
    )
    return upload_html

def get_controls_ts(number_id, keyword_id, dc_id, df_ts):
    """
    Given the ids for the different inputs, it creates the different filters for the time series visualization

    :param number_id: Id for the number input (Number of hashtags to show)
    :param keyword_id: Id for the list of keywords
    :param dc_id: Id for the dropdown options (Search specific hashtags to show)
    :param df_ts: The DataFrame with the hashtag count
    :return:
    """
    options = []
    for c in df_ts.columns[:-1]:
        options.append({"label": c, "value": c})

    today = date.today()

    controls = dbc.Form(
        [
            dbc.Row([
                dbc.Col(
                    dbc.FormGroup(
                        [
                            dbc.Label("Number hashtags:"),
                            dbc.Input(id=number_id, style={"width": "100px"}, n_submit=0, min=1, type="number", value=5, debounce=True),
                        ]
                    ), md=4),
                dbc.Col(
                    dbc.FormGroup(
                        [
                            dbc.Label("Keywords:"),
                            dbc.Input(id=keyword_id, n_submit=0, type="text", value="", debounce=True),
                        ],
                    )),
                dbc.Col(
                    dbc.FormGroup(
                        [
                            dbc.Label("Keywords:"),
                            get_topic_file(dc_id + "-upload")
                        ],
                    ))
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.FormGroup(
                        [
                            dbc.Label("Dates:"),
                            dcc.DatePickerRange(
                                id='sessions_date',
                                min_date_allowed=(2020, 9, 29),
                                display_format="DD-MM-Y",
                                max_date_allowed=(today.year, today.month, today.day),
                                clearable=True
                            ),
                        ]
                    ),
                ]),
                dbc.Col(
                    dbc.FormGroup(
                        [
                            dbc.Label("Hashtags:"),
                            dcc.Dropdown(id=dc_id, options=options, multi=True, style={"width": "200px"}),
                        ],
                    ))
            ])
        ]
    )
    return controls




def set_loading(controls, dcc_graph):
    """
    Function to create a loading effect when filtering a graph

    :param controls: The filters
    :param dcc_graph: The figure that is being updated
    :return: The element to embed the figure in in order to apply the loading effect
    """
    SPINER_STYLE = {
        "margin-top": "25%",
        "width": "99%",
        "height": "20vh",
        "text-align": "center",
        "font-size": "50px",
        "margin-left": "1%",
        "z-index": "1000"
    }
    loading = dcc.Loading(
        # style={"height":"200px","font-size":"100px","margin-top":"500px", "z-index":"1000000"},
        style=SPINER_STYLE,
        color="#000000",
        id="loading-1",
        type="default",
        children=html.Div(id="loading-output", children=[
            dbc.Row(controls, justify="center"),
            dbc.Row(
                children=[dcc_graph], justify="center"
            )
        ])
    ),
    return loading

def get_map_df():
    """
    Function to get the information to create geomap visualizations

    :return: A DataFrame with geographical information
    """
    con = pymongo.MongoClient(config.MONGODB_CONNECTION, port=21000)
    col = con["cstrack"]["geomap_full"]
    info = pd.DataFrame(list(col.find()))
    return info

def get_controls_topics(number_id, keyword_id, topics):
    """
    Function to create the filtering options for the topic modelling visualization

    :param number_id: The id for the number input (Number of topics to create)
    :param keyword_id: The id for the text input (List of words to filter the dataframe)
    :param topics: The number of topics.
    :return:
    """
    today = date.today()

    controls = dbc.Form(
        [
            dbc.Row([
                dbc.Col(
                    dbc.FormGroup(
                        [
                            dbc.Label("Number topics:"),
                            dbc.Input(id=number_id, style={"width": "100px"}, n_submit=0, min=1, max=topics, type="number", value=20, debounce=True),
                        ]
                    ), md=4),
                dbc.Col(
                    dbc.FormGroup(
                        [
                            dbc.Label("Keywords:"),
                            dbc.Input(id=keyword_id, n_submit=0, type="text", value="", debounce=True),
                        ],
                    )),
                dbc.Col(
                    dbc.FormGroup(
                        [
                            dbc.Label("Topics:"),
                            get_topic_file(keyword_id + "-upload")
                        ],
                    ))
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.FormGroup(
                        [
                            dbc.Label("Dates:"),
                            dcc.DatePickerRange(
                                id='sessions_date',
                                min_date_allowed=(2020, 9, 29),
                                display_format="DD-MM-Y",
                                max_date_allowed=(today.year, today.month, today.day),
                                clearable=True
                            ),
                        ]
                    ),
                ])
            ])
        ],
    )
    return controls

def toast_info(title, text):
    return dbc.Toast(
        [html.P(text, className="mb-0")],
        id="simple-toast",
        header=title,
        icon="primary",
        dismissable=True,
    ),