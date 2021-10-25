import base64
import dash
import pandas as pd
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from flask import Flask, request, url_for, redirect, render_template
from webweb import Web
import hashlib
import datetime

com_algorithm = "louvain"
communities = None
com = None

try:
    import berttopic_utils as bt
    import submenus
    import dash_utils
    import communities_utils as cu
    from generate_utils import filter_by_topic
    import map_utils as mu
    import config
    import generate_utils as gu
    import style

except ModuleNotFoundError:
    import application.cstrack_dash.berttopic_utils as bt
    import application.cstrack_dash.submenus as submenus
    import application.cstrack_dash.dash_utils as dash_utils
    import application.cstrack_dash.communities_utils as cu
    from application.cstrack_dash.generate_utils import filter_by_topic
    import application.cstrack_dash.map_utils as mu
    import application.cstrack_dash.config as config
    import application.cstrack_dash.generate_utils as gu
    import application.cstrack_dash.style as style


def create_dashboard(server=None):
    global communities
    global com

    if server:
        base_string = "/dashapp"
    else:
        base_string = ""

    df_map = dash_utils.get_map_df()
    df = pd.read_csv(config.TWEET_DATASET, sep=';', encoding='latin-1', error_bad_lines=False)
    df = df.drop_duplicates(subset=['Texto', 'Usuario'], keep="last").reset_index(drop=True)
    documents = bt.get_cleaned_documents(df)
    bert_model = bt.load_model(config.BERT_MODEL)
    bert_topics = bt.load_topics(config.BERT_TOPICS)
    df_all_h = dash_utils.get_all_hashtags(df)
    df_rt_h = dash_utils.get_rt_hashtags(df)
    df_cstrack = dash_utils.get_twitter_info_df()
    df_ts_raw, days, sortedMH = dash_utils.get_all_temporalseries(df)
    df_ts = dash_utils.get_df_ts(df_ts_raw, days, sortedMH)
    df_ts_rt_raw, days_rt, sortedMH_rt = dash_utils.get_rt_temporalseries(df)
    df_ts_rt = dash_utils.get_df_ts(df_ts_rt_raw, days_rt, sortedMH_rt)
    """wc_main = dash_utils.wordcloudmain(df, config.WC_URL)
    df_deg = dash_utils.get_degrees(df)
    df_sentiment = gu.sentiment_analyser((df))
    df_deg.to_csv("dashdeg.csv")

    G = dash_utils.get_graph_rt(df)
    communities = dash_utils.get_communities(G)
    com = dash_utils.get_community_graph(G, communities)
    graph_communities = []

    for i in range(0, len(communities)):
        graph_communities.append(dash_utils.get_community_graph(G, communities, i))

    g_communities = cu.get_communities_representative_graph(G, communities)
    kcore_g = dash_utils.kcore_graph(df=df)
    two_mode_g = dash_utils.get_two_mode_graph(df)"""

    submenu_1, submenu_2, submenu_3, submenu_4, submenu_5, submenu_6, submenu_7 = submenus.create_submenus(base_string)
    # link fontawesome to get the chevron icons
    FA = "https://use.fontawesome.com/releases/v5.8.1/css/all.css"
    if not server is None:
        app = dash.Dash(server=server, routes_pathname_prefix="/dashapp/",external_stylesheets=[dbc.themes.BOOTSTRAP, FA])
    else:
        app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, FA])
    app.config.suppress_callback_exceptions = True
    if server:
        logo = "/static/dash/cstrack_logo.png"
    else:
        logo = app.get_asset_url("cstrack_logo.png")
    sidebar = html.Div(
        [
            html.A('Back to Workbench', href=url_for("home_bp.startpage")),
            html.Hr(),
            dbc.Col(html.Img(src=logo, height='50px')),
            html.Hr(),
            html.P('Available graphs', className='lead'),
            dbc.Nav(
                [dbc.NavLink('CS-Track stats', href='/dashapp/cstrack',
                                 active='exact')
                 ] + submenu_1 + submenu_2 + submenu_3 + submenu_4 + submenu_5 + submenu_6 + submenu_7,
                    vertical=True, pills=True),
        ]

        ,
        style=style.SIDEBAR_STYLE,
        id='sidebar',
    )

    content = html.Div(id="page-content", style=style.CONTENT_STYLE)

    app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


    # this function is used to toggle the is_open property of each Collapse
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open


    # this function applies the "open" class to rotate the chevron
    def set_navitem_class(is_open):
        if is_open:
            return "fas fa-chevron-down mr-3"
        return "fas fa-chevron-right mr-3"


    for i in range(1, 8):
        app.callback(
            Output(f"submenu-{i}-collapse", "is_open"),
            [Input(f"submenu-{i}", "n_clicks")],
            [State(f"submenu-{i}-collapse", "is_open")],
        )(toggle_collapse)

        app.callback(
            Output(f"chevron-{i}", "className"),
            [Input(f"submenu-{i}-collapse", "is_open")],
        )(set_navitem_class)
        
    @app.callback(Output("page-content", "children"), [Input("url", "pathname")])
    def render_page_content(pathname):
        if pathname == (base_string + "/") or pathname == (base_string + "/cstrack"):
            html_plot = html.Div(children=[

                dcc.Loading(
                    # style={"height":"200px","font-size":"100px","margin-top":"500px", "z-index":"1000000"},
                    style=style.SPINER_STYLE,
                    color="#000000",
                    id="loading-1",
                    type="default",
                    children=html.Div(id="loading-output", children=[
                        dbc.Row(dash_utils.toast_info("CS-Track Twitter Stats",
                                                      "In this graph you can see the number of followers, the number of retweets and the number"
                                                      "of tweets of the @cstrackproject Twitter user account."),
                                justify="center"),
                        dbc.Row(
                            dbc.Col(dcc.Graph(id='graph_retweets',
                                              figure=dash_utils.get_cstrack_graph(df_cstrack, "Retweets",
                                                                                  "Retweets received")), md=8),
                            justify="center"),
                        dbc.Row(
                            dbc.Col(dcc.Graph(id='graph_followers',
                                              figure=dash_utils.get_cstrack_graph(df_cstrack, "Followers",
                                                                                  "Followers")),
                                    md=8),
                            justify="center"),
                        dbc.Row(
                            dbc.Col(dcc.Graph(id='graph_followers',
                                              figure=dash_utils.get_cstrack_graph(df_cstrack, "Tweets",
                                                                                  "Number of Tweets")),
                                    md=8),
                            justify="center")
                    ])
                ),
            ]),
            return html_plot
        elif pathname == (base_string + "/hashtags/all"):
            controls = dash_utils.get_controls_rt("input-key-all", "hashtag-number-all")
            """graph_fig = dbc.Col(dcc.Graph(id='graph_all_hashtags', figure=dash_utils.get_figure(df_all_h[0:10])), md=8)
            graph = dash_utils.set_loading(controls, graph_fig)"""
            html_plot = html.Div(children=[
                dcc.Loading(
                    # style={"height":"200px","font-size":"100px","margin-top":"500px", "z-index":"1000000"},
                    style=style.SPINER_STYLE,
                    color="#000000",
                    id="loading-1",
                    type="default",
                    children=html.Div(id="loading-output", children=[
                        dbc.Row(dash_utils.toast_info("All hashtags barchart",
                                                      "In this graph you can see how many times a hashtag has been used. You can choose the number of hashtags"
                                                      "to show, you can filter the tweets by using keywords (words separated by commas), you can upload a file with"
                                                      "keywords (one word in each line) and you can filter tweets by date"),
                                justify="center"),
                        dbc.Row(controls, justify="center"),
                        dbc.Row(
                            dbc.Col(dcc.Graph(id='graph_all_hashtags', figure=dash_utils.get_figure(df_all_h[0:10])),
                                    md=8),
                            justify="center")
                    ])
                ),
            ]),

            return html_plot
        elif pathname == (base_string + "/hashtags/rt"):
            controls = dash_utils.get_controls_rt("input-key-rt", "hashtag-number-rt")
            html_plot = html.Div(children=[
                dcc.Loading(
                    # style={"height":"200px","font-size":"100px","margin-top":"500px", "z-index":"1000000"},
                    style=style.SPINER_STYLE,
                    color="#000000",
                    id="loading-1",
                    type="default",
                    children=html.Div(id="loading-output", children=[
                        dbc.Row(dash_utils.toast_info("Retweeted hashtags barchart",
                                                      "In this graph you can see how many times a hashtag has been retweeted. You can choose the number of hashtags"
                                                      "to show, you can filter the tweets by using keywords (words separated by commas), you can upload a file with"
                                                      "keywords (one word in each line) and you can filter tweets by date"),
                                justify="center"),
                        dbc.Row(controls, justify="center"),
                        dbc.Row(
                            dbc.Col(dcc.Graph(id='graph_rt_hashtags', figure=dash_utils.get_figure(df_rt_h[0:10])),
                                    md=8),
                            justify="center")
                    ])
                ),

            ]),
            return html_plot
        elif pathname == (base_string + "/timeseries/allhashtags"):
            controls = dash_utils.get_controls_ts("input-key-ts-all", "hashtag-number-ts-all", "hashtags-name-ts-all",
                                                  df_ts)
            html_plot = html.Div(children=[
                dcc.Loading(
                    # style={"height":"200px","font-size":"100px","margin-top":"500px", "z-index":"1000000"},
                    style=style.SPINER_STYLE,
                    color="#000000",
                    id="loading-1",
                    type="default",
                    children=html.Div(id="loading-output", children=[
                        dbc.Row(dash_utils.toast_info("All hashtags time series",
                                                      "In this graph you can see the evolution of hashtags mentions. You can choose the number of hashtags"
                                                      "to show, you can filter the tweets by using keywords (words separated by commas), you can upload a file with"
                                                      "keywords (one word in each line) and you can filter tweets by date. You can also select the specific hashtags that you "
                                                      "want to look at."),
                                justify="center"),
                        dbc.Row(controls, justify="center"),
                        dbc.Row(
                            dbc.Col(dcc.Graph(id='graph_ts_all_hashtags', figure=dash_utils.get_temporal_figure(df_ts)),
                                    md=8), justify="center"),
                    ])
                ),
            ]),
            return html_plot

        elif pathname == (base_string + "/wordcloud"):
            html_plot = html.Div(children=[
                dcc.Loading(
                    # style={"height":"200px","font-size":"100px","margin-top":"500px", "z-index":"1000000"},
                    style=style.SPINER_STYLE,
                    color="#000000",
                    id="loading-1",
                    type="default",
                    children=html.Div(id="loading-output", children=[
                        dbc.Row(dash_utils.toast_info("Wordcloud",
                                                      "In this graph you can see the words that have been most used in the tweets."),
                                justify="center"),
                        dbc.Row(dbc.Col(html.Img(src=config.ASSETS_URL + 'wc2.png')), justify="center"),
                    ])
                ),
            ]),
            return html_plot
        elif pathname == (base_string + "/timeseries/rthashtags"):
            controls = dash_utils.get_controls_ts("input-key-ts-rt", "hashtag-number-ts-rt", "hashtags-name-ts-rt",
                                                  df_ts_rt)
            html_plot = html.Div(children=[
                dcc.Loading(
                    # style={"height":"200px","font-size":"100px","margin-top":"500px", "z-index":"1000000"},
                    style=style.SPINER_STYLE,
                    color="#000000",
                    id="loading-1",
                    type="default",
                    children=html.Div(id="loading-output", children=[
                        dbc.Row(dash_utils.toast_info("Retweeted hashtags time series",
                                                      "In this graph you can see the evolution of hashtags that have been retweeted. You can choose the number of hashtags"
                                                      "to show, you can filter the tweets by using keywords (words separated by commas), you can upload a file with"
                                                      "keywords (one word in each line) and you can filter tweets by date. You can also select the specific hashtags that you "
                                                      "want to look at."),
                                justify="center"),
                        dbc.Row(controls, justify="center"),
                        dbc.Row(
                            dbc.Col(
                                dcc.Graph(id='graph_ts_rt_hashtags', figure=dash_utils.get_temporal_figure(df_ts_rt)),
                                md=8), justify="center"),
                    ])
                ),
            ]),
            return html_plot

        elif pathname == (base_string + "/tables/retweets"):
            list_names = [hashlib.md5(str(name).encode()).hexdigest() for name in df_deg["Name"].tolist()]
            new_deg = df_deg.copy()
            del new_deg["Name"]
            new_deg.insert(0, "Name", list_names, True)
            html_plot = html.Div(children=[
                dcc.Loading(
                    # style={"height":"200px","font-size":"100px","margin-top":"500px", "z-index":"1000000"},
                    style=style.SPINER_STYLE,
                    color="#000000",
                    id="loading-1",
                    type="default",
                    children=html.Div(id="loading-output", children=[
                        dbc.Row(dash_utils.toast_info("Degrees table",
                                                      "In this table you can see different graph metrics to analyse the most 'popular' users.  The indegree represents"
                                                      "the number of times a user has been retweeted, the out degree represents the number of times a user has retweeted someone"
                                                      "and then you also have different centrality measures."),
                                justify="center"),
                        dbc.Row(dbc.Col(

                            dash_table.DataTable(
                                id='datatable-interactivity',
                                columns=[
                                    {"name": i, "id": i, "deletable": True, "selectable": True, "hideable": True}
                                    if i == "iso_alpha3" or i == "year" or i == "id"
                                    else {"name": i, "id": i, "deletable": True, "selectable": True}
                                    for i in new_deg.columns
                                ],
                                style_cell={"minWidth": "80px", "maxWidth": "200px", 'overflow': "hidden",
                                            "textOverflow": "ellipsis"},
                                data=new_deg.to_dict('records'),  # the contents of the table
                                editable=True,  # allow editing of data inside all cells
                                filter_action="native",  # allow filtering of data by user ('native') or not ('none')
                                sort_action="native",  # enables data to be sorted per-column by user or not ('none')
                                sort_mode="single",  # sort across 'multi' or 'single' columns
                                column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                                row_selectable="multi",  # allow users to select 'multi' or 'single' rows
                                row_deletable=True,  # choose if user can delete a row (True) or not (False)
                                selected_columns=[],  # ids of columns that user selects
                                selected_rows=[],  # indices of rows that user selects
                                page_action="native",  # all data is passed to the table up-front or not ('none')
                                page_current=0,  # page number that user is on
                                page_size=10,  # number of rows visible per page
                                style_data={  # overflow cells' content into multiple lines
                                    'whiteSpace': 'normal',
                                    'height': 'auto'
                                },
                                export_format="csv"
                            )
                            , md=8), justify="center"),
                    ])
                ),
            ]),
            return html_plot
        elif pathname == (base_string + "/tables/sentiment"):
            list_names = [hashlib.md5(str(name).encode()).hexdigest() for name in df_sentiment["Usuario"].tolist()]
            df_new_sent = df_sentiment.copy()
            del df_new_sent["Usuario"]
            df_new_sent.insert(0, "Name", list_names, True)
            html_plot = html.Div(children=[
                dcc.Loading(
                    # style={"height":"200px","font-size":"100px","margin-top":"500px", "z-index":"1000000"},
                    style=style.SPINER_STYLE,
                    color="#000000",
                    id="loading-1",
                    type="default",
                    children=html.Div(id="loading-output", children=[
                        dbc.Row(dash_utils.toast_info("Sentiment analysis table",
                                                      "In this table you can see the sentiment analysis of each tweet in the dataset."),
                                justify="center"),
                        dbc.Row(dbc.Col(

                            dash_table.DataTable(
                                id='datatable-sentiment',
                                style_cell={"minWidth": "80px", "maxWidth": "200px", 'overflow': "hidden",
                                            "textOverflow": "ellipsis"},
                                columns=[
                                    {"name": i, "id": i, "deletable": True, "selectable": True, "hideable": True}
                                    if i == "iso_alpha3" or i == "year" or i == "id"
                                    else {"name": i, "id": i, "deletable": True, "selectable": True}
                                    for i in df_new_sent.columns
                                ],
                                data=df_new_sent.to_dict('records'),  # the contents of the table
                                editable=True,  # allow editing of data inside all cells
                                filter_action="native",  # allow filtering of data by user ('native') or not ('none')
                                sort_action="native",  # enables data to be sorted per-column by user or not ('none')
                                sort_mode="single",  # sort across 'multi' or 'single' columns
                                column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                                row_selectable="multi",  # allow users to select 'multi' or 'single' rows
                                row_deletable=True,  # choose if user can delete a row (True) or not (False)
                                selected_columns=[],  # ids of columns that user selects
                                selected_rows=[],  # indices of rows that user selects
                                page_action="native",  # all data is passed to the table up-front or not ('none')
                                page_current=0,  # page number that user is on
                                page_size=10,  # number of rows visible per page
                                style_data={  # overflow cells' content into multiple lines
                                    'whiteSpace': 'normal',
                                    'height': 'auto'
                                }
                            )
                            , md=8), justify="center"),
                    ])
                ),
            ]),
            return html_plot
        elif pathname == (base_string + "/graph/retweets"):
            web = Web(nx_G=kcore_g)
            web.display.height = 600
            web.display.gravity = 0.5
            web.save(config.WC_URL + "test.html")
            srcDoc = open(config.WC_URL + "test.html").read()
            controls = dash_utils.get_controls_rt_g(keyword_id="input-keyword-graph-rt")
            html_plot = html.Div(children=[
                dcc.Loading(
                    # style={"height":"200px","font-size":"100px","margin-top":"500px", "z-index":"1000000"},
                    style=style.SPINER_STYLE,
                    color="#000000",
                    id="loading-1",
                    type="default",
                    children=html.Div(id="loading-output", children=[
                        dbc.Row(dash_utils.toast_info("Graph of Retweets",
                                                      "This graphs show how users retweet each other. Each circle represents a user. You can filter the tweets by using keywords (words separated by commas), you can upload a file with"
                                                      "keywords (one word in each line) and you can filter tweets by date. By filtering, you can create different networks"
                                                      "about different topics."),
                                justify="center"),
                        dbc.Row(controls, justify="center"),
                        dbc.Row(
                            dbc.Col(html.Iframe(id="graph_rt_web", srcDoc=srcDoc, height=800, width=1600), md=8),
                            justify="center")
                    ])
                ),
            ]),

            return html_plot
        elif pathname == (base_string + "/graph/two_mode"):
            web = Web(nx_G=two_mode_g)
            web.display.height = 600
            web.display.gravity = 0.5
            web.display.colorBy = "bipartite"
            web.save(config.WC_URL + "two_mode.html")
            srcDoc = open(config.WC_URL + "two_mode.html").read()
            controls = dash_utils.get_controls_rt_g(keyword_id="input-keyword-graph-two-mode-rt")
            html_plot = html.Div(children=[
                dcc.Loading(
                    # style={"height":"200px","font-size":"100px","margin-top":"500px", "z-index":"1000000"},
                    style=style.SPINER_STYLE,
                    color="#000000",
                    id="loading-1",
                    type="default",
                    children=html.Div(id="loading-output", children=[
                        dbc.Row(dash_utils.toast_info("Graph of Retweets (Two mode)",
                                                      "This graphs show how users retweet tweets. Each red circle is a user, while blue circles are tweets. You can filter the tweets by using keywords (words separated by commas), you can upload a file with"
                                                      "keywords (one word in each line) and you can filter tweets by date. By filtering, you can create different networks"
                                                      "about different topics."),
                                justify="center"),
                        dbc.Row(controls, justify="center"),
                        dbc.Row(
                            dbc.Col(html.Iframe(id="graph_rt_two_mode_web", srcDoc=srcDoc, height=800, width=1600),
                                    md=8),
                            justify="center")
                    ])
                ),
            ]),

            return html_plot
        elif pathname == (base_string + "/graph/retweet_communities"):
            web = Web(nx_G=g_communities)
            web.display.height = 600
            web.display.gravity = 0.5
            web.save(config.WC_URL + "com.html")
            srcDoc = open(config.WC_URL + "com.html").read()
            options = dash_utils.get_controls_community2(communities)
            html_plot = html.Div(children=[
                dcc.Loading(
                    # style={"height":"200px","font-size":"100px","margin-top":"500px", "z-index":"1000000"},
                    style=style.SPINER_STYLE,
                    color="#000000",
                    id="loading-1",
                    type="default",
                    children=html.Div(id="loading-output", children=[
                        dbc.Row(dash_utils.toast_info("Graph of Retweets (Communities)",
                                                      "These graphs represent the communities formed by retweets. In the first visualization each node is one community."
                                                      "In the rest of the visualizations (filter by number), you can see the users that belong to each community."),
                                justify="center"),
                        dbc.Row(options, justify="center"),
                        dbc.Row(
                            dbc.Col(html.Iframe(id="graph_communities_web", srcDoc=srcDoc, height=800, width=1600),
                                    md=8)
                        )
                    ])
                ),

            ]),
            return html_plot
        elif pathname == (base_string + "/geomap/activity"):
            options = dash_utils.get_controls_activity()
            html_plot = html.Div(children=[
                dcc.Loading(
                    # style={"height":"200px","font-size":"100px","margin-top":"500px", "z-index":"1000000"},
                    style=style.SPINER_STYLE,
                    color="#000000",
                    id="loading-1",
                    type="default",
                    children=html.Div(id="loading-output", children=[
                        dbc.Row(dash_utils.toast_info("Map",
                                                      "In geomap you can see the activity of the users. You can filter either by Tweets or by Followers. In the first"
                                                      "case the number of tweets per country will be shown. In the second case the number of followers to users of each country"
                                                      "is shown."),
                                justify="center"),
                        dbc.Row(options, justify="center"),
                        dbc.Row(
                            dbc.Col(dcc.Graph(id='geograph', figure=mu.get_map_stats_by_country(df_map)), md=8))
                    ])
                ),

            ]),
            return html_plot

        elif pathname == (base_string + "/geomap/locations"):
            html_plot = html.Div(children=[
                dcc.Loading(
                    # style={"height":"200px","font-size":"100px","margin-top":"500px", "z-index":"1000000"},
                    style=style.SPINER_STYLE,
                    color="#000000",
                    id="loading-1",
                    type="default",
                    children=html.Div(id="loading-output", children=[
                        dbc.Row(dash_utils.toast_info("Location",
                                                      "In this geomap you can see the approximate location of the users."),
                                justify="center"),
                        dbc.Row(
                            dbc.Col(dcc.Graph(id='geomap_locations', figure=mu.get_map_locations(df_map)), md=8))
                    ])
                ),

            ]),
            return html_plot
        elif pathname == (base_string + "/topic/intertopic"):
            controls = dash_utils.get_controls_topics("topic-number", "topic-keywords",
                                                      topics=len(bert_model.get_topics()))
            html_plot = html.Div(children=[
                dcc.Loading(
                    # style={"height":"200px","font-size":"100px","margin-top":"500px", "z-index":"1000000"},
                    id="loading-1",
                    type="default",
                    children=html.Div(id="loading-output-1", children=[
                        dbc.Row(dash_utils.toast_info("Topic modeling",
                                                      "In these graphs you can see the topic modeling graphs of the tweet dataset. You can create different"
                                                      "topic models by filtering tweets.  You can choose the number"
                                                      "of topics that you want to create. You can filter the tweets by using keywords (words separated by commas), you can upload a file with"
                                                      "keywords (one word in each line) and you can filter tweets by date."),
                                justify="center"),
                        dbc.Row(controls, justify="center"),
                        dbc.Row(
                            children=[
                                dbc.Col(dcc.Graph(id='graph_intertopic', figure=bt.get_intertopic_distance(bert_model)),
                                        md=6),
                                dbc.Col(dcc.Graph(id='graph_topic_bar', figure=bt.get_topics_bar(bert_model)), md=4)]),
                    ])
                ),
            ]),

            return html_plot

        # If the user tries to reach a different page, return a 404 message
        return dbc.Jumbotron(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
            ]
        )


    def get_topics(input_key, file_contents):
        if file_contents is not None:
            decoded = base64.b64decode(file_contents[0].split(",")[1])
            topics = decoded.decode(encoding="utf-8").replace("\r", "").split('\n')
        else:
            topics = input_key.split(",")
        return topics


    def filter_by_date(df_filtered, start_date, end_date):
        if start_date or end_date:
            df_filtered['date_filter'] = pd.to_datetime(df_filtered['Fecha'], errors='coerce')
            df_filtered['date_filter'] = df_filtered['date_filter'].dt.date
            if start_date:
                start_time = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                after_start_date = df_filtered["date_filter"] >= start_time
                df_filtered = df_filtered.loc[after_start_date]
            if end_date:
                end_time = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
                before_end_date = df_filtered["date_filter"] <= end_time
                df_filtered = df_filtered.loc[before_end_date]
        return df_filtered


    @app.callback(
        Output('graph_all_hashtags', 'figure'),
        [Input("input-key-all", "n_submit"), Input("hashtag-number-all", "n_submit"),
         Input('hashtag-number-all-upload', 'contents'),
         dash.dependencies.Input('sessions_date', 'start_date'), dash.dependencies.Input('sessions_date', 'end_date')],
        [State('input-key-all', "value"), State('hashtag-number-all', "value"),
         State('hashtag-number-all-upload', 'filename'),
         State('hashtag-number-all-upload', 'last_modified')]
    )
    def update_hashtags_plot_all(n_submits, n_submits2, file_contents, start_date, end_date, hashtag_number, input_key,
                                 upload_data, last_modified):
        if (n_submits + n_submits2) == 0 and file_contents is None:
            return dash.no_update
        df_filtered = df.copy()
        df_filtered = filter_by_date(df_filtered, start_date, end_date)
        topics = get_topics(input_key, file_contents)
        df_rt = filter_by_topic(df_filtered, keywords=topics,
                                stopwords=["machinelearning", " ai ", "deeplearning", "opendata", "sentinel2",
                                           "oulghours", "euspace", "ruleofflaw", "imageoftheday"])
        df_rt = dash_utils.get_rt_hashtags(df_rt)
        df_rt = df_rt[:hashtag_number]
        df_rt.to_csv("hashtags.csv")
        return dash_utils.get_figure(df_rt)


    @app.callback(
        Output('graph_rt_hashtags', 'figure'),
        [Input("input-key-rt", "n_submit"), Input("hashtag-number-rt", "n_submit"),
         Input('hashtag-number-rt-upload', 'contents'),
         dash.dependencies.Input('sessions_date', 'start_date'), dash.dependencies.Input('sessions_date', 'end_date')],
        [State('input-key-rt', "value"), State('hashtag-number-rt', "value"),
         State('hashtag-number-rt-upload', 'filename'),
         State('hashtag-number-rt-upload', 'last_modified')]
    )
    def update_hashtags_plot(n_submits, n_submits2, file_contents, start_date, end_date, hashtag_number, input_key,
                             upload_data, last_modified):
        if (n_submits + n_submits2) == 0 and file_contents is None:
            return dash.no_update
        df_filtered = df.copy()
        df_filtered = filter_by_date(df_filtered, start_date, end_date)
        topics = get_topics(input_key, file_contents)
        df_r = filter_by_topic(df_filtered, keywords=topics, stopwords=None)
        df_r = dash_utils.get_rt_hashtags(df_r)
        df_r = df_r[:hashtag_number]
        return dash_utils.get_figure(df_r)


    @app.callback(
        Output('graph_ts_all_hashtags', 'figure'),
        [Input("input-key-ts-all", "n_submit"), Input("hashtag-number-ts-all", "n_submit"),
         Input("hashtags-name-ts-all", "value"),
         Input('hashtags-name-ts-all-upload', 'contents'), dash.dependencies.Input('sessions_date', 'start_date'),
         dash.dependencies.Input('sessions_date', 'end_date')],
        [State('input-key-ts-all', "value"), State('hashtag-number-ts-all', "value"),
         State('hashtags-name-ts-all-upload', 'filename'),
         State('hashtags-name-ts-all-upload', 'last_modified')]
    )
    def update_ts_all_plot(n_submits, n_submits2, value_dd, file_contents, start_date, end_date, hashtag_number,
                           input_key, filename, last_modified):
        if (n_submits + n_submits2) == 0 and not value_dd and file_contents is None:
            return dash.no_update
        df_filtered = df.copy()
        df_filtered = filter_by_date(df_filtered, start_date, end_date)
        topics = get_topics(input_key, file_contents)
        if len(topics) > 0 or start_date or end_date:
            df_ts_raw, days, sortedMH = dash_utils.get_all_temporalseries(df_filtered, keywords=topics)
        else:
            df_ts_raw, days, sortedMH = dash_utils.get_all_temporalseries(df_filtered)
        df_ts = dash_utils.get_df_ts(df_ts_raw, days, sortedMH)
        if value_dd and len(value_dd) > 0:
            df_ts_filtered = df_ts[value_dd + ["date"]]
            return dash_utils.get_temporal_figure(df_ts_filtered, n_hashtags=hashtag_number)
        return dash_utils.get_temporal_figure(df_ts, n_hashtags=hashtag_number)


    @app.callback(
        Output('graph_ts_rt_hashtags', 'figure'),
        [Input("input-key-ts-rt", "n_submit"), Input("hashtag-number-ts-rt", "n_submit"),
         Input("hashtags-name-ts-rt", "value"),
         Input('hashtags-name-ts-rt-upload', 'contents'), dash.dependencies.Input('sessions_date', 'start_date'),
         dash.dependencies.Input('sessions_date', 'end_date')],
        [State('input-key-ts-rt', "value"), State('hashtag-number-ts-rt', "value"),
         State('hashtags-name-ts-rt-upload', 'filename'),
         State('hashtags-name-ts-rt-upload', 'last_modified')]
    )
    def update_ts_all_plot(n_submits, n_submits2, value_dd, file_contents, start_date, end_date, hashtag_number,
                           input_key, filename, last_modified):
        if (n_submits + n_submits2) == 0 and not value_dd and file_contents is None:
            return dash.no_update
        df_filtered = df.copy()
        df_filtered = filter_by_date(df_filtered, start_date, end_date)
        topics = get_topics(input_key, file_contents)
        if len(topics) > 0:
            df_ts_rt_raw, days, sortedMH = dash_utils.get_rt_temporalseries(df_filtered, keywords=topics)
        else:
            df_ts_rt_raw, days, sortedMH = dash_utils.get_rt_temporalseries(df_filtered, keywords=topics)
        df_ts = dash_utils.get_df_ts(df_ts_rt_raw, days, sortedMH)
        if value_dd and len(value_dd) > 0:
            df_ts_filtered = df_ts[value_dd + ["date"]]
            return dash_utils.get_temporal_figure(df_ts_filtered, n_hashtags=hashtag_number)
        return dash_utils.get_temporal_figure(df_ts, n_hashtags=hashtag_number)


    @app.callback(
        dash.dependencies.Output('geograph', 'figure'),
        [dash.dependencies.Input('activity_type', 'value')])
    def update_com_graph(value):
        fig = mu.get_map_stats_by_country(df_map, value)
        return fig


    @app.callback(
        dash.dependencies.Output('graph_communities_web', 'srcDoc'),
        [dash.dependencies.Input('com_number2', 'value'),
         dash.dependencies.Input('com_algorithm2', 'value')])
    def update_com_graph(value, algorithm):
        global com_algorithm
        global commusnities
        if value == "all":
            com = g_communities
        else:
            if com_algorithm != algorithm:
                com_algorithm = algorithm
                communities = dash_utils.get_communities(G, algorithm)
            com = dash_utils.get_community_graph(G, communities, int(value))
        web = Web(nx_G=com)
        web.display.height = 600
        web.display.gravity = 0.5
        web.save(config.WC_URL + "com.html")
        srcDoc = open(config.WC_URL + "com.html").read()
        return srcDoc


    @app.callback(
        Output('graph_rt_web', 'srcDoc'),
        [Input("input-keyword-graph-rt", "n_submit"), Input("input-keyword-graph-rt-upload", 'contents')],
        [State('input-keyword-graph-rt', "value"), State('input-keyword-graph-rt-upload', 'filename'),
         State('input-keyword-graph-rt-upload', 'last_modified')]
    )
    def update_rt_g(n_submits, file_contents, keywords, filename, last_modified):
        global df_ts
        if n_submits == 0 and file_contents is None:
            return dash.no_update
        topics = get_topics(keywords, file_contents)
        if len(topics) > 0:
            filtered_graph = dash_utils.kcore_graph(df, keywords=topics)
            web = Web(nx_G=filtered_graph)
            web.display.height = 600
            web.display.gravity = 0.5
            web.save(config.WC_URL + "graph_rt.html")
            srcDoc = open(config.WC_URL + "graph_rt.html").read()
            return srcDoc

        return dash.no_update


    @app.callback(
        Output('graph_rt_two_mode_web', 'srcDoc'),
        [Input("input-keyword-graph-two-mode-rt", "n_submit"),
         Input("input-keyword-graph-two-mode-rt-upload", 'contents')],
        [State('input-keyword-graph-two-mode-rt', "value"), State('input-keyword-graph-two-mode-rt-upload', 'filename'),
         State('input-keyword-graph-two-mode-rt-upload', 'last_modified')]
    )
    def update_rt_g(n_submits, file_contents, keywords, filename, last_modified):
        global df_ts
        if n_submits == 0 and file_contents is None:
            return dash.no_update
        topics = get_topics(keywords, file_contents)
        if len(topics) > 0:
            filtered_graph = dash_utils.get_two_mode_graph(df, keywords=topics)
            web = Web(nx_G=filtered_graph)
            web.display.height = 600
            web.display.gravity = 0.5
            web.display.colorBy = "bipartite"
            web.save(config.WC_URL + "two_mode.html")
            srcDoc = open(config.WC_URL + "two_mode.html").read()
            return srcDoc

        return dash.no_update


    @app.callback(
        [Output('graph_intertopic', 'figure'), Output('graph_topic_bar', 'figure')],
        [Input("topic-keywords", "n_submit"), Input("topic-number", "n_submit"),
         Input('topic-keywords-upload', 'contents'),
         dash.dependencies.Input('sessions_date', 'start_date'), dash.dependencies.Input('sessions_date', 'end_date')],
        [State('topic-keywords', "value"), State("topic-number", "value"), State('topic-keywords-upload', 'filename'),
         State('topic-keywords-upload', 'last_modified')]
    )
    def update_hashtags_plot_all(n_submits, n_submits2, file_contents, start_date, end_date, input_key, hashtag_number,
                                 upload_data, last_modified):
        if (n_submits + n_submits2) == 0 and file_contents is None:
            return dash.no_update
        keywords = get_topics(input_key, file_contents)
        new_model = bert_model
        df_filtered = df.copy()
        df_filtered = filter_by_date(df_filtered, start_date, end_date)

        if len(keywords) > 0:
            df_filtered = filter_by_topic(df_filtered, keywords=keywords, stopwords=None)
            # documents = bt.get_cleaned_documents(df_filtered)
            # new_model, new_topics, new_probs = bt.create_bert_model(documents)
            return bt.get_intertopic_distance(new_model), bt.get_topics_bar(new_model)
            
    return app.server, app


if __name__ == "__main__":
    server, app = create_dashboard()
    app.run_server(host="0.0.0.0",port=6123, debug=False)

