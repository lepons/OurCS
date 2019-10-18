from os import listdir
from os.path import isfile, join
import re
import pandas as pd

from nltk.stem.porter import *
from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation


def get_document_from_folder(folder_path):
    """get a list of string of files content from the folder"""
    files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
    articles = []
    stemmer = PorterStemmer()
    for fileName in files:
        with open(folder_path+fileName, 'rb') as f:
            fileContent = f.read()
            fileContent = fileContent.decode('utf-8')
            pattern = re.compile('([^\s\w]|_)+')
            fileContent = pattern.sub('', fileContent)
            fileContent = re.sub('\s',' ',fileContent)
            fileContent = re.sub('\d+','',fileContent)
            fileContent = ",".join([stemmer.stem(word) for word in fileContent.split(" ")])
        articles.append(fileContent)
    return articles


def display_topics(model, feature_names, no_top_words):
    """display the topics of from the LDA model"""
    for topic_idx, topic in enumerate(model.components_):
        print("Topic %d:" % (topic_idx))
        print(" ".join([feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]]))


def get_LDA_topics(documents, no_features=1000, no_topics=10, no_top_words=10, display=0):
    """ generate LDA model from document

    Attributes:
        documents (list(str)): documents to process list of strings
        no_features (int): feature number
        no_topics (int): numbers of topics to output
        no_top_words (int): numbers of top words
        display (boolean): if yes, print topics
    Return:
        LDA model
    """
    # vectorize the documents
    my_additional_stop_words = ["et", "utc", "use", "oct", "utc", "al", "les", "file", "le", "fri", "httpsaboutjstororgterms"]
    # stop_words = text.ENGLISH_STOP_WORDS.union(my_additional_stop_words)
    tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=no_features, stop_words = text.ENGLISH_STOP_WORDS.union(my_additional_stop_words))
    tf = tf_vectorizer.fit_transform(documents)
    tf_feature_names = tf_vectorizer.get_feature_names()

    # Run LDA
    lda = LatentDirichletAllocation(n_components=no_topics, max_iter=5, learning_method='online',
                                    learning_offset=50.,random_state=0).fit(tf)
    if display:
        display_topics(lda, tf_feature_names, no_top_words)

    return lda


def main():
    folder_path = "./articles/"
    documents = get_document_from_folder(folder_path)
    get_LDA_topics(documents, no_topics=25, no_top_words=20, display=1)


if __name__ == "__main__":
    main()
