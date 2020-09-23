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
import spacy
import en_core_web_sm 
from tqdm import tqdm
from collections import Counter

def search_entity(entities, name):
    if name in entities:
        return name
    return ''

def clean_method(method):
    method = method.replace('.<init>', '.init')
    return method

def clean_entity_name(s):
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

# ignore base types
def not_base_type(substr):
    if ('int' not in substr) and ('boolean' not in substr) and ('float' not in substr) and ('String' not in substr) and ('byte' not in substr) and ('short' not in substr) and ('long' not in substr) and ('double' not in substr) and ('char' not in substr) and ('booleanValue' not in substr):
        return True
    else:
        return False
    
'''
Parse the function, return function_name and parameters.
Note: base type parameters are not concerned.
'''
def parse_function_name(function):
    k1 = function.find('(')
    k2 = function.find(')')
    function_name = function[0:k1]
    results = []
    
    if k2 == k1 + 1:
        return function_name, results
    else:
        substr = function[k1+1:k2].replace(' ', '')
        if ',' in substr:
            temp = substr.split(',')
            for t in temp:
                if not_base_type(t):
                    results.append(t) 
            return function_name, results   
        else:
            if not_base_type(substr):
                results.append(substr)
            return function_name, results

def get_package_name_from_class(class_name):
    for i, c in enumerate(class_name):
        if c.isupper():
           return class_name[0:i-1] 
        
def load_entities_from_file(path):
    i = 0
    with open(path) as f:
        reader = csv.reader(f) 
        for row in reader:
            entity = row[0]
            typee = int(row[1])
            entities_type_dict[typee].add(entity)
            if entity not in entity_id_mapping:
                i += 1
                entity_id_mapping[entity] = i 

def get_extra_permission_relations():
    extra_permission_file = 'res/extra_permission_relations.txt'
    with open(extra_permission_file) as f:
        for line in f:
            temp = line.strip().split(' ')
            method = clean_method(temp[0])
            permission = temp[2]
            if method in entity_id_mapping and permission in entity_id_mapping:
                entity_relations.add((entity_id_mapping[method], relation_type['uses_permission'], entity_id_mapping[permission]))


def define_templates():
    global priority_mattch, pattern_map

    priority_mattch=['uses_permission','returns','refers_to','alternative','conditional']
    pattern_map={}
    pattern_map['conditional']=[]
    pattern_map['refers_to']=[]
    pattern_map['alternative']=[]
    pattern_map['uses_permission']=[]
    pattern_map['returns']=[]

    # Return relation
    # format 1 'return (not by) REF'
    return_ref_re=re.compile('return (?:a|the) @B_.*_E@',re.IGNORECASE)
    pattern_map['returns'].append(return_ref_re)


    # Permission relation
    # format 1 'require Permission REF'
    require_permission_re=re.compile('require .*@B.*#permission#.*E@',re.IGNORECASE)
    pattern_map['uses_permission'].append(require_permission_re)


    # Reference relation
    # format 1 'see also REF'
    see_also_re=re.compile('see also @B_.*_E@',re.IGNORECASE)
    pattern_map['refers_to'].append(see_also_re)

    # format 2 'see REF'
    see_re=re.compile('see @B_.*_E@',re.IGNORECASE)
    pattern_map['refers_to'].append(see_re)

    # format 3 'query REF'
    query_re=re.compile('query @B_.*_E@',re.IGNORECASE)
    pattern_map['refers_to'].append(query_re)

    # format 4 'refer to REF'
    refer_to_re=re.compile('refer to @B_.*_E@',re.IGNORECASE)
    pattern_map['refers_to'].append(refer_to_re)

    # format 5 'returned by REF'
    returned_by_re=re.compile('return by @B_.*_E@',re.IGNORECASE)
    pattern_map['refers_to'].append(returned_by_re)


    # Conditional relation
    before_format='(?: before | after | when | in | between | to | from | if | whether | by )'
    be_format='be'

    # format 1 'Call/be Called/wait for/perform/check/use xxx before REF'
    call_before_re=re.compile('(?: call| {} call| wait for| perform| check| use).*{}@B_.*_E@'.format(be_format,before_format),re.IGNORECASE)
    pattern_map['conditional'].append(call_before_re)

    # format 2 'call REF after'
    call_after_re=re.compile('(?: call| {} call| wait for| perform| check| use).*@B_.*_E@{}'.format(be_format,before_format),re.IGNORECASE)
    pattern_map['conditional'].append(call_after_re)

    # format 3 'before xxx REF [not] exist/be called/be returned/fail '
    before_exist_re=re.compile('{}@B_.*_E@(?: exist| {} call| {} return| fail)'.format(before_format,be_format,be_format),re.IGNORECASE)
    pattern_map['conditional'].append(before_exist_re)

    # format 4 'before xxx call to REF'
    before_call_re=re.compile('(?:before |after |when |in |between |to |from |if |whether |by ).*call to.*@B_.*_E@',re.IGNORECASE)
    pattern_map['conditional'].append(before_call_re)

    # format 5 'REF should/may be called'
    should_be_called_re=re.compile('@B_.*_E@(?: should | may )be call',re.IGNORECASE)
    pattern_map['conditional'].append(should_be_called_re)

    # format 6 'REF must/should be called'
    must_be_called_re=re.compile('@B_.*_E@(?: must | should be ).*for.*{} call'.format(be_format),re.IGNORECASE)
    pattern_map['conditional'].append(must_be_called_re)

    # format 7 'following the call to REF'
    following_call_re=re.compile('follow .*call to .*@B_.*_E@',re.IGNORECASE)
    pattern_map['conditional'].append(following_call_re)

    # format 8 'by invoking/calling REF'
    invoke_relation_re=re.compile('By (?:invoke|call) @B_.*_E@',re.IGNORECASE)
    pattern_map['conditional'].append(invoke_relation_re)

    # format 9 'if xxx then xxx REF be returned/called'
    if_then_called_re=re.compile('if .*then @B_.*_E@ {} (?:return |call )'.format(be_format),re.IGNORECASE)
    pattern_map['conditional'].append(if_then_called_re)

    # format 10 'if xxx then use/call REF'
    if_call_re=re.compile('if .*then (?:use |call )@B_.*_E@',re.IGNORECASE)
    pattern_map['conditional'].append(if_call_re)

    # format 11 'if xxx be/calling REF'
    if_calling_re=re.compile('if .* (?:be|call) .*@B_.*_E@',re.IGNORECASE)
    pattern_map['conditional'].append(if_calling_re)

    # format 12 'require (not permission) REF'
    require_not_permission_re=re.compile('(?im)^(?=.*?(?:require))(?!.*?(?:permission)).*',re.IGNORECASE)
    pattern_map['conditional'].append(require_not_permission_re)

    # format 13 'be initialized with REF'
    initialized_with_re=re.compile('initialize with.*@B_.*_E@',re.IGNORECASE)
    pattern_map['conditional'].append(initialized_with_re)

    # format 14 'register with REF'
    register_with_re=re.compile('register with @B_.*_E@',re.IGNORECASE)
    pattern_map['conditional'].append(register_with_re)




    # Alternative relation
    # format 1 'replaced by REF'
    replace_by_re=re.compile('.*replace by @B_.*_E@',re.IGNORECASE)
    pattern_map['alternative'].append(replace_by_re)

    # format 2 'deprecated,use REF'
    deprecated_use_re=re.compile('deprecat.* use @B_.*_E@',re.IGNORECASE)
    pattern_map['alternative'].append(deprecated_use_re)

    # format 3 'use REF instead'
    use_only_instead_re=re.compile('use @B_.*_E@ instead',re.IGNORECASE)
    pattern_map['alternative'].append(use_only_instead_re)

    # format 4 'use instead of REF'
    use_instead_of_re=re.compile('use instead of @B_.*_E@',re.IGNORECASE)
    pattern_map['alternative'].append(use_instead_of_re)

    # format 5 'use REF directly'
    use_directly_re=re.compile('use @B_.*_E@ directly',re.IGNORECASE)
    pattern_map['alternative'].append(use_directly_re)

    # format 6 'when REF is used instead'
    when_used_instead_re=re.compile('when @B_.*_E@ {} use instead'.format(be_format),re.IGNORECASE)
    pattern_map['alternative'].append(when_used_instead_re)

    # format 7 'REF can be used to'
    can_be_used_to_re=re.compile('@B_.*_E@ can be use to',re.IGNORECASE)
    pattern_map['alternative'].append(can_be_used_to_re)


    # Alternative relation 2
    # format 1 'REF does the reverse'
    does_reverse_re=re.compile('@B_.*_E@.* do the reverse',re.IGNORECASE)
    pattern_map['alternative'].append(does_reverse_re)

    # format 2 'equivalent/equivalently to call/of calling to REF'
    equvialent_to_re=re.compile('(?:equivalent|equivalently) (?:to call|of call to) @B_.*_E@',re.IGNORECASE)
    pattern_map['alternative'].append(equvialent_to_re)

    # format 3 'differences from xx REF'
    difference_from_re=re.compile('(?:difference|different) from @B_.*_E@',re.IGNORECASE)
    pattern_map['alternative'].append(difference_from_re)

    # format 4 'including REF'
    including_re=re.compile('include @B_.*_E@',re.IGNORECASE)
    pattern_map['alternative'].append(including_re)

    # format 5 'associated with the xx REF'
    associated_with_re=re.compile('associate with .*@B_.*_E@',re.IGNORECASE)
    pattern_map['alternative'].append(associated_with_re)

    # format 6 'similar to/like REF'
    similar_to_re=re.compile('similar (?:to|like) @B_.*_E@',re.IGNORECASE)
    pattern_map['alternative'].append(similar_to_re)

    # format 7 'like/unlike REF'
    like_re=re.compile('(?:like|unlike) @B_.*_E@',re.IGNORECASE)
    pattern_map['alternative'].append(like_re)

    # format 8 'In contrast to REF'
    contrast_to_re=re.compile('in contrast to @B_.*_E@',re.IGNORECASE)
    pattern_map['alternative'].append(contrast_to_re)

    # format 9 'be smaller than REF'
    smaller_than_re=re.compile('{} small than @B_.*_E@'.format(be_format),re.IGNORECASE)
    pattern_map['alternative'].append(smaller_than_re)



def method_in_which_class(class_set, method):
    while method and '.' in method:
        method = '.'.join(method.split('.')[:-1])
        if method in class_set:
            return method
    
# find out entities from description
def find_entities_in_description(description):
    entities = re_entity.findall(description)
    ret = []
    for entity in entities:
        entity = entity[3:-3].replace('#', '.')
        ret.append(entity[:] if entity[0] != '.' else entity[1:])
    return ret

# give pattern and text output entities list if match
def match_pattern(cur_pattern, text):
    match_list= cur_pattern.findall(text)
    matched_entities=[]
    for each_match in match_list:
        # print(each_match)
        matched_entities.extend(find_entities_in_description(each_match))
    return matched_entities


def extract_relation_in_description(api, desc):
    res = [] # [entity, relation]
    if not api or not desc:
        return res

    desc=desc.replace('@B_','b_b_').replace('_E@','_e_e')

    doc = nlp(desc)
    sentences = list(doc.sents)

    # for every sentence in the description. 
    for sentence in sentences:
        entities = find_entities_in_description(sentence.text.replace('b_b_','@B_').replace('_e_e','_E@'))
        if not entities:
            continue
        
        sentencelist=list()
        for token in sentence:
            if token.text.startswith("b_b_") and "_e_e" in token.text:
                sentencelist.append(token.text.replace('b_b_','@B_').replace('_e_e','_E@'))
            else:
                sentencelist.append(token.lemma_)
        sentence2 = " ".join(sentencelist)


        recorddict={}
        for i in entities:
            recorddict[i]=1
        for curtype in priority_mattch:
            k=curtype
            vv=pattern_map[k]
            find_status2=0
            
            for eachpattern2 in vv:
                etList2 = match_pattern(eachpattern2,sentence2)

                if not etList2:
                    continue
                for e in etList2:
                    recorddict[e]=0
                    res.append([e, k])
                find_status2=1
                break


            if find_status2:
                break     
    return res


def get_relations_from_json(json_path):
    if not os.path.exists(json_path):
        return
    data = json.load(open(json_path))
    class_name = clean_entity_name(data['ClassName'])
    package_name = get_package_name_from_class(class_name)
    
    # inheritance relation
    inheritance = data['Inheritance']
    for i in inheritance:
        father_name = search_entity(entity_id_mapping, clean_entity_name(i))
        if (len(father_name) > 0) and (father_name not in class_name) and  father_name != 'java.lang.Object':
            entity_relations.add((entity_id_mapping[class_name], relation_type['inheritance'], entity_id_mapping[father_name]))
    
    for method in data['Functions']:
        method_name, params = parse_function_name(method)
    
        method_name = class_name + '.' + method_name    
        
        # function_of and class_of relation
        if class_name in entity_id_mapping:
            entity_relations.add((entity_id_mapping[method_name], relation_type['function_of'], entity_id_mapping[class_name]))
            if package_name in entity_id_mapping:
                entity_relations.add((entity_id_mapping[class_name], relation_type['class_of'], entity_id_mapping[package_name]))
        
        # uses_paramter relation
        for param in params:
            param_class = search_entity(entity_id_mapping, clean_entity_name(param))
            if param_class:
                param_pkg = search_entity(entity_id_mapping, get_package_name_from_class(param_class))
                if param_pkg == package_name:
                    continue
                if param_pkg in ["java.lang.Object", "java.lang.CharSequence", "java.util.List"]:
                    continue
                entity_relations.add((entity_id_mapping[method_name], relation_type['uses_parameter'], entity_id_mapping[param_class]))
        
        method_details = data['Functions'][method]
        # return relation
        ######################### return relation in json is not complete ###############
        returns = method_details['Returns']
        for r in returns:
            r_name = search_entity(entity_id_mapping, clean_entity_name(r[0]))
            if r_name:
                r_name_pkg = search_entity(entity_id_mapping, get_package_name_from_class(r_name))
                if r_name_pkg == package_name:
                    continue
                if r_name == "java.lang.String":
                    continue
                entity_relations.add((entity_id_mapping[method_name], relation_type['returns'], entity_id_mapping[r_name]))
        
        # throw relation
        throws = method_details['Throws']
        for t in throws:
            t_name = search_entity(entity_id_mapping, clean_entity_name(t[0]))
            if t_name:
                t_name_pkg = search_entity(entity_id_mapping, get_package_name_from_class(t_name))
                if t_name_pkg == package_name:
                    continue
                entity_relations.add((entity_id_mapping[method_name], relation_type['throws'], entity_id_mapping[t_name]))
        
        # use_permission relation
        permissions = method_details['Permissions']
        for p in permissions:
            p_name = search_entity(entity_id_mapping, clean_entity_name(p).replace('android.Manifest.permission', 'android.permission'))
            if p_name:
                entity_relations.add((entity_id_mapping[method_name], relation_type['uses_permission'], entity_id_mapping[p_name]))
        
        # refer_to relation
        seealsos = method_details['SeeAlso']
        for seealso in seealsos:
            sa_name = clean_entity_name(seealso)
            if sa_name not in entity_id_mapping:
                sa_name = method_in_which_class(entities_type_dict[2] ,sa_name)
            if sa_name and sa_name != method_name:
                entity_relations.add((entity_id_mapping[method_name], relation_type['refers_to'], entity_id_mapping[sa_name]))
        
        # relations in description
        description = method_details['Description']

        relations = extract_relation_in_description(method_name, description)
        
        for entity, relation in relations:
            if entity in entity_id_mapping:
                entity_relations.add((entity_id_mapping[method_name], relation_type[relation], entity_id_mapping[entity]))
        


def save_relations():
    id_entity_mapping = {}
    for entity,entity_id in entity_id_mapping.items():
        id_entity_mapping[entity_id] = entity
    
    id_relation_mapping = {}
    for relation, relation_id in relation_type.items():
        id_relation_mapping[relation_id] = relation
    
    save_relations = [list(_) for _ in entity_relations]
    save_relations.sort(key = lambda x:x[0])
    save_relations_readable = [[id_entity_mapping[_[0]], id_relation_mapping[_[1]], id_entity_mapping[_[2]]] for _ in save_relations]
    
    with open('res/relations.txt', 'w', newline = '') as f:
        writer = csv.writer(f) 
        writer.writerows(save_relations)
    
    with open('res/relations_readable.txt', 'w', newline = '') as f:
        writer = csv.writer(f) 
        writer.writerows(save_relations_readable)
    
    c_relation = Counter(_[1] for _ in save_relations_readable)
    print('\n\n=========== relations ==========')
    for r,c in c_relation.items():
        print('%s: %d' % (r,c))

def getAllRelations():
    global relation_type, entities_type_dict, entity_id_mapping, entity_relations, nlp, re_entity
    relation_type = {
        'function_of':1,
        'class_of':2,
        'inheritance':3,
        'uses_parameter':4,
        'returns':5,
        'throws':6,
        'alternative':7,
        'conditional':8,
        'refers_to':9,
        'uses_permission':10
    }
    entities_type_dict = {
        1: set(), # package
        2: set(), # class
        3: set(), # method
        4: set(), # permission
        5: set() # others
    }
    entity_id_mapping = {}
    entity_relations = set()

    nlp = en_core_web_sm.load()
    re_entity = re.compile(r'@B_\S+_E@')

    load_entities_from_file('res/entities.txt')
    define_templates()

    get_extra_permission_relations()

    doc_json_dir = 'res/API_docs_in_json'
    all_json_files = [f for f in os.listdir(doc_json_dir) if f.endswith(".json")]
    print('All json files: %d' % len(all_json_files))
    
    for j_f in tqdm(all_json_files):
        j_f_path = os.path.join(doc_json_dir, j_f)
        get_relations_from_json(j_f_path)
    
    save_relations()           

if __name__ == "__main__":
    getAllRelations()
