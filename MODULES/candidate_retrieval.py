import pandas as pd
import numpy as np
import os
import pickle
from sklearn.preprocessing import MultiLabelBinarizer, normalize
from sentence_transformers import SentenceTransformer
import faiss
import re
from rank_bm25 import BM25Okapi

def tokenize(text):
    # Remove punctuation and convert to lowercase
    text = re.sub(r'[^\w\s]', '', text)
    return text.lower().split()

def save_embeddings(embeddings, onehot_encoders, faiss_index, file_path):
    with open(file_path, 'wb') as file:
        pickle.dump({'embeddings':embeddings, 'onehot_encoders':onehot_encoders, 'faiss_index':faiss_index}, file)

def load_embeddings(file_path):
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    return data['embeddings'], data['onehot_encoders'], data['faiss_index']



sbert_embeddings, faiss_index, mlb_dev, mlb_plat, mlb_genre = None, None, None, None, None
def init_sbert_faiss(games, weights):
    global sbert_embeddings, faiss_index, mlb_dev, mlb_plat, mlb_genre

    os.makedirs(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'embeddings')), exist_ok=True)
    embedding_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'embeddings', 'sbert_embeddings.pkl'))

    if os.path.exists(embedding_filepath):
        print('Loading SBERT embeddings...')
        sbert_embeddings, encoders, faiss_index = load_embeddings(embedding_filepath)
        mlb_dev, mlb_plat, mlb_genre = encoders['mlb_dev'], encoders['mlb_plat'], encoders['mlb_genre']
    
    else:
        print('Creating new embeddings...')
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode(games['Title'] +  ' ' + games['Summary'], show_progress_bar=True, normalize_embeddings=False)
        mlb_dev, mlb_plat, mlb_genre = MultiLabelBinarizer(), MultiLabelBinarizer(), MultiLabelBinarizer()
        developer_onehot, platform_onehot, genre_onehot = mlb_dev.fit_transform(games['Developers']), mlb_plat.fit_transform(games['Platforms']), mlb_genre.fit_transform(games['Genres'])
        sbert_embeddings = normalize(np.hstack((
                            weights[0] * embeddings,
                            weights[1] * developer_onehot,
                            weights[2] * platform_onehot,
                            weights[3] * genre_onehot
                            )), norm='l2', axis=1)
        faiss_index = faiss.IndexFlatIP(sbert_embeddings.shape[1])
        faiss_index.add(sbert_embeddings)
        save_embeddings(sbert_embeddings, {'mlb_dev':mlb_dev, 'mlb_plat':mlb_plat, 'mlb_genre':mlb_genre}, faiss_index, embedding_filepath)



def retrieve_top_k_faiss(query, top_k=100):
    global sbert_embeddings, faiss_index, mlb_dev, mlb_plat, mlb_genre

    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(query['Processed'], show_progress_bar=True, normalize_embeddings=False)
    developer_onehot = mlb_dev.transform(np.array([query['Developers']]).reshape(1, -1))
    platform_onehot = mlb_plat.transform(np.array([query['Platforms']]).reshape(1, -1))
    genre_onehot = mlb_genre.transform(np.array([query['Genres']]).reshape(1, -1))

    query_embeddings = normalize(np.hstack((
                    embeddings.reshape(1, -1),
                    developer_onehot,
                    platform_onehot,
                    genre_onehot
                    )), norm='l2', axis=1)

    distance, index = faiss_index.search(query_embeddings, top_k)
    distance, index = distance.flatten(), index.flatten()

    output = []
    for d, i in zip(distance, index):
        # filter out documents with score 0
        if d == 0:
            continue
        output.append((query['Processed'], doc_titles[i], i, d))

    return output



bm25_models = None
def init_bm25_models(documents):
    global bm25_models
    bm25_models = [
        BM25Okapi(documents['Title'].apply(lambda doc: tokenize(doc)).tolist(), k1=1.6, b=0.4),
        BM25Okapi(documents['Developers'].apply(lambda doc: tokenize(doc)).tolist(), k1=1.2, b=0.3),
        BM25Okapi(documents['Summary'].apply(lambda doc: tokenize(doc)).tolist(), k1=0.8, b=0.6),
        BM25Okapi(documents['Platforms'].apply(lambda doc: tokenize(doc)).tolist(), k1=1.4, b=0.2),
        BM25Okapi(documents['Genres'].apply(lambda doc: tokenize(doc)).tolist(), k1=1.4, b=0.2),
    ]



def retrieve_top_k_bm25_new(processed_query, top_k=100):
    global bm25_models, BM25_weights, doc_titles
    query = tokenize(processed_query['Processed'])
    query_original = tokenize(processed_query['Original'])
    scores = np.zeros((len(bm25_models), len(doc_titles)))
    score_details = []
    for i, model in enumerate(bm25_models):
        # for title we use the original query
        if i == 0:
            model_score = model.get_scores(query_original)
        else:
            model_score = model.get_scores(query)
        score_details.append(model_score.tolist())
        scores[i] = model_score * BM25_weights[i]
    scores = np.sum(scores, axis=0)
    score_details = np.column_stack(score_details)
    ranked = sorted(zip(enumerate(doc_titles), scores, score_details), key=lambda zipper: zipper[1], reverse=True)
    ranked_topk = ranked[:top_k]
    output = []
    details_output = []
    for k in ranked_topk:
        doc_id, doc_title, score, details = k[0][0], k[0][1], k[1], k[2]
        # filter out documents with score 0
        if score == 0:
            continue
        details_output.append(details)
        output.append((processed_query['Processed'], doc_title, doc_id, score))
    return output, details_output, scores, score_details



BM25_weights, doc_titles = None, None
def init(games_bm25, games_SBERT, SBERT_weights, bm25_weights):
    global BM25_weights, doc_titles
    BM25_weights = bm25_weights
    doc_titles = games_bm25['Title']

    init_bm25_models(games_bm25)
    init_sbert_faiss(games_SBERT, SBERT_weights)



def execute(query, top_k=100):
    topk_bm25, topk_bm25_scores, scores, score_details = retrieve_top_k_bm25_new(query, top_k=top_k)
    topk_faiss = retrieve_top_k_faiss(query, top_k=top_k * 3)

    topk_bm25_df = pd.DataFrame(topk_bm25, columns=['Query','Title','ID','BM25 Score'])
    topk_bm25_df['BM25_Scores'] = topk_bm25_scores
    
    topk_faiss_df = pd.DataFrame(topk_faiss, columns=['Query','Title','ID', 'SBERT Score']).drop(columns=['Title'])

    results = pd.merge(topk_bm25_df, topk_faiss_df, on=['Query', 'ID'], how='outer').fillna(0)
    # populate BM25 Score for FAISS results
    results['BM25 Score'] = results.apply(lambda row: row['BM25 Score'] if row['BM25 Score'] > 0 else scores[row['ID']], axis=1)

    return results