import os
from dotenv import load_dotenv

load_dotenv()

TWEET_DATASET = os.getenv('TWEET_DATASET')
MONGODB_CONNECTION = os.getenv('MONGODB_CONNECTION')
BERT_MODEL = os.getenv('BERT_MODEL')

print(TWEET_DATASET, MONGODB_CONNECTION, BERT_MODEL)