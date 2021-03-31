import json
import os
import re
from collections import Counter

def get_all_entity():
    rpath = './res/doc_in_json'
    jsonList = os.listdir(rpath)
    jsonList.sort(key=lambda x: x.split('.')[0])
    alldict = {"function":[], "macro":[], "method":[], "structure":[], "class":[], "interface":[], "header":[]}
    for js in jsonList:
        with open(os.path.join(rpath, js), 'r') as rf:
            apis = json.load(rf)
            for api in apis:
                name = api['Name']
                for k in alldict.keys():
                    if " "+k in name:
                        name = re.sub('\(.*?\)', '', name)
                        name = name.replace(" " + k, "").strip()
                        name = name.replace(" callback", "").strip()
                        alldict[k].append(name)
        if "_methods" not in js:
            dian = js.find('.json')
            header = js[:dian]
            alldict["header"].append(header)
    for k in alldict.keys():
        alldict[k] = list(set(alldict[k]))
    print(len(alldict['header']))
    return alldict


def entity_id():
    entities_dict = get_all_entity()
    wfile = './res/entity.txt'
    wf = open(wfile, 'w')
    ent_id = 1
    for key, value in entities_dict.items():
        if key in ['function', 'macro', 'method']:
            type_id = 1
        elif key == 'structure':
            type_id = 2
        elif key in ['class', 'interface']:
            type_id = 3
        elif key == 'header':
            type_id = 4
        else:
            type_id = 0
            print('!!!OUT OF TYPE!!!')
        for en in value:
            wf.write(en.lower()+","+str(type_id)+","+str(ent_id))
            wf.write('\n')
            ent_id += 1
    wf.close()

def get_ent_id():
    ent_id = {}
    with open('./res/entity.txt') as rf:
        for line in rf.readlines():
            res = line.strip().split(',')
            ent = res[0]
            id = res[2]
            ent_id[ent] = id
    return ent_id

def formatEXC(rfile):
    wfile = rfile.replace('.', '_format.')
    wf = open(wfile, 'w')
    with open(rfile, 'r') as rf:
        for line in rf.readlines():
            res = re.findall(r"'(.*?)'", line)
            wf.write(res[0]+','+res[1]+','+res[2])
            wf.write('\n')
    wf.close()

def entity_type():
    wfile = './res/entity_type.txt'
    with open(wfile, 'w') as wf:
        wf.write("function,1\n")
        wf.write("structure,2\n")
        wf.write("class,3\n")
        wf.write("header,4")

if __name__ == "__main__":
    dir = './res'
    if not os.path.exists(dir):
        os.makedirs(dir)
    entity_id()
    entity_type()
