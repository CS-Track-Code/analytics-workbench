from geopy.geocoders import Nominatim
import pymongo
import pandas as pd

geolocator = Nominatim(user_agent="geoapiExercises")

con = pymongo.MongoClient("f-l2108-pc09.aulas.etsit.urjc.es", port=21000)
col = con["cstrack"]["map_data"]
latitudes = pd.DataFrame(list(col.find()))
country_codes = []
for i, row in latitudes.iterrows():
    location = geolocator.reverse(str(row["lat"]) + "," + str(row["lon"]))
    try:
        address = location.raw['address']
        print(address)
        country_code = address.get('country_code').upper()
        print(country_code)
        country_codes.append(country_code)
    except AttributeError:
        country_codes.append("NaN")

latitudes["country_code"] = country_codes
latitudes.to_csv("latitudes_cc.csv")

