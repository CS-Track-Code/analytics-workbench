import datetime
import itertools
from networkx.algorithms import community
import pandas as pd
import pymongo
import plotly.express as px
import plotly.graph_objects as go

eu_box = {"west": -25.1634705067,
          "south": 27.6929716381,
          "east": 60.7935607433,
          "north": 66.8997802006}

start = datetime.datetime.now()
con = pymongo.MongoClient("f-l2108-pc09.aulas.etsit.urjc.es", port=21000)
col = con["cstrack"]["map_data"]

coordinates = pd.DataFrame(list(col.find()))
coordinates["lat"] = pd.to_numeric(coordinates["lat"])
coordinates["lon"] = pd.to_numeric(coordinates["lon"])
eu_coordinates = coordinates[(coordinates["lat"] > eu_box["south"]) & (coordinates["lat"] < eu_box["north"]) &
                             (coordinates["lon"] > eu_box["west"]) & (coordinates["lon"] < eu_box["east"])]
print(coordinates.dtypes)
"""fig = px.scatter_geo(coordinates, lat="lat", lon="lon")
fig.show()"""

"""fig = go.Figure(go.Densitymapbox(lat=coordinates.lat, lon=coordinates.lon,radius=10))
fig.update_layout(mapbox_style="stamen-terrain", mapbox_center_lon=180)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()"""

fig = go.Figure(go.Scattergeo(lon=eu_coordinates["lon"], lat=eu_coordinates["lat"], text=eu_coordinates["screen_name"]))
fig.update_layout(geo_scope="world",height=500, margin={"r":0,"t":0,"l":0,"b":0})
fig.show()

print("END:", datetime.datetime.now() - start)