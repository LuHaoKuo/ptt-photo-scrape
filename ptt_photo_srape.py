#require PhantomJS browser 
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import os
import re
import urllib

#This is a simple demonstration of PTT forum scraping.
#With user-specified date, it will found all the post in that period, download all photos of each 
#articles with a file name of article title, and generate a download list

PTT_URL = 'https://www.ptt.cc'

#filter for article link, push counts and title
def get_articles(dom, date):

    soup = BeautifulSoup(dom, 'html.parser')

    articles = []  
    divs = soup.find_all('div', 'r-ent')
    print("yournote = ",soup)
    for d in divs:
        
        if (d.find('div', 'date').string).strip() == date:  
            push_count = 0
            if d.find('div', 'nrec').string:
                try:
                    push_count = int(d.find('div', 'nrec').string)  #retrieve push count
                except ValueError:  
                    pass

            # get article link and title			
            if d.find('a'):  #if hyperlink exists
                
                href = d.find('a')['href']
                title = d.find('a').string
                articles.append({
                    'title': title,
                    'href': href,
                    'push_count': push_count
                })
        
    return articles



def parse(dom):
    soup = BeautifulSoup(dom, 'html.parser')
    links = soup.find(id='main-content').find_all('a')
    img_urls = []
    for link in links:
        if re.match(r'^https?://(i.)?(m.)?imgur.com', link['href']):
            img_urls.append(link['href'])
    return img_urls

def save(img_urls, title):
    if img_urls:
        try:
            dname = title.strip()  
            os.makedirs(dname)
            for img_url in img_urls:
                if img_url.split('//')[1].startswith('m.'):
                    img_url = img_url.replace('//m.', '//i.')
                if not img_url.split('//')[1].startswith('i.'):
                    img_url = img_url.split('//')[0] + '//i.' + img_url.split('//')[1]
                if not img_url.endswith('.jpg'):
                    img_url += '.jpg'
                fname = img_url.split('/')[-1]
                urllib.request.urlretrieve(img_url, os.path.join(dname, fname))
        except Exception as e:
            print(e)

#Main
os.chdir('/Users/k.vincent/Desktop/Python/use1')
URL = input("URL: ")
date = input("Date in mm/dd:")
if date[0] == '0':
    date = date[1:5]
if date == 'today':
    date = time.strftime("%m/%d").lstrip('0')

wfile = open("Article_Info.txt", "w",encoding = "UTF-8")
    
CurrentPageNum = int(URL[(URL.find("index"))+5: (URL.find("index"))+9])
index = 0
while 1:
    #any start page of ptt works. this is an example 
    url = 'https://www.ptt.cc/bbs/Food/index%d.html'%CurrentPageNum
    #PhantomJS path is required
    driver = webdriver.PhantomJS(executable_path='/Users/k.vincent/Downloads/phantomjs-2.1.1-macosx/bin/phantomjs')  # PhantomJs
    driver.get(url)  
    page = driver.page_source 
    driver.close()  

    #filter article by user-indicated date
    if page:
        if date[0] == 0:
            date = Date[1:5]
        if date == 'today':
            date = time.strftime("%m/%d").lstrip('0') 
        current_articles = get_articles(page, date)
   
        for post in current_articles:
            print(post['title'], "瀏覽量:",post['push_count'], "\n URL=   ", post['href'] )
            wfile.write(str(post['title'])+'\n'+ "瀏覽量: "+str(post['push_count'])+ "\n URL=   "+str(post['href'])+'\n\n')
            
    
    for article in current_articles:
            print('Processing', article)
            driver = webdriver.PhantomJS(executable_path='/Users/k.vincent/Downloads/phantomjs-2.1.1-macosx/bin/phantomjs')  # PhantomJs
            driver.get(PTT_URL + article['href']) 
            page = driver.page_source  
            driver.close()
            
            if page:
                img_urls = parse(page)
                save(img_urls, article['title'])
                article['num_image'] = len(img_urls)
                print("\n\n >>>>>>>>>", article['num_image'],"<<<<<<<<<\n\n")
    
    CurrentPageNum -= 1
    if current_articles !=[]:
        index = 1
    if current_articles == [] and index ==1:
        break
wfile.close()

    

    
