import nltk

from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

nltk.download("stopwords")
nltk.download('punkt')


def split_to_tokens(text, lang):
    t_tokens = nltk.word_tokenize(text, language=lang)
    return t_tokens


def split_to_tokens_without_stopwords(text, lang):
    sw = set(stopwords.words(lang))
    t_tokens = split_to_tokens(text, lang)
    t_tokens = [item.lower() for item in t_tokens if item not in sw and len(item) > 3 and not item.isdigit()]
    return t_tokens


def stem_tokens(t_tokens, lang):
    stemmer = SnowballStemmer(language=lang)
    t_tokens = [stemmer.stem(item) for item in t_tokens]
    return t_tokens


def text_to_tokens(text, lang="english"):
    t_tokens = split_to_tokens_without_stopwords(text, lang)
    t_tokens = stem_tokens(t_tokens, lang)
    return t_tokens


def text_to_most_important_tokens(text, tfidf_extractor, lang="english", minimum_percentage=0.25,
                                  also_return_all_tokens=False):
    if not lang == "english":
        return 0
    t_tokens = split_to_tokens_without_stopwords(text, lang)

    tfidf_result = tfidf_extractor.extract(t_tokens)
    tfidf_list = [[score, word, tf] for score, word, tf in
                  zip(tfidf_result['score'], tfidf_result['word'], tfidf_result['tf'])]

    tokens = []
    minimum = tfidf_list[0][0] * minimum_percentage
    for tf_elem in tfidf_list:
        if tf_elem[0] >= minimum:
            for i in range(tf_elem[2]):
                tokens.append(tf_elem[1])

    t_tokens = stem_tokens(tokens, lang)
    if also_return_all_tokens:
        return t_tokens, tokens
    else:
        return t_tokens
