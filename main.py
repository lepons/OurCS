from os import listdir
from os.path import isfile, join
import re
import collections

from numpy.linalg import norm
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.porter import *
from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation


# Util Functions
def get_document_names(folder_path):
    files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
    return files


def get_documents_content(file_list, folder_path):
    """get a list of string of files content from the folder"""
    articles = []
    stemmer = PorterStemmer()
    for fileName in file_list:
        if (fileName[0] == '.'):
            continue
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


def get_articles_with_descending_relevance(file_names, relevance_results):
    ranking = sorted(range(len(relevance_results)),key=relevance_results.__getitem__, reverse = True)
    articles_with_relevance = []
    for i in ranking:
        rel_with_filename = []
        rel_with_filename.append(relevance_results[i])
        rel_with_filename.append(file_names[i])
        articles_with_relevance.append(rel_with_filename)
    return articles_with_relevance


def get_document_with_cos_rel(document_name, folder_path, vocab, queryvector):
    file_list = [document_name]
    document_content = get_documents_content(file_list, folder_path)
    cos_sim = calculate_cosine_similarity(document_content, folder_path, vocab, queryvector)
    return cos_sim, document_name


def get_queryvector(query_file):
    """
    Attributes: query_file path
    Returns: vocab list , query vector (as a list)
    """
    with open(query_file) as file:
        words = file.read().split('\n')
        # create word vector for query
        vocab = []
        queryvector = []
        numwords = 0
        for w in words:
            winfo = w.split(' ')
            if (len(winfo) == 2):
                vocab.append(winfo[0])
                queryvector.append(winfo[1])
    return vocab, queryvector


def calculate_cosine_similarity(documents, vocab, queryvector, no_features=1000):
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

    # normalize the counts
    L2_norm = norm([value for _, value in counter.items()])

    # create a query text file
    file_path = "./new_neg_query.txt"
    File_object = open(file_path, 'w')
    for key, value in counter.items():
        # compute the normalized value and add to query
        File_object.writelines(key + ' ' + str(value/L2_norm) + '\n')
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
    my_additional_stop_words = ["et", "utc", "use", "oct", "utc", "al", "les", "file", "le", "la", "fri", "divis",
                                "download", "httpsaboutjstororgterms", "new"]
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

def avgcossim(results):
    total = 0
    for r in results:
        total += r[0]
    return total/len(results)

def main():
    # threshold = 0.6
    n_top_words = 10
    folder_path = "./new_negatives/"
    query_path = "./new_neg_query.txt"
    # data_path = "./kagglenews/"

    file_list = get_document_names(folder_path)
    documents = get_documents_content(file_list, folder_path)

    # data_list = get_document_names(data_path)
    # data_documents = get_documents_content(data_list, data_path)
    lda, tf_feature_names = get_LDA_topics(documents, no_topics=100, no_top_words=n_top_words, display=0)
    build_query(lda, tf_feature_names, no_top_words=n_top_words)

    # vocab, queryvector = get_queryvector(query_path)
    # print(vocab)
    # # against the training set
    # print("AGAINST TRAINING SET")
    # results = calculate_cosine_similarity(documents, vocab, queryvector)
    # sorted_results = get_articles_with_descending_relevance(file_list, results)
    # for r in sorted_results:
    #     print(r)
    # print(avgcossim(sorted_results))

    # with the kaggle dataset first 1000
    # print("AGAINST KAGGLE FIRST 1000")
    # results = calculate_cosine_similarity(data_documents, vocab, queryvector)
    # sorted_results = get_articles_with_descending_relevance(data_list, results)
    # above_thres = []
    # f = open("./cos_rel_results_for_kagglenews","w")
    # for r in sorted_results:
    #     # if (r[0] > threshold):
    #     f.write(str(r)+"\n")            
    #     above_thres.append(r)
    #     print(r)
    # f.close()

    # print("AGAINST EVENT REGISTRY 631")
    # file_list_from_er = get_document_names("./news_articles/")
    # documents_from_er = get_documents_content(file_list_from_er, "./news_articles/")
    # results = calculate_cosine_similarity(documents_from_er, vocab, queryvector)
    # sorted_results = get_articles_with_descending_relevance(file_list_from_er, results)
    # above_thres = []
    # f = open("./cos_rel_results_for_ernews","w")        
    # for r in sorted_results:
    #     # if (r[0] > threshold):
    #     f.write(str(r)+"\n")            
    #     above_thres.append(r)
    #     print(r)
    # f.close()

    # print(get_document_with_cos_rel('Gender history and labour history.txt', folder_path, vocab, queryvector))

    # print("AGAINST PAPER ABSTRACT 544")
    # file_list_from_ab = get_document_names("./abstracts/")
    # documents_from_ab = get_documents_content(file_list_from_ab, "./abstracts/")
    # results = calculate_cosine_similarity(file_list_from_ab, vocab, queryvector)
    # sorted_results = get_articles_with_descending_relevance(file_list_from_ab, results)
    # above_thres = []
    # for r in sorted_results:
    #     # if (r[0] > threshold):
    #     above_thres.append(r)
    #     print(r)
    # print(get_document_with_cos_rel('Gender history and labour history.txt', folder_path, vocab, queryvector))

    # f = open("./cos_rel_results_for_ernews","w")
    # f.write(r+"\n")            
    # f.close()

if __name__ == "__main__":
    main()
