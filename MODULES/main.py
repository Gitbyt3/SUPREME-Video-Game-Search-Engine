import pandas as pd
from ast import literal_eval as string_to_list
import preprocessing as pp
import query_processing as qp
import candidate_retrieval as cr
import os
import json
import sys
from sklearn.preprocessing import StandardScaler
import numpy as np

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
    # init preprocessing
    pp.init(games)

    games_BM25, games_SBERT = games_processing(games)
    # Load the expansion terms from the JSON file for query processing
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Query_Processing/expansion_terms.json')), 'r') as json_file:
        expansion_terms = json.load(json_file)
    developer_set, platform_set, genre_set = qp.init(games_SBERT, expansion_terms)

    SBERT_weights = [0.5, 0.2, 0.3, 0.4]
    BM25_weights = [2.0, 0.6, 1.5, 0.8, 0.8]
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
        scaler = StandardScaler()
        # candidates[['BM25 Score', 'SBERT Score']] = scaler.fit_transform(candidates[['BM25 Score', 'SBERT Score']])
        candidates['weighted_score'] = candidates['BM25 Score'] * .7 + candidates['SBERT Score'] * .3
        candidates = candidates.sort_values(by='weighted_score', ascending=False)
    
        sys.stdout.write(json.dumps({
            'id': req_id,
            'data': candidates[['Title', 'ID', 'BM25 Score', 'SBERT Score', 'BM25_Scores', 'weighted_score']].head(10).to_dict(orient='records')
        }, cls=NumpyEncoder))
        sys.stdout.flush()

    print('\nExiting the program...')
    sys.stdout.flush()
    return None

if __name__ == "__main__":
    main()