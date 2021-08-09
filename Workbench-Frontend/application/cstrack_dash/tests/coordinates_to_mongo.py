import pandas as pd
import pymongo
import json


con = pymongo.MongoClient("f-l2108-pc09.aulas.etsit.urjc.es", port=21000)
col_map = con["cstrack"]["geomap_full"]

df = pd.read_csv("full_data_2.csv", index_col=False)
df = df.drop(columns=["Unnamed: 0"])
df = df.drop(columns=["Unnamed: 0.1.1"])
df = df.drop(columns=["Unnamed: 0.1"])
print(df)

col_map.insert_many(df.to_dict(orient="records"))