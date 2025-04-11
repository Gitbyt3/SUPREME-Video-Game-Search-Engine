import requests
import pandas as pd
from io import StringIO
from ast import literal_eval as string_to_list
import query_processing as qp
import candidate_retrieval as cr

def games_processing(games):
    games['Summary'] = games['Summary'].fillna('')
    games[['Plays','Playing','Backlogs','Wishlist','Lists','Reviews']] = games[['Plays','Playing','Backlogs','Wishlist','Lists','Reviews']].map(lambda x: float(x.replace('K','')) * 1000 if 'K' in x else float(x))
    games[['Developers','Platforms','Genres']] = games[['Developers','Platforms','Genres']].map(string_to_list)
    games = games.drop_duplicates(subset='Title', ignore_index=True)
    games[['Developers','Platforms','Genres']] = games[['Developers','Platforms','Genres']].map(lambda listed: [x.lower() for x in listed])
    games['Title'], games['Summary']  = games['Title'].str.lower(), games['Summary'].str.lower()

    games_SBERT = games.copy()
    games_BM25 = games.copy()
    games_BM25[['Developers','Platforms','Genres']] = games_BM25[['Developers','Platforms','Genres']].map(lambda x: ' '.join(x))

    return games_BM25, games_SBERT

def main():
    games = pd.read_csv(StringIO(requests.get("https://drive.google.com/uc?export=download&id=1lBpDPlBsoR3UUe1sYLs5z4cLiJr0_tAs").text), index_col=0)
    games_BM25, games_SBERT = games_processing(games)
    developer_set, platform_set, genre_set, expansion_terms = qp.init(games_SBERT)

    SBERT_weights = [0.5, 0.2, 0.3, 0.4]
    BM25_weights = [2.0, 0.6, 1.5, 0.8, 0.8]
    cr.init(games_BM25, games_SBERT, SBERT_weights, BM25_weights)

    test_query = "  THis Is a test_query playstation 5 PS5 FPS First-person shooter"
    test_processed = qp.execute(test_query, expansion_terms, developer_set, platform_set, genre_set)
    candidates = cr.execute(test_processed)
    print(candidates)

    return None

if __name__ == "__main__":
    main()