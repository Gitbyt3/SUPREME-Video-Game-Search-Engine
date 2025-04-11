import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MultiLabelBinarizer, normalize
from sentence_transformers import SentenceTransformer
import faiss

def BM25_field_matrix(df, game_attribute, k_1=1.2, b=0.8, max_features=50000, min_df=2):
    documents = df[game_attribute].to_list()
    pipe = Pipeline([('count', CountVectorizer(max_features=max_features, min_df=min_df)), ('tfid', TfidfTransformer())]).fit(documents)
    term_doc_matrix = pipe['count'].transform(documents)
    doc_lengths, avg_dl, idfs, tfs = term_doc_matrix.sum(axis=1), np.mean(term_doc_matrix.sum(axis=1)), pipe['tfid'].idf_.reshape(1, -1), term_doc_matrix.multiply(1 / term_doc_matrix.sum(axis=1))
    numerator = (k_1 + 1) * tfs
    denominator = k_1 * ((1 - b) + b * (doc_lengths / avg_dl)) + tfs
    BM25 = numerator.multiply(1 / denominator)
    BM25 = BM25.multiply(idfs)
    vocab = pipe['count'].get_feature_names_out()
    vocab = {term:index for index, term in enumerate(vocab)}
    return BM25.tocsr(), vocab

def SBERT_embed_FAISS_index(games, weights):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(games['Title'] +  ' ' + games['Summary'], show_progress_bar=True, normalize_embeddings=False)
    mlb1, mlb2, mlb3 = MultiLabelBinarizer(), MultiLabelBinarizer(), MultiLabelBinarizer()
    developer_onehot, platform_onehot, genre_onehot = mlb1.fit_transform(games['Developers']), mlb2.fit_transform(games['Platforms']), mlb3.fit_transform(games['Genres'])
    doc_embeddings = normalize(np.hstack((
                        weights[0] * embeddings,
                        weights[1] * developer_onehot,
                        weights[2] * platform_onehot,
                        weights[3] * genre_onehot
                        )), norm='l2', axis=1)
    data_index = faiss.IndexFlatIP(doc_embeddings.shape[1])
    data_index.add(doc_embeddings)
    return data_index, mlb1, mlb2, mlb3

def retrieve_top_k_bm25(query, bm25_list, weights, doc_titles, top_k=100, epsilon=1e-6):
    def bm25_filtered(query, bm25):
        matrix, vocab = bm25
        query = query['Processed'].split(' ')
        query_tokens = [vocab[term] if term in vocab else 'OOV' for term in query]
        IV = [term for term in query_tokens if term != 'OOV']
        if len(IV) != 0:
            doc_scores = matrix[:, IV].sum(axis=1)
            if 'OOV' in query:
                doc_scores += np.full((matrix.shape[0], 1), epsilon)
        else:
            doc_scores = np.full((matrix.shape[0], 1), epsilon)
        return doc_scores
    bm25_weighted = np.zeros((bm25_list[0][0].shape[0], 1))
    for bm25, weight in zip(bm25_list, weights):
        bm25_weighted += weight * bm25_filtered(query, bm25)
    scores = np.ravel(bm25_weighted)
    ranked = sorted(zip(enumerate(doc_titles), scores), key=lambda zipper: zipper[1], reverse=True)
    ranked_topk = ranked[:top_k]
    output = []
    for k in ranked_topk:
        doc_id, doc_title, score = k[0][0], k[0][1], k[1]
        output.append((query['Processed'], doc_title, doc_id, score, 0))

    return output

def retrieve_top_k_faiss(query, faiss_index, mlb_dev, mlb_plat, mlb_genre, doc_titles, top_k=100):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    text_embeddings = model.encode(query['Processed'], show_progress_bar=True, normalize_embeddings=False)
    dev_onehot = mlb_dev.transform(np.array([query['Developers']]).reshape(1, -1))
    plat_onehot = mlb_plat.transform(np.array([query['Platforms']]).reshape(1, -1))
    genre_onehot = mlb_genre.transform(np.array([query['Genres']]).reshape(1, -1))

    query_embeddings = normalize(np.hstack((
                    text_embeddings.reshape(1, -1),
                    dev_onehot,
                    plat_onehot,
                    genre_onehot
                    )), norm='l2', axis=1)

    distance, index = faiss_index.search(query_embeddings, top_k)
    distance, index = distance.flatten(), index.flatten()

    output = []
    for d, i in zip(distance, index):
        output.append((query['Processed'], doc_titles[i], i, 0, d))

    return output

def init(games_bm25, games_SBERT, SBERT_weights):
    bm25_matrices = [
        BM25_field_matrix(games_bm25, 'Title', k_1=1.2, b=0.4, max_features=5000, min_df=1),
        BM25_field_matrix(games_bm25, 'Developers', k_1=1.1, b=0.3, max_features=4000, min_df=1),
        BM25_field_matrix(games_bm25, 'Summary', k_1=1.8, b=0.8, max_features=20000, min_df=2),
        BM25_field_matrix(games_bm25, 'Platforms', k_1=1.0, b=0.2, max_features=500, min_df=2),
        BM25_field_matrix(games_bm25, 'Genres', k_1=1.0, b=0.2, max_features=800, min_df=2)
                    ]
    index, mlb_dev, mlb_plat, mlb_genre = SBERT_embed_FAISS_index(games_SBERT, SBERT_weights)

    return bm25_matrices, index, mlb_dev, mlb_plat, mlb_genre

def execute(query, doc_titles, bm25_matrices, bm25_weights, faiss_index, mlb_dev, mlb_plat, mlb_genre, top_k=100):
    topk_bm25 = retrieve_top_k_bm25(query, bm25_matrices, bm25_weights, doc_titles)
    topk_faiss = retrieve_top_k_faiss(query, faiss_index, mlb_dev, mlb_plat, mlb_genre, doc_titles)
    topk_bm25_df = pd.DataFrame(topk_bm25, columns=['Query','Title','ID','BM25 Score','SBERT Score'])
    topk_faiss_df = pd.DataFrame(topk_faiss, columns=['Query','Title','ID','BM25 Score','SBERT Score'])
    results = pd.concat([topk_bm25_df, topk_faiss_df], axis=0).drop_duplicates(subset=['Query','ID']).sort_values(by='Query',ignore_index='True')

    return results