from newsapi import NewsApiClient
import sys

newsapi = NewsApiClient(api_key='52ca22c3c26e415f8050fb5cacbe0d92')

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
