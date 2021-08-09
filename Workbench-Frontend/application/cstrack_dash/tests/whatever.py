import pymongo

db = pymongo.MongoClient(host="127.0.0.1", port=27017)
twitter_data = db["cstrack"]["cstrack_stats"]
twitter_dict_list = list(twitter_data.find())

db_2 = pymongo.MongoClient(host="f-l2108-pc09.aulas.etsit.urjc.es", port=21000)
db_2["cstrack"]["cstrack_stats"].insert_many(twitter_dict_list)