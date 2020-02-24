from bs4 import BeautifulSoup
from urllib.request import urlopen
from pathlib import Path
import re
import ssl
import os

try:
    _create_unverified_https_context = ssl._create_unverifiedcontext
except AttributeError:
    pass
else: ssl._create_default_https_context = _create_unverified_https_context

def get_page_content(url):
    try:
        html_response_text = urlopen(url).read()
        page_content = html_response_text.decode('utf-8')
        return page_content
    except Exception as e:
        return None


def clean_title(title):
    invalid_characters = ['<', '>', ':','"', '/', '\\', '|', '?', '*']
    for c in invalid_characters:
        title=title.replace(c,'')
    return title

#if re.search(term, page_text, re.I)

def get_urls(soup):
    links = soup.find_all('a')
    urls=[]
    for link in links:
        urls.append(link.get('href'))
    return urls

def is_url_valid(url):
    if url is None:
        return False
    if re.search('#', url):
        return False
    #match=re.search('^/wiki/', url)
    match=re.search('^/wiki/.*:.*',url)
    if match:
        return False 
    else:
        match=re.search('^/wiki/', url)
        if match:
            return True 
        else:
            return False

def reformat_url(url):
    match=re.search('^/wiki/', url)
    if match:
        return "https://en.wikipedia.org"+url
    else:
        return url

def save(text, path):
    f = open(path, 'w', encoding = 'utf-8', errors = 'ignore')
    f.write(text)
    f.close()

    #f=open("crawled_urls.txt", "w")
    #i = 1
    #for url in crawled_urls:
    #    f.write(str(i) + ': ' + url + '\n')
    #    i += 1
    #f.close()

def match(term, mainText):
    if re.search(term, mainText, re.I) is None:
        return False
    else:
        return True

def crawler(seedURLs, relatedTerms):
    queue = []
    visited = []
    pageCount = 0
    savedURLs = []
    folder = "../pages/"
    for url in seedURLs:
        queue.append(url)
        visited.append(url)
    #while queue is not empty
    while not queue == []:
        #print("queue=" + str(queue))
        url = reformat_url(queue.pop(0))
        pageContent = get_page_content(url)
        soup = BeautifulSoup(pageContent, 'html.parser')
        page_text = soup.get_text()
        if pageContent is None:
            continue
        termCount = 0
        pageMainText = get_page_content(url)
        for term in relatedTerms:
            if match(term, page_text):
                termCount += 1
                if termCount >= 3:
                    pageTitle = soup.title.string
                    savePath = Path(folder+pageTitle)
                    #save(page_text, pageTitle)
                    save(page_text, savePath)
                    savedURLs.append(url)
                    pageCount += 1
                    #print("page#: " + str(pageCount) + " | termCount: "+ str(termCount) + " | url: "+reformat_url(url))
                    print("page#: %-4i | termCount: %i | url: %s" % (pageCount, termCount, reformat_url(url)))
                    break
        if pageCount >= 500:
            break
        outGoingURLs = get_urls(soup)
        for outGoingURL in outGoingURLs:
            if is_url_valid(outGoingURL) and outGoingURL not in visited:
                queue.append(outGoingURL)
                visited.append(outGoingURL)
    #save(savedURLs, "savedURLs.txt")
    #write save to file
    txt = open("savedURLS.txt", 'w')
    for page in savedURLs:
        txt.write("%s\n"%(page))
    txt.close()

seeds = ["https://en.wikipedia.org/wiki/Weight_training", "https://en.wikipedia.org/wiki/Bodybuilding"]
related = ["lift", "bench", "squat", "deadlift", "lbs", "hypertrophy", "muscle", "fit", "olympic", "exercise"]
crawler(seeds, related)

#content=get_page_content(seeds[0])
#print(content)
