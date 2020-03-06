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
        terms = list()
        for term in relatedTerms:
            if match(term, page_text):
                terms.append(term)
                termCount += 1
                if termCount >= 4:
                    pageTitle = soup.title.string
                    savePath = Path(folder+pageTitle+".txt")
                    #save(page_text, pageTitle)
                    save(page_text, savePath)
                    savedURLs.append(url)
                    pageCount += 1
                    print("page#: %03i | url: %-100s | Terms: %s, %s, %s, %s" % (pageCount, reformat_url(url), terms[0], terms[1], terms[2], terms[3]))
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

#seeds = ["https://en.wikipedia.org/wiki/Weight_training", "https://en.wikipedia.org/wiki/Bodybuilding"]
#related = ["dumbbell", "bench", "barbell", "deadlift", "lbs", "hypertrophy", "muscle", "strength", "supplement", "protein"]
seeds = ["https://en.wikipedia.org/wiki/Olympic_Games", "https://en.wikipedia.org/wiki/Ancient_Olympic_Games"]
related = ["olympics", "race", "swimming", "competition", "speed", "training", "drugs", "medal", "torch", "marathon", "biking", "athlete", "athletics", "sport"]
crawler(seeds, related)

#content=get_page_content(seeds[0])
#print(content)
