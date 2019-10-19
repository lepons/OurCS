from eventregistry import *
import re

# print(vocab)
er = EventRegistry(apiKey = "dc366e58-71be-440c-9c52-bba1619ecf07")

q = QueryArticles(
    keywords = QueryItems.OR(["occupation sexism", "women in work", "glass ceiling", "gender discrimination", "history of women employment"]),
    dataType = ["news", "blog"],
    lang = ["eng"],
    isDuplicateFilter="skipDuplicates",
    )

for art in q.execQuery(er, sortBy = "date", maxItems = 500):
    # print(art)
    title = re.sub(r'([^\s\w]|_)+', '', art["title"])
    f = open("./news_articles/"+str(title)+".txt","w")
    f.write(art['date']+"\n")                
    f.write(art['url']+"\n")
    f.write(art['body']+"\n")
    f.close()