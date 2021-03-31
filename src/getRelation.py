import http
import json
import os
import re
import http
import urllib.request
import urllib.error

from bs4 import BeautifulSoup

relation2id = {"function_of":1, "class_of":2, "inheritance":3, "uses_parameter":4, "returns":5,
               "conditional":6, "alternative":7, "refers_to":8}

def find_all(sub, s):
    index_list = []
    index = s.find(sub)
    while index != -1:
        index_list.append(index)
        index = s.find(sub, index + 1)
    return index_list

def function_of():
    rset = set()
    rpath = './res/doc_in_json'
    jsonList = os.listdir(rpath)
    jsonList.sort(key=lambda x: x.split('.')[0])
    for js in jsonList:
        rf = open(os.path.join(rpath, js), 'r')
        apis = json.load(rf)
        for api in apis:
            header = api['Head'].lower()
            name = api['Name'].lower()
            if " function" in name or " macro" in name:
                rset.add((name, "function_of", header))
            if " method" in name:
                name = getformatted(name)
                # method_class
                me_start = name.find("::")
                classname = name[:me_start]
                rset.add((name, "function_of", classname))

    return rset

def inheritance():
    rset = set()
    rpath = './res/doc_in_json'
    jsonList = os.listdir(rpath)
    jsonList.sort(key=lambda x: x.split('.')[0])
    for js in jsonList:
        rf = open(os.path.join(rpath, js), 'r')
        apis = json.load(rf)
        for api in apis:
            name = api['Name']
            if " class" in name or " interface" in name:
                inhe = api['Inheritance']
                name = name.replace(" class", "").strip()
                name = name.replace(" interface", "").strip()
                rset.add((name, "inheritance", inhe))
    return rset

def uses_parameter():
    rdir = 'res/doc_in_json'
    rfiles = ['class_methods.json', 'interface_methods.json']
    uses_parameter = set()
    for js in rfiles:
        with open(os.path.join(rdir, js), 'r') as rf:
            apis = json.load(rf)
            for api in apis:
                name = api['Name']
                end = name.find(" method")
                purename = name[: end].strip()

                # get uses_parameter
                if "Syntax" in api:
                    syn = api['Syntax']
                    i = syn.find("(")
                    j = syn.find(")")
                    if j == i + 1:
                        continue
                    inkuohao = syn[i + 1:j]
                    paras = inkuohao.split(",") 
                    for para in paras:
                        parts = para.split(" ")
                        if len(parts) > 2:
                            ty = ""
                            for i in range(0, len(parts) - 1):
                                ty += parts[i] + " "
                            ty = ty.replace("const", "")
                            ty = ty.replace("*", "")
                            ty = ty.replace("&", "")
                            ty = ty.replace("volatile", "")
                            if ty.strip() != "" and ty.strip() != "...":
                                uses_parameter.add((purename, "uses_parameter", ty.lower().strip()))
                        else:
                            ty = parts[0].replace("&", "")
                            ty = ty.replace("const", "")
                            ty = ty.replace("*", "")
                            ty = ty.replace("volatile", "")
                            if ty.strip() != "" and ty.strip() != "...":
                                uses_parameter.add((purename, "uses_parameter", ty.lower().strip()))

    rpath = './res/doc_in_json'
    jsonList = os.listdir(rpath)
    jsonList.sort(key=lambda x: x.split('.')[0])
    for js in jsonList:
        if js in rfiles:
            continue
        rf = open(os.path.join(rpath, js), 'r')
        apis = json.load(rf)
        for api in apis:
            header = api['Head'].lower()
            name = api['Name'].lower()
            # get uses_parameter
            if " macro" in name:
                if "Parameters" in api:
                    ps = api['Parameters']
                    for p in ps:
                        if p[1] != " ":
                            tp = p[1].replace("*", "")
                            tp = tp.replace("const", "").strip()
                            tp = tp.replace("&", "")
                            tp = tp.replace("@++b_", "")
                            tp = tp.replace("_b++@", "")
                            if "@++u_" in tp:
                                ubstr = tp.replace("@++u_", "")
                                ubstr = tp.replace("_u++@", "")
                                x = ubstr.find("_")
                                ubstr = ubstr[x + 1:]
                                ubstr.replace("_", " ")
                                ubstr.replace("$", "_")
                                if ubstr.strip() != "":
                                    uses_parameter.add((name, "uses_parameter", ubstr.lower().strip()))
            if " function" in name:
                if "Syntax" in api:
                    syn = api['Syntax']
                    i = syn.find("(")
                    j = syn.find(")")
                    inkuohao = syn[i + 1:j]
                    paras = inkuohao.split(",")
                    for para in paras:
                        parts = para.split(" ")
                        if len(parts) > 2:
                            ty = ""
                            for i in range(0, len(parts) - 1):
                                ty += parts[i] + " "
                            ty = ty.replace("const", "")
                            ty = ty.replace("*", "")
                            ty = ty.replace("&", "")
                            ty = ty.replace("volatile", "")
                            if ty.strip() != "" and ty.strip() != "...":
                                uses_parameter.add((name, "uses_parameter", ty.lower().strip()))
                        else:
                            ty = parts[0].replace("&", "")
                            ty = ty.replace("const", "")
                            ty = ty.replace("*", "")
                            ty = ty.replace("volatile", "")
                            if ty.strip() != "" and ty.strip() != "...":
                                uses_parameter.add((name, "uses_parameter", ty.lower().strip()))
    return uses_parameter

def returns():
    rdir = 'res/doc_in_json'
    rfiles = ['class_methods.json', 'interface_methods.json']
    returns = set()
    for js in rfiles:
        with open(os.path.join(rdir, js), 'r') as rf:
            apis = json.load(rf)
            for api in apis:
                name = api['Name']
                end = name.find(" method")
                purename = name[: end].strip()
                # get returns
                if "Syntax" in api:
                    syn = api['Syntax']
                    rettype = syn.split(" ")[0]
                    rettype = rettype.replace("&", "")
                    if rettype.strip() != "":
                        returns.add((purename, "returns", rettype.lower().replace("winapi", "").strip()))

    rpath = './res/doc_in_json'
    jsonList = os.listdir(rpath)
    jsonList.sort(key=lambda x: x.split('.')[0])
    for js in jsonList:
        if js in rfiles:
            continue
        rf = open(os.path.join(rpath, js), 'r')
        apis = json.load(rf)
        for api in apis:
            header = api['Head'].lower()
            name = api['Name'].lower()
            # get returns
            if "Syntax" in api:
                syn = api['Syntax']
                # callback function
                if "callback function" in name:
                    t = syn.replace("\n", "")
                    fenhao = t.find(";")
                    t = t[fenhao + 1:]
                    rettype = t.split(" ")[0]
                    rettype = rettype.replace("&", "")
                    if rettype.strip() != "":
                        returns.add((name, "returns", rettype.lower().replace("winapi", "").strip()))
                elif " function" in name or " macro" in name:
                    rettype = syn.split(" ")[0]
                    rettype = rettype.replace("&", "")
                    if rettype.strip() != "":
                        returns.add((name, "returns", rettype.lower().replace("winapi", "").strip()))
        rf.close()
    return returns

def refers_to():
    rdir = 'res/doc_in_json'
    rfiles = ['class_methods.json', 'interface_methods.json']
    refers_to = set()
    for js in rfiles:
        with open(os.path.join(rdir, js), 'r') as rf:
            apis = json.load(rf)
            for api in apis:
                name = api['Name']
                end = name.find(" method")
                purename = name[: end].strip()
                # get refers_to
                if "See also" in api:
                    sa = api['See also']
                    for key, value in sa.items():
                        if value:
                            for item in value:
                                if item:
                                    refers_to.add((purename, "refers_to", item.lower()))

    rpath = './res/doc_in_json'
    jsonList = os.listdir(rpath)
    jsonList.sort(key=lambda x: x.split('.')[0])
    for js in jsonList:
        if js in rfiles:
            continue
        rf = open(os.path.join(rpath, js), 'r')
        apis = json.load(rf)
        for api in apis:
            name = api['Name'].lower()
            if "See also" in api:
                sa = api['See also']
                for key, value in sa.items():
                    if value:
                        for item in value:
                            if item:
                                refers_to.add((name, "refers_to", item.lower()))
        rf.close()
    return refers_to

def class_of():
    rpath = './res/doc_in_json'
    jsonList = os.listdir(rpath)
    jsonList.sort(key=lambda x: x.split('.')[0])

    wheader = set()
    for js in jsonList:
        rf = open(os.path.join(rpath, js), 'r')
        apis = json.load(rf)
        for api in apis:
            if " class" in api['Name'] or " interface" in api['Name']:
                header = api['Head'].lower()
                name = api['Name'].lower()
                wheader.add((name, "class_of", header))
        rf.close()
    return wheader

def getDesc():
    rpath = './res/doc_in_json'
    jlist = os.listdir(rpath)

    wdict = {}
    for js in jlist:
        rf = open(os.path.join(rpath, js), 'r')
        apis = json.load(rf)
        for api in apis:
            desc = para_desc = ret_desc = remark = ""
            apiname = api['Name']
            desc = api['Description']
            if "Parameters" in api:
                para_desc_list = [d[2] for d in api['Parameters']]
                para_desc = "\n".join(para_desc_list)
            if "Return value" in api:
                ret_desc = api['Return value']['desc']
            if "Remarks" in api:
                remark = api['Remarks']
            wdict[apiname] = desc + "\n\n" + para_desc + '\n\n' + ret_desc + '\n\n' + remark
        rf.close()
    newapis = processDesc(wdict)
    return newapis

# conditional
pat1 = re.compile(r'call (.*?) once for every time it called (.*?)(,|\.)') 
pat2 = re.compile(r'opened by @\+\+(.*?)\+\+@\.')                       
pat3 = re.compile(r'obtains a reference to the (.*?) interface .* by calling the (.*?) method')     
pat4 = re.compile(r'obtain the result of the original(.*?) call after .* by calling(.*?)\.')      
pat5 = re.compile(r'when @\+\+(.*?)\+\+@ is called')                    
pat6 = re.compile(r'The (.*?) interface is used to translate (.*?) instances') 
pat7 = re.compile(r'Closes .* opened by using the @\+\+(.*?)\+\+@')    
pat8 = re.compile(r'by a preceding @\+\+(.*?)\+\+@')                   
pat9 = re.compile(r'allocations made on it using @\+\+(.*?)\+\+@')     
pat10 = re.compile(r'if .* using the @\+\+(.*?)\+\+@ .* before')        
pat11 = re.compile(r'cannot .* until @\+\+(.*?)\+\+@ is called')       
pat12 = re.compile(r'made on .* using @\+\+(.*?)\+\+@ are no longer valid')
pat13 = re.compile(r'to write .* call @\+\+(.*?)\+\+@ first', re.I)    
pat14 = re.compile(r'until @\+\+(.*?)\+\+@ is called')                  
pat15 = re.compile(r'If @\+\+(.*?)\+\+@ is called without a prior call to (.*?),', re.I)   
pat16 = re.compile(r'rather than .* using @\+\+(.*?)\+\+@')             
pat17 = re.compile(r'this differs from @\+\+(.*?)\+\+@', re.I)         
pat18 = re.compile(r'through an internal call to @\+\+(.*?)\+\+@')     
pat19 = re.compile(r'returns a pointer to .* @\+\+(.*?)\+\+@', re.I)    
pat20 = re.compile(r'retrieves a pointer to .* @\+\+(.*?)\+\+@', re.I)  
pat21 = re.compile(r'should call @\+\+(.*?)\+\+@ once for every time it called @\+\+(.*?)\+\+@')   
pat22 = re.compile(r'after @\+\+(.*?)\+\+@ is called, additional calls to the @\+\+(.*?)\+\+@', re.I)
pat23 = re.compile(r'call @\+\+(.*?)\+\+@ before .*, and call @\+\+(.*?)\+\+@ when you have finished', re.I)   
pat24 = re.compile(r'the @\+\+(.*?)\+\+@ function is .*? callback function used with the @\+\+(.*?)\+\+@', re.I)   
pat0 = re.compile(r'the @\+\+(.*?)\+\+@ function specifies a callback function used with the @\+\+(.*?)\+\+@', re.I)    
pat25 = re.compile(r'to .*, call @\+\+(.*?)\+\+@', re.I)        
pat26 = re.compile(r'to .*, use the  @\+\+(.*?)\+\+@', re.I)        
pat27 = re.compile(r'this function returns .* that can be examined using functions such as @\+\+(.*?)\+\+@', re.I)  
pat28 = re.compile(r'will not .* unless .* by the @\+\+(.*?)\+\+@')    

# alternative
pat29 = re.compile(r'superseded by the @\+\+(.*?)\+\+@')       
pat30 = re.compile(r'is identical to the @\+\+(.*?)\+\+@')      
pat31 = re.compile(r'this function is an extension to (.*?)\.', re.I)  
pat32 = re.compile(r'the @\+\+(.*?)\+\+@ interface is derived from the @\+\+(.*?)\+\+@', re.I) 
pat33 = re.compile(r'Similar to the (.*?) interface')  
pat34 = re.compile(r'unlike @\+\+(.*?)\+\+@', re.I)     
pat35 = re.compile(r'the @\+\+(.*?)\+\+@ .* is similar to the @\+\+(.*?)\+\+@', re.I)   
pat36 = re.compile(r'is identical to @\+\+(.*?)\+\+@')      
pat37 = re.compile(r'The @\+\+(.*?)\+\+@ .*, which is available from a call to @\+\+(.*?)\+\+@')   
pat38 = re.compile(r'Instead, use @\+\+(.*?)\+\+@')     

# refers to
pat39 = re.compile(r'see @\+\+(.*?)\+\+@')              

conditional_pat = [pat0, pat1, pat2, pat3, pat4, pat5, pat6, pat7, pat8, pat9, pat10, pat11, pat12, pat13, pat14, pat15, pat16, pat17, pat18, pat19, pat20, pat21, pat22, pat23, pat24, pat25, pat26, pat27, pat28]
alternative_pat = [pat29, pat30, pat31, pat32, pat33, pat34, pat35, pat36, pat37, pat38]

def parseTemplate():
    apis = getDesc()
    conditional_rel = set()
    alternative_rel = set()
    refers_to_rel = set()
    allapis = {}
    cnt = 0
    for api, desc in apis.items():
        cnt += 1
        # refers_to
        res = re.findall(pat39, desc)
        if res:
            for s in res:
                refers_to_rel.add((api, "refers_to", s))
        # conditional & alternative
        for pat in conditional_pat:
            res = re.findall(pat, desc)
            if res:
                if isinstance(res[0], str):
                    for s in res:
                        conditional_rel.add((api, "conditional", s))
                elif isinstance(res[0], tuple):
                    for tu in res:
                        conditional_rel.add((tu[0], "conditional", tu[1]))
        for pat in alternative_pat:
            res = re.findall(pat, desc)
            if res:
                if isinstance(res[0], str):
                    for s in res:
                        alternative_rel.add((api, "alternative", s))
                elif isinstance(res[0], tuple):
                    for tu in res:
                        alternative_rel.add((tu[0], "alternative", tu[1]))
    return conditional_rel, alternative_rel, refers_to_rel

def processDesc(apis):
    newapis = {}
    for api, desc in apis.items():
        newapis[api] = desc.replace('\n', ' ').strip()
    return newapis

def get_ent_id():
    ent_id = {}
    with open('./res/entity.txt') as rf:
        for line in rf.readlines():
            res = line.strip().split(',')
            ent = res[0]
            id = res[2]
            ent_id[ent] = id
    return ent_id

def relation_id():
    wpath = './res/relation.txt'
    ent2id = get_ent_id()
    relation_id = []
    refers_to_set = refers_to()
    conditional_set, alternative_set, tem_refers_set = parseTemplate()

    allrelation = {}
    allrelation['function_of'] = function_of()
    allrelation['class_of'] = class_of()
    allrelation['inheritance'] = inheritance()
    allrelation['uses_parameter'] = uses_parameter()
    allrelation['returns'] = returns()
    allrelation['conditional'] = conditional_set
    allrelation['alternative'] = alternative_set
    allrelation['refers_to'] = refers_to_set | tem_refers_set

    for key, value in allrelation.items():
        relation = key
        rel_id = relation2id[relation]
        cnt = 0
        for rel_tu in value:
            et1 = getformatted(rel_tu[0].lower())
            et2 = getformatted(rel_tu[2].lower())
            if et1 in ent2id.keys() and et2 in ent2id.keys():
                id1 = ent2id[et1]
                id2 = ent2id[et2]
                relation_id.append((id1, rel_id, id2))
                cnt += 1
        print(relation, cnt)
    with open(wpath, 'w') as wf:
        for item in relation_id:
            wf.write(str(item[0]) + ',' + str(item[1]) + ',' + str(item[2]))
            wf.write('\n')


def getformatted(et1):
    if " callback function" in et1:
        et1 = et1.replace(" callback function", "")
    elif " function" in et1:
        et1 = et1.replace(" function", "")
    elif " macro" in et1:
        et1 = et1.replace(" macro", "")
    elif " interface" in et1:
        et1 = et1.replace(" interface", "")
    elif " class" in et1:
        et1 = et1.replace(" class", "")
    elif " method" in et1:
        et1 = et1.replace(" method", "")
    elif " structure" in et1:
        et1 = et1.replace(" structure", "")
    et1 = et1.replace(".h", "")
    if et1.find("b_") == 0 and et1.find("_b") == len(et1) - 2:
        et1 = et1.replace("b_", "")
        et1 = et1.replace("_b", "")
    if et1.find("i_") == 0 and et1.find("_i") == len(et1) - 2:
        et1 = et1.replace("i_", "")
        et1 = et1.replace("_i", "")
    et1 = et1.replace("@++", "")
    et1 = et1.replace("++@", "")
    if "u_" in et1 and "_u" in et1:
        indexl = find_all("_", et1)
        start = indexl[1] + 1
        end = indexl[-1]
        et1 = et1[start : end]
    et1 = re.sub('\(.*?\)', '', et1)
    return et1.strip()

def relation_type():
    wpath = './res/relation_type.txt'
    with open(wpath, 'w') as wf:
        for key, value in relation2id.items():
            wf.write(key + "," + str(value))
            wf.write('\n')


if __name__ == "__main__":
    dir = './res'
    if not os.path.exists(dir):
        os.makedirs(dir)
    relation_id()
    relation_type()
