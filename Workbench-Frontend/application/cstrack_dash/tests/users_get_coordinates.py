import requests
import urllib.parse
import pymongo
import json

db = pymongo.MongoClient(host="f-l2108-pc09.aulas.etsit.urjc.es", port=21000)
col_people = db["cstrack"]["users"]
col_coordinates = db["cstrack"]["coordinates"]
localizations = list(col_people.find())
dividers = [",", "."]
for row in localizations:
    correct = False
    tries = 0
    base_address = row["location"]
    print(base_address)
    if len(base_address) > 0:
        while not correct and tries < 2:
            address = base_address.split(dividers[tries])[0]
            try:
                user_exists = col_coordinates.find_one({"screen_name": row["screen_name"]})
                if user_exists is None:

                    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'
                    print(url)
                    response = requests.get(url).json()

                    data = {"lat": response[0]["lat"], "lon": response[0]["lon"], "screen_name": row["screen_name"]}
                    col_coordinates.insert_one(data)
                correct = True
            except IndexError:
                tries += 1
            except json.decoder.JSONDecodeError:
                tries += 1


