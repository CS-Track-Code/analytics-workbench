import pandas as pd
import pymongo
import map_utils as mu

con = pymongo.MongoClient("f-l2108-pc09.aulas.etsit.urjc.es", port=21000)
col = con["cstrack"]["geomap_full"]
info = pd.DataFrame(list(col.find()))
mu.get_map_locations(info)