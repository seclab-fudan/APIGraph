#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2020-08-10

@author: mingo
@module: 
'''

import numpy as np
import random
import tensorflow as tf
import multiprocessing as mp
import math
import pickle
import os
import csv
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

class KnowledgeGraph:
    def __init__(self, data_dir, train_rate=0.8):
        self.data_dir = data_dir
        self.train_rate = train_rate
        
        self.entity_dict = {}
        self.relation_dict = {}
        
        self.train_data = []
        self.test_data = []
        self.all_data = []
        
        self.generating = True
        
        self.load_dicts()
    
    def load_dicts(self):
        entity_dict_filename = 'entities.txt'
        relation_filename = 'relations.txt'
        
        with open(self.data_dir + entity_dict_filename) as entity_dict_file:
            i = 0
            reader = csv.reader(entity_dict_file) 
            for row in reader:
                entity = row[0]
                i += 1
                self.entity_dict[i] = entity 
        
        self.n_entity = len(self.entity_dict) + 1
        self.entity = np.arange(self.n_entity).tolist()
        
        relation_type =  {
            'function_of':1,
            'class_of':2,
            'inheritance':3,
            'uses_parameter':4,
            'returns':5,
            'throws':6,
            'alternative':7,
            'conditional':8,
            'refers_to':9,
            'uses_permission':10,
        }
        
        for k,v in relation_type.items():
            self.relation_dict[v] = k
                
        self.n_relation = len(self.relation_dict) + 1
        with open(self.data_dir + relation_filename) as relation_file:
            for line in relation_file:
                if random.random() < self.train_rate:
                    temp = line.strip().split(',')
                    self.train_data.append((int(temp[0]), int(temp[2]), int(temp[1])))
                else:
                    temp = line.strip().split(',')
                    self.test_data.append((int(temp[0]), int(temp[2]), int(temp[1])))
                
                self.all_data.append((int(temp[0]), int(temp[2]), int(temp[1])))
        
        self.train_data_set = set(self.train_data)
        
        self.n_train_triple = len(self.train_data)
        self.n_test_triple = len(self.test_data)
        self.n_triple = len(self.all_data)
    
    def next_raw_batch(self, batch_size, n_epoch):
        start = 0
        rand_idx = np.random.permutation(self.n_train_triple)
        
        count = 0
        while count < n_epoch:

            end = min(start + batch_size, self.n_train_triple)

            yield [self.train_data[i] for i in rand_idx[start:end]]
            
            if end == self.n_train_triple:
                start = 0
                rand_idx = np.random.permutation(self.n_train_triple)
                count += 1
            else:
                start = end
    
    def generate_train_batch(self, in_queue, out_queue):
        while True:
            raw_batch = in_queue.get()
            
            if raw_batch is None:
                return
            else:
                batch_pos = raw_batch
                batch_neg = []
                corrupt_head_prob = np.random.binomial(1, 0.5)
                for head, tail, relation in batch_pos:
                    head_neg = head
                    tail_neg = tail
                    while True:
                        if corrupt_head_prob:
                            head_neg = random.choice(self.entity)
                        else:
                            tail_neg = random.choice(self.entity)
                        
                        if (head_neg, tail_neg, relation) not in self.train_data_set:
                            break
                            
                    batch_neg.append((head_neg, tail_neg, relation))
                    
                out_queue.put((batch_pos, batch_neg))

class TransE:
    def __init__(self, kg: KnowledgeGraph, embed_dim=20, margin_value=2.0, learning_rate=0.1):
        self.kg = kg
        self.sess = tf.Session()
        
        self.embed_dim = embed_dim
        self.margin_value = margin_value
        self.learning_rate = learning_rate
        
        self.build_model()
        
        
    def build_model(self):
        with tf.variable_scope('TransE'):
            self.triple_pos = tf.placeholder(dtype=tf.int32, shape=[None, 3])
            self.triple_neg = tf.placeholder(dtype=tf.int32, shape=[None, 3])
            self.margin = tf.placeholder(dtype=tf.float32, shape=[None])
            
            bound = 6 / math.sqrt(self.embed_dim)
            self.embed_initializer = tf.random_uniform_initializer(minval=-bound, maxval=bound)
            
            self.entity_embedding_raw = tf.get_variable(name='entity_embedding_raw', shape=[self.kg.n_entity, self.embed_dim], initializer=self.embed_initializer)
            self.relation_embedding_raw = tf.get_variable(name='relation_embedding_raw', shape=[self.kg.n_relation, self.embed_dim], initializer=self.embed_initializer)
            
            self.entity_embedding = tf.nn.l2_normalize(self.entity_embedding_raw, dim=1)
            self.relation_embedding = tf.nn.l2_normalize(self.relation_embedding_raw, dim=1)
            
            self.head_pos = tf.nn.embedding_lookup(self.entity_embedding, self.triple_pos[:, 0])
            self.tail_pos = tf.nn.embedding_lookup(self.entity_embedding, self.triple_pos[:, 1])
            self.relation_pos = tf.nn.embedding_lookup(self.relation_embedding, self.triple_pos[:, 2])
            
            self.head_neg = tf.nn.embedding_lookup(self.entity_embedding, self.triple_neg[:, 0])
            self.tail_neg = tf.nn.embedding_lookup(self.entity_embedding, self.triple_neg[:, 1])
            self.relation_neg = tf.nn.embedding_lookup(self.relation_embedding, self.triple_neg[:, 2])            
            
            self.distance_pos = self.head_pos + self.relation_pos - self.tail_pos
            self.distance_neg = self.head_neg + self.relation_neg - self.tail_neg
            
            self.score_pos = tf.reduce_sum(tf.square(self.distance_pos), axis=1)
            self.score_neg = tf.reduce_sum(tf.square(self.distance_neg), axis=1)
            
            self.loss = tf.reduce_sum(tf.nn.relu(self.margin + self.score_pos - self.score_neg))
            self.opt = tf.train.AdamOptimizer(self.learning_rate).minimize(self.loss)
            
    
    def train(self, batch_size=1000, n_epoch=30):
        raw_batch_queue = mp.Queue()
        train_batch_queue = mp.Queue()
        
        for _ in range(n_epoch):
            mp.Process(target=self.kg.generate_train_batch, kwargs={'in_queue': raw_batch_queue, 'out_queue':train_batch_queue}).start()
        
        batch_count = 0
        for raw_batch in self.kg.next_raw_batch(batch_size, n_epoch):
            raw_batch_queue.put(raw_batch)
            batch_count += 1
        
        n_batch = int( batch_count / n_epoch)
        
        for _ in range(n_epoch):
            raw_batch_queue.put(None)
        
        self.sess.run(tf.global_variables_initializer())
        
        count = 0
        epoch_loss = 0
        epoch_len = 0
        
        for i in range(batch_count):
            
            batch_pos, batch_neg = train_batch_queue.get()
            
            batch_loss, _ = self.sess.run([self.loss, self.opt], feed_dict={self.triple_pos: batch_pos, self.triple_neg: batch_neg, self.margin: [self.margin_value] * len(batch_pos)})
            
            epoch_loss += batch_loss
            epoch_len += len(batch_pos)
            
            if i % n_batch == 0:
                print('epoch %d, loss=%.6f'%(count, epoch_loss / epoch_len))
                epoch_loss = 0
                epoch_len = 0
                count += 1
                
                
    def get_embeddings(self):
        embeded_results = self.sess.run(self.entity_embedding)
        return embeded_results

def run_TransE():
    the_dim=10
    data_path = 'res/'
    KG = KnowledgeGraph(data_path)
    model = TransE(KG, embed_dim=the_dim)
    model.train(batch_size=100, n_epoch=100)
    embeddings = model.get_embeddings()
    embeddings[0,:] = np.zeros(the_dim)
    method_entity_embedding={}
    with open(data_path + 'entities.txt', 'r') as f:
        i = 0
        for line in f:
            i += 1
            entity, typee = line.strip().split(',')
            if int(typee) == 3: # method
                method_entity_embedding[entity] = embeddings[i].tolist()
    
    with open(data_path + 'entity_embedding_TransE.pkl', 'wb') as embeddings_file:
        pickle.dump(embeddings, embeddings_file, protocol = 2)

    print('method length: %d' % len(method_entity_embedding))
    with open(data_path + 'method_entity_embedding_TransE.pkl', 'wb') as f:
        pickle.dump(method_entity_embedding, f, protocol = 2)

if __name__ == "__main__":
    run_TransE()
