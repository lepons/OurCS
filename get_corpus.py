import sys
import os
import csv
import re
import requests
import random

from eventregistry import *
from bs4 import BeautifulSoup
from newsapi import NewsApiClient

newsapi = NewsApiClient(api_key='52ca22c3c26e415f8050fb5cacbe0d92')


def write_to_file(ls, file_path):
    with open(file_path, "w") as f:
        for item in ls:
            # compute the normalized value and add to query
            f.writelines(item + '\n')


def rankLines(path):
    """take in a text file, rank the key value pair, return a list if passing a threshold"""
    data = []
    with open(path, 'r') as f:
        query_ls = f.readlines()
        for query in query_ls:
            array = query.rsplit(' ')
            key = array[0]
            freq = array[1]
            data.append((key, freq))
    data = sorted(data, key=lambda key: key[1], reverse=True)
    comb_ls = []
    for key, freq in data:
        if float(freq) > 0.05:
            comb_ls.append((key,float(freq)))
    return comb_ls


def getQueries(keyWordsArray):
    """random select words from the queries"""
    idx = [random.randint(1, len(keyWordsArray) - 1) for i in range(10)]
    query = list(set([keyWordsArray[i][0] for i in idx]))
    return query


def query_crossref(query_ls):
    """query article DOIs from a list of queries"""
    DOI_ls = []
    querystring = '('+')OR('.join(query_ls)+')'

    # initiate the query
    query_link = str("https://api.crossref.org/works?query=" + querystring)
    r = requests.get(query_link + "&cursor=*").json()

    # loop through each pages
    n = 0
    for pg in range(20):
        nxt = r['message']['next-cursor']
        r = requests.get(query_link + "&cursor=" + nxt)
        r = r.json()
        try:
            n = n + len(r['message']['items'])
            print("new items: " + str(n))
            for item in r['message']['items']:
                DOI = item['URL']
                DOI_ls.append(DOI)
        except KeyError:
            break
    DOI_ls = list(set(DOI_ls))
    return DOI_ls


def get_articles(query,folder_path):
    """save articles from google newsapi

    Attributes:
        query: list with query phrases/words
    """
    querystring = '('+')OR('.join(query)+')'
    response = newsapi.get_everything(
        q=querystring,
        from_param='2019-10-17',
        page_size=100,
        language='en')
    articles = response['articles']
    for i in range(len(articles)):
        f = open(folder_path+str(i)+".txt","w")
        if (articles[i]['content'] != None):
            f.write(articles[i]['url']+"\n")
            f.write(articles[i]['content'])
        f.close()


def html2text(url):
    try:
        response=requests.get(url).text
    except:
        return
    soup = BeautifulSoup(response,features="lxml")
    for script in soup(["script", "style"]):
            script.extract()
    text = soup.get_text()

    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    text_list = text.split("\n")
    if "Abstract" in text_list:
        i = text_list.index("Abstract")
        abstract = text_list[i+1]
        return abstract


def write_abstract(urls_file):
    count = 0
    for line in urls_file:
        print(line)
        abstract = html2text(line)
        if abstract != None:
            path = "./abstracts/" + str(count) + ".txt"
            file = open(path, "w")
            file.write(abstract)
            count += 1
            file.close()


def save_kaggle_data(kaggledata_path,output_path,max_num):
    """ parses kaggle data which is in csv format
    Attributes:
        kaggledata_path (folder where the csv files are stored)
        max_num int of number of articles to save
    """
    files = os.listdir(kaggledata_path)
    csv.field_size_limit(100000000)

    count = 0
    for file in files:
        if (file[-4:] == '.csv'):
            with open(kaggledata_path+file) as csvfile:
                readCSV = csv.reader(csvfile, delimiter=',')
                for row in readCSV:
                    try:
                        title = re.sub(r'([^\s\w]|_)+', '', row[2])
                        f = open(output_path+title+'.txt',"w+")
                        f.write(row[9])
                        f.close()
                        count += 1
                    except:
                        print("error parsing 1 file")
                    if (count == max_num):
                        return


def get_event_register():
    er = EventRegistry(apiKey="dc366e58-71be-440c-9c52-bba1619ecf07")
    q = QueryArticles(
        keywords=QueryItems.OR(["occupation sexism", "women in work", "glass ceiling", "gender discrimination",
                                "history of women employment"]),
        dataType=["news", "blog"],
        lang=["eng"],
        isDuplicateFilter="skipDuplicates",
    )

    for art in q.execQuery(er, sortBy="date", maxItems=500):
        # print(art)
        title = re.sub(r'([^\s\w]|_)+', '', art["title"])
        f = open("./news_articles/" + str(title) + ".txt", "w")
        f.write(art['date'] + "\n")
        f.write(art['url'] + "\n")
        f.write(art['body'] + "\n")
        f.close()
    return


def main():
    # get google news corpus
    query_topics = ['occupation sexism', 'women in work', 'glass ceiling', 'gender discrimination',
                    'history of women employment']
    path = 'newscorpus/'
    if (len(sys.argv) > 1):
        path = sys.argv[1]
    get_articles(query_topics, path)

    # get crossref corpus
    file_path = "./query.txt"
    keywords = rankLines(file_path)
    DOI_ls = []
    for i in range(50):
        query_ls = getQueries(keywords)
        DOI_ls.extend(query_crossref(query_ls))
    write_to_file(DOI_ls, "./URL.txt")
    with open("URL.txt", "r") as urls_file:
        write_abstract(urls_file)

    # get kaggle corpus
    kaggledata_path = "./kaggle/"
    output_path = "./kagglenews/"
    max_num = 1000
    save_kaggle_data(kaggledata_path, output_path, max_num)

    # get event register corpus
    get_event_register()
import sys
import os
import csv
import re
import requests
import random

from eventregistry import *
from bs4 import BeautifulSoup
from newsapi import NewsApiClient

newsapi = NewsApiClient(api_key='52ca22c3c26e415f8050fb5cacbe0d92')


def write_to_file(ls, file_path):
    with open(file_path, "w") as f:
        for item in ls:
            # compute the normalized value and add to query
            f.writelines(item + '\n')


def rankLines(path):
    """take in a text file, rank the key value pair, return a list if passing a threshold"""
    data = []
    with open(path, 'r') as f:
        query_ls = f.readlines()
        for query in query_ls:
            array = query.rsplit(' ')
            key = array[0]
            freq = array[1]
            data.append((key, freq))
    data = sorted(data, key=lambda key: key[1], reverse=True)
    comb_ls = []
    for key, freq in data:
        if float(freq) > 0.05:
            comb_ls.append((key,float(freq)))
    return comb_ls


def getQueries(keyWordsArray):
    """random select words from the queries"""
    idx = [random.randint(1, len(keyWordsArray) - 1) for i in range(10)]
    query = list(set([keyWordsArray[i][0] for i in idx]))
    return query


def query_crossref(query_ls):
    """query article DOIs from a list of queries"""
    DOI_ls = []
    querystring = '('+')OR('.join(query_ls)+')'

    # initiate the query
    query_link = str("https://api.crossref.org/works?query=" + querystring)
    r = requests.get(query_link + "&cursor=*").json()

    # loop through each pages
    n = 0
    for pg in range(20):
        nxt = r['message']['next-cursor']
        r = requests.get(query_link + "&cursor=" + nxt)
        r = r.json()
        try:
            n = n + len(r['message']['items'])
            print("new items: " + str(n))
            for item in r['message']['items']:
                DOI = item['URL']
                DOI_ls.append(DOI)
        except KeyError:
            break
    DOI_ls = list(set(DOI_ls))
    return DOI_ls


def get_articles(query,folder_path):
    """save articles from google newsapi

    Attributes:
        query: list with query phrases/words
    """
    querystring = '('+')OR('.join(query)+')'
    response = newsapi.get_everything(
        q=querystring,
        from_param='2019-10-17',
        page_size=100,
        language='en')
    articles = response['articles']
    for i in range(len(articles)):
        f = open(folder_path+str(i)+".txt","w")
        if (articles[i]['content'] != None):
            f.write(articles[i]['url']+"\n")
            f.write(articles[i]['content'])
        f.close()


def html2text(url):
    try:
        response=requests.get(url).text
    except:
        return
    soup = BeautifulSoup(response,features="lxml")
    for script in soup(["script", "style"]):
            script.extract()
    text = soup.get_text()

    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    text_list = text.split("\n")
    if "Abstract" in text_list:
        i = text_list.index("Abstract")
        abstract = text_list[i+1]
        return abstract


def write_abstract(urls_file):
    count = 0
    for line in urls_file:
        print(line)
        abstract = html2text(line)
        if abstract != None:
            path = "./abstracts/" + str(count) + ".txt"
            file = open(path, "w")
            file.write(abstract)
            count += 1
            file.close()


def save_kaggle_data(kaggledata_path,output_path,max_num):
    """ parses kaggle data which is in csv format
    Attributes:
        kaggledata_path (folder where the csv files are stored)
        max_num int of number of articles to save
    """
    files = os.listdir(kaggledata_path)
    csv.field_size_limit(100000000)

    count = 0
    for file in files:
        if (file[-4:] == '.csv'):
            with open(kaggledata_path+file) as csvfile:
                readCSV = csv.reader(csvfile, delimiter=',')
                for row in readCSV:
                    try:
                        title = re.sub(r'([^\s\w]|_)+', '', row[2])
                        f = open(output_path+title+'.txt',"w+")
                        f.write(row[9])
                        f.close()
                        count += 1
                    except:
                        print("error parsing 1 file")
                    if (count == max_num):
                        return


def get_event_register():
    er = EventRegistry(apiKey="dc366e58-71be-440c-9c52-bba1619ecf07")
    q = QueryArticles(
        keywords=QueryItems.OR(["occupation sexism", "women in work", "glass ceiling", "gender discrimination",
                                "history of women employment"]),
        dataType=["news", "blog"],
        lang=["eng"],
        isDuplicateFilter="skipDuplicates",
    )

    for art in q.execQuery(er, sortBy="date", maxItems=500):
        # print(art)
        title = re.sub(r'([^\s\w]|_)+', '', art["title"])
        f = open("./news_articles/" + str(title) + ".txt", "w")
        f.write(art['date'] + "\n")
        f.write(art['url'] + "\n")
        f.write(art['body'] + "\n")
        f.close()
    return


def main():
    # get google news corpus
    query_topics = ['occupation sexism', 'women in work', 'glass ceiling', 'gender discrimination',
                    'history of women employment']
    path = 'newscorpus/'
    if (len(sys.argv) > 1):
        path = sys.argv[1]
    get_articles(query_topics, path)

    # get crossref corpus
    file_path = "./query.txt"
    keywords = rankLines(file_path)
    DOI_ls = []
    for i in range(50):
        query_ls = getQueries(keywords)
        DOI_ls.extend(query_crossref(query_ls))
    write_to_file(DOI_ls, "./URL.txt")
    with open("URL.txt", "r") as urls_file:
        write_abstract(urls_file)

    # get kaggle corpus
    kaggledata_path = "./kaggle/"
    output_path = "./kagglenews/"
    max_num = 1000
    save_kaggle_data(kaggledata_path, output_path, max_num)

    # get event register corpus
    get_event_register()


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()