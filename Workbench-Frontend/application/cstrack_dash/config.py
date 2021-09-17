import os
from dotenv import load_dotenv

load_dotenv()

TWEET_DATASET = os.getenv('TWEET_DATASET')
MONGODB_CONNECTION = os.getenv('MONGODB_CONNECTION')
BERT_MODEL = os.getenv('BERT_MODEL')
BERT_TOPICS = os.getenv('BERT_TOPICS')
ASSETS_URL = os.getenv("ASSETS_URL")
WC_URL = os.getenv("WC_URL")

print(TWEET_DATASET, MONGODB_CONNECTION, BERT_MODEL)