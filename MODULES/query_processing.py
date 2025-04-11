import pandas as pd
import os
import json
import unicodedata
import re
from ast import literal_eval as string_to_list
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
import requests

def init(games):
    response = requests.get("https://drive.google.com/uc?export=download&id=1OgpQ62XC2H-MCHEkg-aJetRKcJOMq7e1")
    expansion_terms = json.loads(response.text)

    developer_set, platform_set, genre_set = set(), set(), set()
    for developers, platforms, genres in zip(games['Developers'], games['Platforms'], games['Genres']):
        developer_set.update(set(developers)), platform_set.update(set(platforms)), genre_set.update(set(genres))
    developer_set, platform_set, genre_set = set(word.lower() for word in developer_set), set(word.lower() for word in platform_set), set(word.lower() for word in genre_set)

    return developer_set, platform_set, genre_set, expansion_terms

def execute(query, expansion_terms, developers, platforms, genres, synonym_expansion=False):
    def query_normalisation(query):
        query = query.lower()
        query = unicodedata.normalize('NFKD', query)
        query = ''.join([c for c in query if not unicodedata.combining(c)])
        query = query.replace('-', ' ')
        query = re.sub(f'[{re.escape(string.punctuation)}]', '', query)
        query = re.sub(r'\s+', ' ', query).strip()
        tokens = word_tokenize(query)
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words]
        lemmatiser = WordNetLemmatizer()
        lemmatised = [lemmatiser.lemmatize(word) for word in tokens]
        return ' '.join(lemmatised)

    def query_expansion(query, expansion_terms, synonym_expansion=True):
        if synonym_expansion is True:
            synonym_expansion = 2
        def get_synonyms(token):
            synonyms = set()
            for syn in wordnet.synsets(token):
                for lemma in syn.lemmas():
                    synonym = lemma.name().replace('_', ' ')
                    if synonym.lower() != token.lower():
                        synonyms.add(synonym)
            return list(synonyms)
        for term in expansion_terms:
            if term in query:
                loc = query.find(term)
                query = query[:loc] + expansion_terms[term] + ' ' + query[loc:]
        expanded_tokens = []
        for token in query.split(' '):
            expanded_tokens.append(token)
            if synonym_expansion:
                synonyms = get_synonyms(token)
                expanded_tokens.extend(synonyms[:synonym_expansion])
        unique_terms = []
        for token in expanded_tokens:
            if token not in unique_terms:
                unique_terms.append(token)
            
        return ' '.join(unique_terms)

    def query_parsing(query, developers, platforms, genres):
        def extract_years(query):
            pattern = r'\b(19[8-9]\d|20\d{2})\b'
            matches = re.findall(pattern, query)
            return [int(year) for year in matches]
        
        query_years = extract_years(query)
        query_developers = [developer for developer in developers if developer in query]
        query_platforms = [platform for platform in platforms if platform in query]
        query_genres = [genre for genre in genres if genre in query]
        return {'Developers':query_developers, 'Platforms':query_platforms, 'Genres':query_genres, 'Years':query_years}

    normalised_expanded = query_expansion(query_normalisation(query), expansion_terms, synonym_expansion=synonym_expansion)
    parsed = query_parsing(normalised_expanded, developers, platforms, genres)
    output = {'Original':query, 'Processed':normalised_expanded, 'Developers':parsed['Developers'], 'Platforms':parsed['Platforms'], 'Genres':parsed['Genres'], 'Years':parsed['Years']}
    return output


if __name__ == "__main__":
    init('test')