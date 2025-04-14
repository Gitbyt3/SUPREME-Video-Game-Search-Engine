import pandas as pd
from ast import literal_eval as string_to_list
import preprocessing as pp
import query_processing as qp
import candidate_retrieval as cr
import query_ranking as qr
import os
import json
import sys
from sklearn.preprocessing import StandardScaler
import numpy as np
import math
from utils import sigmoid_scaling, max_min_scaling

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)
            
def filter_games(games):
    games['Summary'] = games['Summary'].fillna('')
    games = games.drop_duplicates(subset='Title', ignore_index=True)
    games[['Developers','Platforms','Genres']] = games[['Developers','Platforms','Genres']].map(string_to_list)

    return games

def games_processing(games):
    games[['Plays','Playing','Backlogs','Wishlist','Lists','Reviews']] = games[['Plays','Playing','Backlogs','Wishlist','Lists','Reviews']].map(lambda x: float(x.replace('K','')) * 1000 if 'K' in x else float(x))
    games[['Developers','Platforms','Genres']] = games[['Developers','Platforms','Genres']].map(lambda listed: [x.lower() for x in listed])
    games['Title'], games['Summary']  = games['Title'].str.lower(), games['Summary'].str.lower()

    games_SBERT = games.copy()
    games_BM25 = games.copy()
    games_BM25[['Developers','Platforms','Genres']] = games_BM25[['Developers','Platforms','Genres']].map(lambda x: ' '.join(x))

    return games_BM25, games_SBERT

def main():
    sys.stdout.write('IR Python Program initializing...\ncwd: {}\n'.format(os.getcwd()))
    sys.stdout.flush()

    games = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backloggd_games.csv')), index_col=0)
    games = filter_games(games)
    games['ID'] = games.index
    # init preprocessing
    pp.init(games)

    games_BM25, games_SBERT = games_processing(games)
    # Load the expansion terms from the JSON file for query processing
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Query_Processing/expansion_terms.json')), 'r') as json_file:
        expansion_terms = json.load(json_file)
    qp.init(games_SBERT, expansion_terms)

    SBERT_weights = [0.5, 0.2, 0.3, 0.4]
    BM25_weights = [2.0, 0.8, 1.0, 1.4, 1.4]
    cr.init(games_BM25, games_SBERT, SBERT_weights, BM25_weights)

    sys.stdout.flush()
    sys.stdout.write('initialized')
    sys.stdout.flush()

    while True:
        line = sys.stdin.readline()

        if not line:
            break
        line = line.strip()
        if line == 'exit':
            break

        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            sys.stderr.write('Invalid JSON format.\n')
            sys.stderr.flush()
            continue

        query = message['query']
        req_id = message['id']
        processed_query = qp.execute(query)
        sys.stderr.write('Done query processing: ' + query + ' -> ' + processed_query['Processed'] + '\n')
        sys.stderr.flush()
        candidates = cr.execute(processed_query)
        # scaler = StandardScaler()
        # candidates[['BM25 Score', 'SBERT Score']] = scaler.fit_transform(candidates[['BM25 Score', 'SBERT Score']])
        # try use Sigmoid scaling
        # candidates['weighted_score'] = sigmoid_scaling(candidates['BM25 Score']) * .7 + sigmoid_scaling(candidates['SBERT Score']) * .3
        # try use min-max scaling
        candidates['BM25 Score'] = max_min_scaling(candidates['BM25 Score'])
        candidates['SBERT Score'] = max_min_scaling(candidates['SBERT Score'])
        candidates['weighted_score'] = candidates['BM25 Score'] * 0.7 + candidates['SBERT Score'] * 0.3
        # candidates = candidates.sort_values(by='weighted_score', ascending=False)

        # merge other columns
        candidates = pd.merge(candidates, 
            games[['ID', 'Plays', 'Release_Date', 'Playing', 'Rating', 'Genres', 'Platforms']], 
            on='ID', 
            how='left').fillna(0)

        qr.init() # bypass the model loading
        results = qr.execute(0, processed_query, candidates, useLTR=True)
    
        sys.stdout.write(json.dumps({
            'id': req_id,
            'data': results[['Title', 'ID', 'BM25 Score', 'SBERT Score', 'BM25_Scores', 'weighted_score', 'Final Score']].head(12).to_dict(orient='records')
        }, cls=NumpyEncoder))
        sys.stdout.flush()

    print('\nExiting the program...')
    sys.stdout.flush()
    return None

if __name__ == "__main__":
    main()