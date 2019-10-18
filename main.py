from os import listdir
from os.path import isfile, join
import re
import collections

from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.porter import *
from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation

def articles_in_descending_relevance(folder_path, relevance_results):
    files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
    # print(similarity_results)
    ranking = sorted(range(len(relevance_results)),key=relevance_results.__getitem__, reverse = True)
    articles_with_relevance = []
    for i in ranking:
        rel_with_filename = []
        rel_with_filename.append(relevance_results[i])
        rel_with_filename.append(files[i])
        articles_with_relevance.append(rel_with_filename)
    return articles_with_relevance
    # print(ranking)
    # print(similarity_results[ranking[0]])


def calculate_cosine_similarity(documents, folder_path, query_file, no_features=1000):
    #get base vector

    with open(query_file) as file:
        words = file.read().split()
        #count frequency
        wdict = {}
        for w in words:
            if w in wdict:
                wdict[w] += 1
            else:
                wdict[w] = 1
        #get vocab and freq array
        vocab = []
        queryvector = []
        for w in wdict:
            vocab.append(w)
            queryvector.append(wdict[w])

        files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
        tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=no_features, vocabulary = vocab)
        tf = tf_vectorizer.fit_transform(documents)
        doc_term_matrix = tf.todense()
        # show counterVectorizer result 
        # df = pd.DataFrame(doc_term_matrix,
        #               columns=tf_vectorizer.get_feature_names(),
        #               index=files)
        # print(df)
        similarity_results = []
        for vector in doc_term_matrix:
            # print(cosine_similarity([queryvector], vector))
            sim_result = cosine_similarity([queryvector], vector)
            similarity_results.append(sim_result[0][0])

        return similarity_results

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


def trim_counter(counter, min_appearance=2):
    """trim the counter by deleting keys value pairs for lower than min_appearance counts"""
    # List of keys to be deleted from dictionary
    selected_keys = list()

    # Iterate over the dict and put to be deleted keys in the list
    for (key, value) in counter.items():
        if value < min_appearance:
            selected_keys.append(key)

    # Iterate over the list and delete corresponding key from dictionary
    for key in selected_keys:
        if key in counter:
            del counter[key]
    return counter


def build_query(model, feature_names, no_top_words, min_appearance=2):
    """create a query file from the number of top words from topics"""
    # compile a list of all the top words from each topics
    words_ls = []
    for topic_idx, topic in enumerate(model.components_):
        ls = [feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]]
        words_ls.extend(ls)

    # create counter with more than min_appearance
    counter = collections.Counter(words_ls)
    counter = trim_counter(counter, min_appearance=2)

    # create a query text file
    file_path = "./query.txt"
    File_object = open(file_path, 'w')
    for key in counter:
        File_object.writelines(key + '\n')
    File_object.close()
    return


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
    tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=no_features,
                                    stop_words = text.ENGLISH_STOP_WORDS.union(my_additional_stop_words))
    tf = tf_vectorizer.fit_transform(documents)
    tf_feature_names = tf_vectorizer.get_feature_names()

    # Run LDA
    lda = LatentDirichletAllocation(n_components=no_topics, max_iter=5, learning_method='online',
                                    learning_offset=50.,random_state=0).fit(tf)
    if display:
        display_topics(lda, tf_feature_names, no_top_words)

    return lda, tf_feature_names


def calculate_cosine_similarity(documents, folder_path, query_file, no_features=1000):
    #get base vector

    with open(query_file) as file:
        words = file.read().split()
        #count frequency
        wdict = {}
        for w in words:
            if w in wdict:
                wdict[w] += 1
            else:
                wdict[w] = 1
        #get vocab and freq array
        vocab = []
        queryvector = []
        for w in wdict:
            vocab.append(w)
            queryvector.append(wdict[w])

        files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
        tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=no_features, vocabulary = vocab)
        tf = tf_vectorizer.fit_transform(documents)
        doc_term_matrix = tf.todense()
        # show counterVectorizer result 
        # df = pd.DataFrame(doc_term_matrix,
        #               columns=tf_vectorizer.get_feature_names(),
        #               index=files)
        # print(df)
        similarity_results = []
        for vector in doc_term_matrix:
            # print(cosine_similarity([queryvector], vector))
            sim_result = cosine_similarity([queryvector], vector)
            similarity_results.append(sim_result[0][0])

        return similarity_results


def main():
    n_top_words = 10
    folder_path = "./articles/"
    query_path = "./query.txt"
    documents = get_document_from_folder(folder_path)
    lda, tf_feature_names = get_LDA_topics(documents, no_topics=100, no_top_words=n_top_words, display=0)
    build_query(lda, tf_feature_names, no_top_words=n_top_words)
    # get_LDA_topics(documents, no_topics=25, no_top_words=20, display=1)
    results = calculate_cosine_similarity(documents, folder_path, query_path)
    
    print(articles_in_descending_relevance(folder_path, results))


if __name__ == "__main__":
    main()
