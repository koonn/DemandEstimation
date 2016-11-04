#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 13:23:46 2016

@author: TK
"""

import requests
import bs4
from time import sleep 
import pandas as pd
import csv

##### catalog → maker #####
url = "http://www.goo-net.com/catalog/"
resp = requests.get(url)
html = resp.text.encode(resp.encoding)

soup = bs4.BeautifulSoup(html,"lxml")
makers = soup.find(class_= 'line').find_all('li')

link_makername = []
for tag in makers:
    link = tag.find('a')['href']  
    maker_name = tag.find('a').text
    link_makername.append([maker_name,link])
    sleep(1)
del maker_name, link

##### maker →　brand #####
link_brandname = []
i = 0
while i < len(link_makername):
    sleep(1)
    url = "http://www.goo-net.com" + link_makername[i][1]
    resp = requests.get(url)
    html = resp.text.encode(resp.encoding)
    soup = bs4.BeautifulSoup(html,"lxml")
    brands = soup.find_all(class_= 'img')
    for tag in brands:
        link = tag.find('a')['href']  
        brand_name = tag.find('span').text
        link_brandname.append([link_makername[i][0],brand_name,link])
    i += 1 
    print(i)
    
    del  link, brand_name

   
for brand in link_brandname:
    if brand[2].find('index') != -1:
        continue        
    brand[2] = brand[2].replace('.html', '/index.html')    

##### 使うブランドを絞った #####
df_uselist = pd.read_csv("uselist.csv",names=[0], encoding = 'shift-jis', engine = 'python').T
uselist = df_uselist.values.tolist()
uselist = []

with open("uselist.csv","r", encoding = 'shift-jis') as f:
    reader = csv.reader(f)
    
    for row in reader:
        uselist.append(row)
    
ulist = []
for row in uselist:
    ulist.append(row[0])

ulist.append(link_brandname[166][1] )    
ulist.append('ＣＸ−３')
ulist.append('ＣＸ−５')
ulist.append('ＷＲＸ Ｓ４')
ulist.append('ランドクルーザー')
ulist.append('アテンザセダン')
                          
del uselist 

usebrand = []
for brand in link_brandname:
    if brand[1] not in ulist:
        continue
    usebrand.append(brand)

del link_brandname, df_uselist, brand, row, ulist     
    
##### brand → model ##### 
link_modelname = []    
i = 0
while i < len(usebrand) :
    sleep(1)
    url = "http://www.goo-net.com" + usebrand[i][2]
    resp = requests.get(url)
    html = resp.text.encode(resp.encoding)
    soup = bs4.BeautifulSoup(html,"lxml")
    models = soup.find_all(class_= 'grade')
    for tag in models:
        update = tag.find_parents('div',class_='box_roundGray')[0].get('id')
        link = tag.find('a')['href']  
        model_name = tag.find('a').text
        link_modelname.append([usebrand[i][0],usebrand[i][1],update,model_name,link])
    i += 1
    print(i)           
   
    
    
for model in link_modelname:
    model[2] = int(model[2])    

del model_name, link, update, model
        
##### datasetのヘッダを作る #####
desc = ['maker','brands','update','modelname']

url = "http://www.goo-net.com" + link_modelname[1][4]
resp = requests.get(url)
html = resp.text.encode(resp.encoding)
soup = bs4.BeautifulSoup(html,"lxml")

part1 = soup.find_all(class_='tbl_type01') 
desc1 = [] 
i = 0
while i < len(part1) :
    target_desc = part1[i].find_all('th')
    for descs in target_desc:
        desc1.append(descs.text)
        
    i += 1

part1m = soup.find_all(class_='tbl_type01 mb20')
desc1m = []
i = 0
while i < len(part1m) :
    target_desc = part1m[i].find_all('th')
    for descs in target_desc:
        desc1m.append(descs.text)
        
    i += 1

for descs in desc1:
    desc.append(descs)
for descs in desc1m:
    desc.append(descs)
desc.append('price')
desc.append('colors')

del descs, desc1, desc1m


        
##### model dataset #####
values = []
i = 0 
while i < len(link_modelname):
    sleep(1)
    url = "http://www.goo-net.com" + link_modelname[i][4]
    resp = requests.get(url)
    html = resp.text.encode(resp.encoding)
    soup = bs4.BeautifulSoup(html,"lxml")
#priceをとる
    partp = soup.find_all('span', class_='price')
    price = partp[0].text

#スペックを取る。　tbl_type01
    part1 = soup.find_all(class_='tbl_type01') 
    val1 = []
    j = 0
    while j < len(part1) :        
        target_val = part1[j].find_all('td')
        for vals in target_val:
            val1.append(vals.text)    
        j += 1
    
#スペックを取る。　tbl_type01 mb20
    part1m = soup.find_all(class_='tbl_type01 mb20')
    val1m = []
    j = 0
    while j < len(part1m) :       
        target_val = part1m[j].find_all('td')
        for vals in target_val:
            val1m.append(vals.text)
        j += 1

#  colour selectable 
    partc = soup.find_all(class_='tbl_type03') 
    c = []

    target_c = partc[0].find_all('td')
    for colors in target_c:
        c.append(colors.text)
    colors = len(c) - c.count('') - 18

    u = link_modelname[i][0:4]
    u.extend(val1)
    u.extend(val1m)
    u.append(price)
    u.append(colors)
    values.append(u)
    i += 1
    print(i)
    
del c, colors, i, j, val1, val1m  



#csvに出力
dataset = pd.DataFrame(values)
dataset.columns = desc
dataset = dataset.drop("総合",axis = 1)
dataset.to_csv("carspec.csv", encoding = 'utf-16')
     