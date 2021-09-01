import pandas as pd
import pycountry
import pycountry_convert as pc

df = pd.read_csv("full_data.csv")
continent = []
country_name = []
for i, row in df.iterrows():
    print(row["country_code"])
    if str(row["country_code"]).lower() == "nan":
        continent.append("nan")
        country_name.append("nan")
    else:
        country = pycountry.countries.get(alpha_2=row["country_code"])
        print(country)
        try:
            country_name.append(country.name)
            continent_name = pc.convert_continent_code_to_continent_name(pc.country_alpha2_to_continent_code(country.alpha_2))
            continent.append(country.alpha_3)
        except Exception as e:
            country_name.append("nan")
            continent.append("nan")

df["country"] = country_name
df["continent"] = continent
df.to_csv("full_data_2.csv")