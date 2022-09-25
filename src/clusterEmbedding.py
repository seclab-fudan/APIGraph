#! /usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Created on 2020-08-16

@author: mingo
@module: 
'''

import os
import pickle
import numpy as np 
from sklearn.cluster import KMeans

cluster_k = 2000

def clusterEmbedding():
    with open('res/method_entity_embedding_TransE.pkl', 'rb') as f:
        entity_embedding = pickle.load(f)

    embeddings_id_entity_mapping = {}
    embeddings = []

    id = 0
    for entity, embedding in entity_embedding.items():
        embeddings_id_entity_mapping[id] = entity
        embeddings.append(embedding)
        id += 1

    print('\n=========== clustering through k-means ============\n')
    embeddings = np.array(embeddings)
    y_pred = KMeans(n_clusters=cluster_k, random_state=0).fit_predict(embeddings)
    
    cluster_method = {}
    idx = 0
    for y in y_pred:
        method = embeddings_id_entity_mapping[idx]
        if y not in cluster_method:
            cluster_method[y] = [method]
        else:
            cluster_method[y].append(method)
        idx += 1
    print(len(cluster_method))
    method_cluster_mapping = {}
    cluster_api_mapping = {}
    for key in cluster_method:
        for method in cluster_method[key]:
            method_cluster_mapping[method] = key
            if cluster_api_mapping.get(key, None) == None:
                cluster_api_mapping[key] = method

    with open('res/method_cluster_mapping_%d.pkl' % (cluster_k), 'wb') as f:
        pickle.dump(method_cluster_mapping, f, protocol = 2)

    with open('res/cluster_api_mapping_%d.pkl' % cluster_k, 'wb') as f:
        pickle.dump(cluster_api_mapping, f, protocol = 2)

if __name__ == "__main__":
    clusterEmbedding()
