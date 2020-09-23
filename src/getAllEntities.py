#! /usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Created on 2020-08-09

@author: mingo
@module: 
'''

import os
import csv
import json
import re
from tqdm import tqdm

def clean_entity_name(s):
    re_entity = re.compile(r'@B_\S+_E@')
    entities = re_entity.findall(s)
    if entities:
        entity = s[3:-3].replace('#', '.')
        return entity[:] if entity[0] != '.' else entity[1:]
    else:
        result = s
        if '<' in result:
            k = result.find('<')
            result = result[0:k]
        if '(' in result:
            k = result.find('(')
            result = result[0:k]

        result = result.replace('[]', '')
        if '#' in result:
            k1 = result.find('#')
            result = result[k1+1:]
        return result

def clean_method(method):
    method = method.replace('.<init>', '.init')
    return method

def get_package_name_from_class(class_name):
    for i, c in enumerate(class_name):
        if c.isupper():
           return class_name[0:i-1] 

def get_class_name_from_method(method_name):
    split_method = method_name.split('.')
    split_method.reverse()
    for i, part in enumerate(split_method):
        if part[0].isupper():
            class_start = i
    class_part = split_method[class_start: ]
    class_part.reverse()
    class_name = '.'.join(class_part)
    return class_name

def get_package_name_from_method(method_name):
    for i, c in enumerate(method_name):
        if c.isupper():
           return method_name[0:i-1] 

def getEntities(json_path, all_entities):
    if not os.path.exists(json_path):
        return
    
    data = json.load(open(json_path))
    class_name = clean_entity_name(data['ClassName'])
    package_name = get_package_name_from_class(class_name)
    
    if class_name:
        all_entities[class_name] = entity_type['class']
    if package_name:
        all_entities[package_name] = entity_type['package']
    
    for method in data['Functions']:
        method_name = class_name + '.' + method[0:method.find('(')]
        all_entities[method_name] = entity_type['method']

def loadPermissionsExternal(all_entities):
    permissions_path = 'res/all_permissions.txt'
    with open(permissions_path) as f:
        for line in f:
            permission = line.strip()
            if permission:
                all_entities[permission] = entity_type['permission']


def loadEntitiesInExternal(all_entites):
    external_file_path = 'res/extra_permission_relations.txt'
    with open(external_file_path) as f:
        for line in f:
            temp = line.strip().split(' ')
            method_name = clean_method(temp[0])
            all_entites[method_name] = entity_type['method']

def printEntitiesInfo(all_entites):
    count_entities = {}
    for t,v in entity_type.items():
        count_entities[v] = 0
    for entity in all_entites:
        count_entities[all_entites[entity]] += 1
    print('=========== entities =============')
    for t,v in entity_type.items():
        print('%s: %d' % (t, count_entities[v]))
                
def getAllEntities():
    global entity_type
    entity_type = {
        'package':1,
        'class':2,
        'method':3,
        'permission':4
    }
    all_entities = {}
    doc_json_dir = 'res/API_docs_in_json'

    json_files = os.listdir(doc_json_dir)
    for j_f in tqdm(json_files):
        j_f_path = os.path.join(doc_json_dir, j_f)
        getEntities(j_f_path, all_entities)
    loadPermissionsExternal(all_entities)
    loadEntitiesInExternal(all_entities)

    save_entities = [[entity, all_entities[entity]] for entity in all_entities]
    save_entities.sort(key = lambda x:x[1])
    
    with open('res/entities.txt','w',newline='') as f:
        writer = csv.writer(f)
        writer.writerows(save_entities)

    printEntitiesInfo(all_entities)

if __name__ == "__main__":
    getAllEntities()
