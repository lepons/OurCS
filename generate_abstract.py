import requests
from bs4 import BeautifulSoup

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

def main():
    urls_file = open("./URL.txt","r")
    write_abstract(urls_file)
    urls_file.close()
    
if __name__ == '__main__':
    main()
