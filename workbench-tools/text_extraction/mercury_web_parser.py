# -*- coding: utf-8 -*-
import requests


def extract_text(api_endpoint, web_url, retry=False, from_wiki_no_ref=False):
    text = raw_text(api_endpoint, web_url)
    if from_wiki_no_ref:
        text = text.split('<h2><span class="mw-headline" id="See_also">See also</span></h2>')[0]
    while text.find("<") >= 0:
        text = text.split("<", 1)[0] + text.split(">", 1)[1]
    while len(text.replace("\n\n\n", "\n\n")) < len(text):
        text = text.replace("\n\n\n", "\n\n")
    text = text.replace("&#xE4;", "ä").replace("&#xF6;", "ö").replace("&#xFC;", "ü").replace("&#xDF;", "ß") \
        .replace("&#xC4;", "Ä").replace("&#xD6;", "Ö").replace("&#xDC;", "Ü").replace("&#x201E;", '"') \
        .replace("&#x201C;", '"').replace("&#x2013;", '-').replace("&amp;", '&').replace("&#xA0", ' ') \
        .replace("&#xE6;", "æ").replace("&#xE5;", "å").replace('&quot;', '"').replace("&apos;", "'")
    len_of_text = len(text)
    while len_of_text > len(text.replace("  ", " ")):
        text = text.replace("  ", " ")
        len_of_text = len(text)
    print("after: " + text)
    if not retry:
        if text.find(" ") < 0 and "http://" in text:
            extract_text(api_endpoint, text, retry=True)
    return text


def raw_text(api_endpoint, web_url):
    headers = {"x-api-key": None}

    url = "{}?url={}".format(api_endpoint, web_url)
    print(url)
    response = requests.get(url, headers=headers)
    return response.json()['content']


def extract_wiki_without_ref(api_endpoint, web_url, retry=False):
    return extract_text(api_endpoint, web_url, retry, True)
