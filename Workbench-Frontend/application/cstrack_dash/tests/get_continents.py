import pandas as pd
import pycountry
import pycountry_convert as pc

df = pd.read_csv("full_data.csv")
df_2 = pd.read_csv("country_info.csv")

continent = []
country_name = []
for i, row in df.iterrows():
    print(row["country_code"])
    if str(row["country_code"]).lower() == "nan":
        continent.append("nan")
        country_name.append("nan")
    else:
        search_row = df_2[df_2["Two_Letter_Country_Code"] == row["country_code"]]

        try:
            print(search_row.Continent_Name.values[0], "|", search_row.Country_Name.values[0])
            country_name.append(search_row.Country_Name.values[0])
            continent.append(search_row.Continent_Name.values[0])
        except Exception as e:
            print(e)
            try:
                country = pycountry.countries.get(alpha_2=row["country_code"])
                country_name.append(country.name)
                try:
                    continent_name = pc.convert_continent_code_to_continent_name(
                        pc.country_alpha2_to_continent_code(country.alpha_2))
                    continent.append(continent_name)
                except Exception as e:
                    continent.append("nan")
            except Exception as e:
                print(country)
                country_name.append("nan")
                continent.append("nan")

df["country"] = country_name
df["continent"] = continent
df.to_csv("full_data_2.csv")