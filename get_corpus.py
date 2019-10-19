from newsapi import NewsApiClient
import sys
import requests
import random

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
        if float(freq) > 0.04:
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


if __name__ == "__main__":
    query_topics = ['occupation sexism', 'women in work', 'glass ceiling', 'gender discrimination', 'history of women employment']
    path = 'newscorpus/'
    if (len(sys.argv) > 1):
        path = sys.argv[1]
    get_articles(query_topics, path)
    file_path = "./query.txt"
    keywords = rankLines(file_path)
    DOI_ls = []
    for i in range(20):
        query_ls = getQueries(keywords)
        DOI_ls.extend(query_crossref(query_ls))
    write_to_file(DOI_ls, "./URL.txt")