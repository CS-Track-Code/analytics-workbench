import pandas as pd
import generate_utils as gu

df = pd.read_csv("Lynguo_def2.csv", sep=';', encoding='latin-1', error_bad_lines=False)
gu.sentiment_analyser(df)
