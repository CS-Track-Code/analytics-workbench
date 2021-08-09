import pandas as pd
import pymongo
import json


con = pymongo.MongoClient("f-l2108-pc09.aulas.etsit.urjc.es", port=21000)
col_users = con["cstrack"]["users"]

users = pd.DataFrame(list(col_users.find()))
users_followers = []
users_tweets = []

col = con["cstrack"]["coordinates"]
coordinates = pd.DataFrame(list(col.find()))
coordinates["lat"] = pd.to_numeric(coordinates["lat"])
coordinates["lon"] = pd.to_numeric(coordinates["lon"])

for i, row in coordinates.iterrows():
    print(users[users["screen_name"] == row["screen_name"]]["followers_count"].values[0])
    users_followers.append(users[users["screen_name"] == row["screen_name"]]["followers_count"].values[0])
    users_tweets.append(users[users["screen_name"] == row["screen_name"]]["statuses_count"].values[0])
coordinates["tweets"] = users_tweets
coordinates["followers"] = users_followers
coordinates.to_csv("coordinates.csv")




