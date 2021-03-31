#coding=utf-8
import http
import json
import time
import urllib.request

import bs4
from bs4 import BeautifulSoup
import re
import os
import random

baseUrl = "https://docs.microsoft.com/en-us/windows/win32/api/"

def askURL(url):
    head = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"
    }
    try:
        request = urllib.request.Request(url, headers=head)
        response = urllib.request.urlopen(request)
        try:
            html = response.read().decode('utf-8')
        except http.client.IncompleteRead as e:
            page = e.partial
            html = page.decode('utf-8')
    except urllib.error.HTTPError as e:
        html = ""
    return html

def askURL_m(url, num_retry = 5):
    html = ""
    head = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"
    }
    try:
        request = urllib.request.Request(url, headers=head)
        response = urllib.request.urlopen(request, timeout=10)

        # response = urllib.request.urlopen(url)
        try:
            html = response.read().decode('utf-8')
        except http.client.IncompleteRead as e:
            page = e.partial
            html = page.decode('utf-8')
        response.close()
    except Exception as e:
        html = None
        if num_retry > 0:
            return askURL(url, num_retry - 1)
    return html


paraName = re.compile(r'<p><code>(.*?)</code></p>')

# add link format
def getLink(html):
    if "href=" in html:
        u = "".join(re.findall(re.compile(r'href="(.*?)"'), html))  # url after href
        rep = "".join(re.findall(re.compile(r'">(.*?)</a>'), html))
        if "api" in u:  # example: @++u_errhandlingapi_GetLastError_u++@
            headapi = "".join(re.findall(re.compile(r'/api/(.*?)/'), u))
            headapi = headapi.replace("_", "#")         # replace "_" in header name to "#" for better differentiating
            uuu = headapi + "_" + rep.replace("_", "$")     # replace original "_" to "$" for better differentiating
        else:  # example: @++u_other_Conventions_for_Function_Prototypes_u++@
            uuu = "other_" + rep.replace(" ", "_")
        uuu = "@++u_" + uuu + "_u++@"
        return True, rep, uuu
    else:
        return False, "", ""


def parseInheritance(url):
    html = askURL(url)
    soup = BeautifulSoup(html, "html.parser")
    inh = soup.find('h2', id='inheritance')
    if not inh:
        return ""
    desc = ""
    res = ""
    for tag in inh.next_siblings:
        if tag.name == 'h2':
            break
        if tag.name == 'p':
            goal_p = inh.next_sibling
            if tag.string:
                desc = tag.string
            else:
                for s in tag.strings:
                    desc += s
            inhe1 = re.findall(re.compile(r'implements (.*?)\.'), desc)
            inhe2 = re.findall(re.compile(r'interface inherits from the (.*?) interface\.'), desc)

            if inhe1:
                res = inhe1[0]
            elif inhe2:
                res = inhe2[0]
    return res



def parseApi(url):
    dict = {}
    html = askURL(url)
    if not html:
        return dict
    soup = BeautifulSoup(html, "html.parser")
    m = soup.find('main', id='main')

    # get api's name
    dict['Name'] = str(m.h1.string)
    print(dict)

    # 1.get description
    # description html without 'description' label
    dict['Description'] = ""
    pflag = 0
    divflag = 0
    for item in soup.main.children:
        if item.name == 'h2':
            break
        if item.name == 'div':
            divflag = 1
            continue
        if item.name == 'p':
            # general case
            pflag = 1
            for i in soup.main.p.strings:
                dict['Description'] += str(i)
            if soup.main.p.b is not None:
                for tob in soup.main.p.b.strings:
                    dict['Description'] = dict['Description'].replace(str(tob), "@++b_" + tob + "_b++@")
            if soup.main.p.i is not None:
                for toi in soup.main.p.i.strings:
                    dict['Description'] = dict['Description'].replace(str(toi), "@++i_" + toi + "_i++@")
            desc_html = str(soup.main.p)  # soup.main.p---tag
            exist, rep, uuu = getLink(desc_html)
            if exist:
                dict['Description'] = dict['Description'].replace(rep, uuu)
    if pflag == 0:
        # special case
        div = soup.find('div', class_="alert")
        if divflag == 0:
            # without description (https://docs.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-readprocessmemory)
            dict['Description'] = " "
        else:
            for item in div.next_siblings:
                if item.name == 'h2':
                    break
                if item.name != 'div':
                    if item.name == 'b':
                        bb = "@++b_" + item.string + "_b++@"
                        dict['Description'] += bb
                    elif item.name == 'a':
                        exist, rep, uuu = getLink(str(item))
                        if exist:
                            dict['Description'] += item.string.replace(rep, uuu)
                    else:
                        dict['Description'] += item.string
        if soup.main.p is not None:
            for i in soup.main.p.strings:
                dict['Description'] += str(i)
            if soup.main.p.b is not None:
                for tob in soup.main.p.b.strings:
                    dict['Description'] = dict['Description'].replace(str(tob), "@++b_" + tob + "_b++@")
            if soup.main.p.i is not None:
                for toi in soup.main.p.i.strings:
                    dict['Description'] = dict['Description'].replace(str(toi), "@++i_" + toi + "_i++@")
            desc_html = str(soup.main.p)  # soup.main.p---tag
            exist, rep, uuu = getLink(desc_html)
            if exist:
                dict['Description'] = dict['Description'].replace(rep, uuu)
    else:
        div = soup.find('div', class_="alert")
        if div is not None:
            for item in div.next_siblings:
                if item.name == 'h2':
                    break
                if item.name != 'div':
                    if item.name == 'b':
                        bb = "@++b_" + item.string + "_b++@"
                        dict['Description'] += bb
                    elif item.name == 'a':
                        exist, rep, uuu = getLink(str(item))
                        if exist:
                            dict['Description'] += item.string.replace(rep, uuu)
                    else:
                        if item.string is not None:
                            dict['Description'] += item.string

    # 2. get syntax
    s = soup.find('h2', id="syntax")
    if s is not None:
        tmp = soup.main.pre
        if tmp is None:
            tmp = soup.find('pre')
        dict[s.string] = tmp.string


    # 3.get parameters
    p = soup.find('h2', id="parameters")
    lis = []
    if p is not None:
        for pp in p.next_siblings:
            if pp.name == 'h2':
                break
            if pp == '\n':
                continue
            lis.append(pp)
        names = []
        types = []
        descs = []
        description = ""
        # find all description
        for item in lis:
            n = re.findall(paraName, str(item))
            t = re.findall("Type", str(item))
            if n:
                if description != "":
                    descs.append(description)
                description = ""
            elif t:
                if description != "":
                    descs.append(description)
                description = ""
            else:   # 描述
                if isinstance(item, bs4.element.Tag):
                    for i in item.strings:
                        description += i
                    if item.b is not None:
                        for tob in item.b.strings:
                            description = description.replace(str(tob), "@++b_" + tob + "_b++@")
                    if item.i is not None:
                        for toi in item.i.strings:
                            description = description.replace(str(toi), "@++i_" + toi + "_i++@")
                    exist, rep, uuu = getLink(str(item))
                    if exist:
                        description = description.replace(rep, uuu)
                elif isinstance(item, bs4.element.NavigableString):
                    description += str(item)
        if description != "":
            descs.append(description)

        for item in lis:
            typestr = ""
            n = re.findall(paraName, str(item))
            t = re.findall("Type", str(item))
            if n:       # parameter name
                names.append("".join(n))
            elif t:     # parameter type
                if item.b is not None:
                    if item.b.string is not None:
                        typestr = item.b.string
                    else:
                        for j in item.b.strings:
                            typestr += j
                elif item.strong is not None:
                    if item.strong.string is not None:
                        typestr = item.strong.string
                    else:
                        for j in item.strong.strings:
                            typestr += j
                typestr = "@++b_" + str(typestr) + "_b++@"
                exist, rep, uuu = getLink(str(item))
                if exist:
                    typestr = typestr.replace(rep, uuu)
                types.append(typestr)
        paras = []
        llen = len(names)
        for i in range(0, llen):
            if len(types) >= llen and len(descs) >= llen:
                paras.append((names[i], types[i], descs[i]))
            elif i >= len(types) and i < len(descs):
                paras.append((names[i], " ", descs[i]))
            elif i < len(types) and i >= len(descs):
                paras.append((names[i], types[i], " "))
            else:
                paras.append((names[i], " ", " "))
        dict[p.string] = paras

    # 4. get return
    v = soup.find('h2', id="return-value")
    ret = []
    if v is not None:
        for vv in v.next_siblings:
            if vv.name == 'h2':
                break
            if vv == '\n':
                continue
            ret.append(vv)
        retdict = {}
        retdict['desc'] = ""
        typestr = ""
        for item in ret:
            t = re.findall("Type", str(item))
            if t:       # return type
                if item.b is not None:
                    if item.b.string is not None:
                        typestr = item.b.string
                    else:
                        for j in item.b.strings:
                            typestr += j
                elif item.strong is not None:
                    if item.strong.string is not None:
                        typestr = item.strong.string
                    else:
                        for j in item.strong.strings:
                            typestr += j
                typestr = "@++b_" + str(typestr) + "_b++@"
                exist, rep, uuu = getLink(str(item))
                if exist:
                    typestr = typestr.replace(rep, uuu)
                retdict['retType'] = typestr
            else:       # return value description
                if isinstance(item, bs4.element.Tag):
                    for ds in item.strings:
                        retdict['desc'] += ds
                    if item.b is not None:
                        for tob in item.b.strings:
                            retdict['desc'] = retdict['desc'].replace(str(tob), "@++b_" + tob + "_b++@")
                    if item.i is not None:
                        for toi in item.i.strings:
                            retdict['desc'] = retdict['desc'].replace(str(toi), "@++i_" + toi + "_i++@")
                    exist, rep, uuu = getLink(str(item))
                    if exist:
                        retdict['desc'] = retdict['desc'].replace(rep, uuu)
                elif isinstance(item, bs4.element.NavigableString):
                    retdict['desc'] += str(item)
        dict[v.string] = retdict

    # 5.get remarks
    r = soup.find('h2', id="remarks")
    rem = []
    remark = ""
    if r is not None:
        for rr in r.next_siblings:
            if rr.name == 'h2':
                break
            if rr == '\n':
                continue
            rem.append(rr)
        for item in rem:
            if isinstance(item, bs4.element.Tag):
                for i in item.strings:
                    remark += i
                if item.b is not None:
                    for tob in item.b.strings:
                        remark = remark.replace(str(tob), "@++b_" + tob + "_b++@")
                if item.i is not None:
                    for toi in item.i.strings:
                        remark = remark.replace(str(toi), "@++i_" + toi + "_i++@")
                exist, rep, uuu = getLink(str(item))
                if exist:
                    remark = remark.replace(rep, uuu)
            elif isinstance(item, bs4.element.NavigableString):
                remark += str(item)
        dict[r.string] = remark

    # 6.get requirements
    req = soup.find('h2', id="requirements")
    if req is not None:
        contents = soup.find_all('tbody')
        content = ""
        for c in contents:
            if re.findall('<td style="text-align: left;">', str(c)):
                content = str(c)
        reqdict = {}
        keys = re.findall(re.compile('<td><strong>(.*?)</strong></td>'), content)
        values = re.findall(re.compile('<td style="text-align: left;">(.*?)</td>'), content)
        for i in range(0, len(keys)):
            reqdict[keys[i]] = values[i]
        dict[req.string] = reqdict

    # 7.get See also
    sa = soup.find('h2', id="see-also")
    seea = []
    seealso = {}
    key = "Default"
    if sa is not None:
        for ss in sa.next_siblings:
            if ss == '\n':
                continue
            if ss.name != 'p':
                break
            seea.append(ss)
        for item in seea:
            if item.b is not None:
                if not key in seealso and key != "Default":
                    seealso[key] = []
                key = item.b.string
            elif item.strong is not None:
                if not key in seealso and key != "Default":
                    seealso[key] = []
                key = item.strong.string
            else:
                if not key in seealso:
                    if item.a is not None:
                        href = item.a.get('href')
                        seealso[key] = [href.split("-")[-1]]
                    else:
                        seealso[key] = [item.string]
                else:
                    if item.a is not None:
                        href = item.a.get('href')
                        seealso[key].append(href.split("-")[-1])
                    else:
                        seealso[key].append(item.string)
        if not key in seealso:
            seealso[key] = []
        dict[sa.string] = seealso

    # 8.get inheritance
    name = dict['Name']
    if " interface" in name or " class" in name:
        dict['Inheritance'] = parseInheritance(url)


    return dict

def get_interface_href():
    rpath = './res/doc_in_json'
    jsonList = os.listdir(rpath)
    jsonList.sort(key=lambda x: x.split('.')[0])
    wclass = {}
    winter = {}
    for js in jsonList:
        rf = open(os.path.join(rpath, js), 'r')
        apis = json.load(rf)
        for api in apis:
            if " class" in api['Name']:
                name = api['Name'].replace(" class", "").strip()
                url = api['Url'].strip()
                wclass[name] = url
            elif " interface" in api['Name']:
                name = api['Name'].replace(" interface", "").strip()
                url = api['Url'].strip()
                winter[name] = url
        rf.close()
    all_dict = {}
    all_dict['class'] = wclass
    all_dict['interface'] = winter
    return all_dict


def find_all(sub, s):
    index_list = []
    index = s.find(sub)
    while index != -1:
        index_list.append(index)
        index = s.find(sub, index + 1)
    return index_list

def get_method_url(dict):
    url_set = set()
    i = 0
    for name, url in dict.items():
        print(i)
        i += 1
        html = askURL(url)
        soup = BeautifulSoup(html, "html.parser")
        m = soup.find('main', id='main')
        # get method links
        me = soup.find_all('h2', id="methods")
        for m in me:
            for item in m.next_siblings:
                if item.name == 'h2':
                    break
                if item.name == 'table':
                    tds = item.find_all('td')
                    for td in tds:
                        relativeURL = "".join(re.findall(re.compile(r'href="(.*?)"'), str(td)))  # url after href
                        toreplace_index = find_all('/', url)[-1]
                        if relativeURL:
                            complete_url = url[:toreplace_index + 1]  + relativeURL
                            url_set.add(complete_url)
    return url_set

def Methods_url():
    all_dict = get_interface_href()
    class_dict = all_dict['class']
    interface_dict = all_dict['interface']
    print("class parse begins!")
    class_url_set = get_method_url(class_dict)
    print("class parse finished!")
    print("interface parse begins!")
    inter_url_set = get_method_url(interface_dict)
    print("interface parse finished!")
    all_url_dict = {}
    all_url_dict['class'] = list(class_url_set)
    all_url_dict['interface'] = list(inter_url_set)
    print(len(class_url_set))
    print(len(inter_url_set))
    return all_url_dict

def Methods_page():
    c_wlist = []
    i_wlist = []
    dir = './res/doc_in_json'
    class_wfile = 'class_methods.json'
    inter_wfile = 'interface_methods.json'
    all_dict = Methods_url()
    class_urllist = all_dict['class']
    inter_urllist = all_dict['interface']
    i = 0
    print("start interface!")
    for i_url in inter_urllist:
        print(i)
        i += 1
        dict = parseApi(i_url)
        if not dict:
            continue
        dict['Head'] = "".join(re.findall(re.compile(r'/api/(.*?)/'), i_url))  # add header name（without .h）
        dict['Url'] = i_url  # add url source
        sa_dict = spySeeAlso(i_url)
        dict['See also'] = sa_dict
        i_wlist.append(dict)
    with open(os.path.join(dir, inter_wfile), 'w') as wf:
        json.dump(i_wlist, wf, indent=2)

    print("start class!")
    for i_url in class_urllist:
        print(i)
        i += 1
        dict = parseApi(i_url)
        if not dict:
            continue
        dict['Head'] = "".join(re.findall(re.compile(r'/api/(.*?)/'), i_url))  # add header name（without .h）
        dict['Url'] = i_url  # add url source
        sa_dict = spySeeAlso(i_url)
        dict['See also'] = sa_dict
        c_wlist.append(dict)
    with open(os.path.join(dir, class_wfile), 'w') as wf:
        json.dump(c_wlist, wf, indent=2)

def spySeeAlso(url):
    dict = {}
    html = askURL_m(url, 5)
    if html == "":
        return dict
    soup = BeautifulSoup(html, "html.parser")
    m = soup.find('main', id='main')
    sa = soup.find('h2', id="see-also")
    seea = []
    seealso = {}
    key = "Default"

    # other api
    if sa is not None:
        for ss in sa.next_siblings:
            if ss == '\n':
                continue
            if ss.name != 'p':
                break
            seea.append(ss)
        for item in seea:
            if item.b is not None:
                if not key in seealso and key != "Default":
                    seealso[key] = []
                key = item.b.string
            elif item.strong is not None:
                if not key in seealso and key != "Default":
                    seealso[key] = []
                key = item.strong.string
            else:
                if not key in seealso:
                    seealso[key] = [item.string]
                else:
                    seealso[key].append(item.string)
        if not key in seealso:
            seealso[key] = []
    return seealso


if __name__ == "__main__":
    wlist, head, line = [], "", "a"
    save_dir = './res/doc_in_json'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    rfile = open("links.txt", encoding='utf-8')
    while 1:
        if not line:
            break
        elif head != "":
            with open(os.path.join(save_dir, head + ".json"), 'w') as f:
                json.dump(wlist, f, indent=2)
                wlist = []
        while 1:
            line = rfile.readline()
            if not line:
                break
            if line[0] == '*':
                break
            dict = parseApi(line)
            if not dict:
                continue
            dict['Head'] = "".join(re.findall(re.compile(r'/api/(.*?)/'), line))  # add header name（without .h）
            dict['Url'] = line  # add source url
            head = dict['Head']
            wlist.append(dict)
    rfile.close()

    # spy methods
    Methods_page()


