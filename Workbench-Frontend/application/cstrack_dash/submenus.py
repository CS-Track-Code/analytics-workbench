""" Module to create the sidebar of the Dash application
"""

import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

try:
    import style
except ModuleNotFoundError:
    import application.cstrack_dash.style as style

def create_submenus(base_string):

    submenu_1 = [
        html.Li(
            # use Row and Col components to position the chevrons
            dbc.Row(
                [
                    dbc.Col("Most used hashtags"),
                    dbc.Col(
                        html.I(id="chevron-1", className="fas fa-chevron-right mr-3"), width="auto"
                    ),
                ],
                className="my-1",
            ),
            style={"cursor": "pointer"},
            id="submenu-1",
        ),
        # we use the Collapse component to hide and reveal the navigation links
        dbc.Collapse(
            [
                dbc.Nav(
                    [dbc.NavLink("All hashtags", href=base_string + "/hashtags/all", active="partial"),
                    dbc.NavLink("Retweeted hashtags", href=base_string + "/hashtags/rt", active="partial")],
                    pills=True, vertical=True
                )
            ],
            id="submenu-1-collapse",
        ),
    ]

    submenu_2 = [
        html.Li(
            dbc.Row(
                [
                    dbc.Col("Time series"),
                    dbc.Col(
                        html.I(id="chevron-2", className="fas fa-chevron-right mr-3"), width="auto"
                    ),
                ],
                className="my-1",
            ),
            style={"cursor": "pointer"},
            id="submenu-2",
        ),
        dbc.Collapse(
            [
                dbc.Nav(
                [
                    dbc.NavLink("All hashtags", href= base_string + "/timeseries/allhashtags", active="partial"),
                    dbc.NavLink("Retweeted hashtags", href= base_string + "/timeseries/rthashtags", active="partial"),
                ],
                pills = True, vertical=True
                )
            ],
            id="submenu-2-collapse",
        ),
    ]

    submenu_3 = [
        html.Li(
            dbc.Row(
                [
                    dbc.Col("Wordcloud"),
                    dbc.Col(
                        html.I(id="chevron-3", className="fas fa-chevron-right mr-3"), width="auto"
                    ),
                ],
                className="my-1",
            ),
            style={"cursor": "pointer"},
            id="submenu-3",
        ),
        dbc.Collapse(
            [
                dbc.Nav(
                [
                dbc.NavLink("Wordcloud", href= base_string + "/wordcloud", active="partial"),
                ],
                pills=True, vertical=True
                )
            ],
            id="submenu-3-collapse",
        ),
    ]

    submenu_4 = [
        html.Li(
            dbc.Row(
                [
                    dbc.Col("Tables"),
                    dbc.Col(
                        html.I(id="chevron-4", className="fas fa-chevron-right mr-3"), width="auto"
                    ),
                ],
                className="my-1",
            ),
            style={"cursor": "pointer"},
            id="submenu-4",
        ),
        dbc.Collapse(
            [
                dbc.Nav(
                [
                dbc.NavLink("Degrees", href= base_string + "/tables/retweets", active="partial"),
                dbc.NavLink("Sentiment", href= base_string + "/tables/sentiment", active="partial"),
                ],
                pills=True, vertical=True
                )
            ],
            id="submenu-4-collapse",
        ),
    ]

    submenu_5 = [
        html.Li(
            dbc.Row(
                [
                    dbc.Col("Networks"),
                    dbc.Col(
                        html.I(id="chevron-5", className="fas fa-chevron-right mr-3"), width="auto"
                    ),
                ],
                className="my-1",
            ),
            style={"cursor": "pointer"},
            id="submenu-5",
        ),
        dbc.Collapse(
            [
                dbc.Nav([
                    dbc.NavLink("Retweets", href=base_string + "/graph/retweets", active="partial"),
                    dbc.NavLink("RT Communities", href=base_string + "/graph/retweet_communities", active="partial"),
                    dbc.NavLink("Two mode", href=base_string + "/graph/two_mode", active="partial"),
                ],
                pills=True, vertical=True)

            ],
            id="submenu-5-collapse",
        ),
    ]


    submenu_6 = [
        html.Li(
            dbc.Row(
                [
                    dbc.Col("Geomaps"),
                    dbc.Col(
                        html.I(id="chevron-6", className="fas fa-chevron-right mr-3"), width="auto"
                    ),
                ],
                className="my-1",
            ),
            style={"cursor": "pointer"},
            id="submenu-6",
        ),
        dbc.Collapse(
            [
                dbc.Nav([
                    dbc.NavLink("Tweets and Follows per country", href=base_string + "/geomap/activity", active="partial"),
                    dbc.NavLink("Locations", href=base_string + "/geomap/locations", active="partial"),
                ],
                pills=True, vertical=True)

            ],
            id="submenu-6-collapse",
        ),
    ]

    submenu_7 = [
        html.Li(
            dbc.Row(
                [
                    dbc.Col("Topic modelling"),
                    dbc.Col(
                        html.I(id="chevron-7", className="fas fa-chevron-right mr-3"), width="auto"
                    ),
                ],
                className="my-1",
            ),
            style={"cursor": "pointer"},
            id="submenu-7",
        ),
        dbc.Collapse(
            [
                dbc.Nav([
                    dbc.NavLink("Intertopic map", href=base_string + "/topic/intertopic", active="partial"),
                ], pills=True, vertical=True)
            ],
            id="submenu-7-collapse",
        ),
    ]
    return submenu_1, submenu_2, submenu_3, submenu_4, submenu_5, submenu_6, submenu_7


