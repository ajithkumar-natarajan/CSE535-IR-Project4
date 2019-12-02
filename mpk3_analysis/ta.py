from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import LabelEncoder
import fasttext
import pickle
import sys
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys


'''
This file does topic analysis on POI tweets
Please make sure when you send tweets to this
file they are in a jsonl file

The point of this file is:

1) to create an LDA model 
2) Save model as a pickled file 
3) Use the pickled file to load a model
4) Use that model to classify tweets
&
1) Load all models including SVD
2) read and incoming list of tweets and a query string
3) output three graphs showing the query in the vectorizer
space of each country


I didnt want to create two separate fo
(1) Get tweets and separate and country
(2) Perform LDA '''
NUM_SVD_DIM = 3
NUM_OF_TOPICS = 5
LANG_DETECT_MODEL = '/home/mpk3/Desktop/IR_Final/analytics/ft/models/lid.176.ftz'
# print(str(sys.argv[1]))
flag = sys.argv[1]  # --create  --label --graphcloud --gtopics
all_else = sys.argv[1:]
option = sys.argv[2]
if len(all_else) > 2:
    query = sys.argv[3]


def load_json(jsonl_fin):
    ''' Method for loading jsonl files'''
    tweet_json_lines = np.array([])
    with open(jsonl_fin) as fin:
        line = fin.readline()
        while line:
            tweet_json_lines = np.append(tweet_json_lines, eval(line))
            line = fin.readline()
    return tweet_json_lines


def detect_language(tweet):
    ''' This is currently not used!!!!!
    This detects the language of a string of text
    and returns a text value associated with that language
    ex: detec_language('is is obviously English')
    return : 'en' '''
    detector = fasttext.load_model(LANG_DETECT_MODEL)
    return detector.predict(tweet)[0][0][-2:]


def separate_by_country(tweet_json_lines):
    '''Separates all of the tweets passed to it
    into a single array whose first dimension
    represents a country
    '''
    usa = []
    india = []
    brazil = []
    for tweet in tweet_json_lines:
        if tweet.get('country') is 'USA':
            usa.append(tweet)
        if tweet.get('country') is 'India':
            india.append(tweet)
        if tweet.get('country') is 'Brazil':
            brazil.append(tweet)
    all_tweets = np.array([usa, india, brazil])
    return all_tweets


def get_text_only(tweet_list):
    '''Utility function for getting
    the text out of a tweet
    '''
    tweets = []
    for tweet in tweet_list:
        tweets.append(tweet.get('tweet_text'))
    return tweets


def get_stopword_list(filein):
    '''Loads stopword files'''
    stopwords = []
    with open(filein) as fin:
        line = fin.readline()
        while line:
            stopwords.append(line)
            line = fin.readline().rstrip()
    return stopwords


def create_stop_lists():
    ''' Creates stop word for each language
    Scikit-learn has a built in list for english but
    doing loading a separate english streamlines the
    process
    '''
    stop_lists = {}
    stop_lists['hi'] = get_stopword_list('./stopwords/hi_stopwords.txt')
    stop_lists['pt'] = get_stopword_list('./stopwords/pt_stopwords.txt')
    stop_lists['en'] = get_stopword_list('./stopwords/en_stopwords.txt')
    return stop_lists


def create_svd(sparse_matrix):
    svd = TruncatedSVD(n_components=NUM_SVD_DIM)
    svd.fit(sparse_matrix)
    return svd


def build_topic_model(all_tweets, stop_lists):
    for country_tweets in all_tweets:
        if len(country_tweets) > 0:
            country = country_tweets[0].get('country')
            stops = stop_lists.get(country)
            country_tweets = get_text_only(country_tweets)
            vectorizer = CountVectorizer(max_df=0.95, min_df=2,
                                         max_features=20000, stop_words=stops)
            counts = vectorizer.fit_transform(country_tweets)
            lda = LatentDirichletAllocation(
                n_components=NUM_OF_TOPICS).fit(counts)
            fout_vect = 'models/' + country + '_vec_model.pickle'
            fout_lda = 'models/' + country + '_lda_model.pickle'
            pickle.dump(vectorizer, open(fout_vect, 'wb'))
            pickle.dump(lda, open(fout_lda, 'wb'))
            print(country + ' : Complete')


def build_SVD_models(all_tweets):
    for country_tweets in all_tweets:
        if len(country_tweets) > 0:
            country = country_tweets[0].get('country')
            country_tweets = get_text_only(country_tweets)
            vectorizer = TfidfVectorizer()
            tfidf = vectorizer.fit_transform(country_tweets)
            svd = create_svd(tfidf)
            fout_vect = 'models/' + country + '_tfidf_model.pickle'
            fout_lda = 'models/' + country + '_svd_model.pickle'
            pickle.dump(vectorizer, open(fout_vect, 'wb'))
            pickle.dump(svd, open(fout_lda, 'wb'))
            print(country + ' : Complete')


def create_models_lda(fin):
    tweet_json_lines = load_json(fin)
    all_tweets = separate_by_country(tweet_json_lines)
    stop_lists = create_stop_lists()
    build_topic_model(all_tweets, stop_lists)


def create_models_svd(fin):
    tweet_json_lines = load_json(fin)
    all_tweets = separate_by_country(tweet_json_lines)
    build_SVD_models(all_tweets)


def load_model_lda(fin_v, fin_lda):
    vectorizer = pickle.load(open(fin_v, 'rb'))
    lda = pickle.load(open(fin_lda, 'rb'))
    return lda, vectorizer


def load_model_svd(fin_v, fin_svd):
    vectorizer = pickle.load(open(fin_v, 'rb'))
    svd = pickle.load(open(fin_svd, 'rb'))
    return svd, vectorizer


def label_tweet(text):
    countries = {'Brazil', 'USA', 'India'}
    labels = {}
    for country in countries:
        fin_v = 'models/' + country + '_vec_model.pickle'
        fin_lda = 'models/' + country + '_lda_model.pickle'
        lda, vectorizer = load_model_lda(fin_v, fin_lda)
        label = str(np.argmax(lda.transform(vectorizer.transform([text]))))
        labels[country] = label
    return labels


def get_phrase_vectors(phrases, svd, vectorizer):
    ''' This converts the list of tweets returned by
    get_phrases and returns two lists. The indexes of
    each of the returned lists are important so these
    lists should never be shuffled or rearranged
    return: phrase_vectors is a list of all the 300-D vectors
    for each tweet
    poi_names is a list of the corresponding names'''
    # splitline is there to handle newline characters
    # rstrip does not work for this
    phrases_only = phrases[:, 0]
    phrase_vectors = np.array(
        [svd.transform(vectorizer.transform([phrase]))
         for phrase in phrases_only])
    poi_names = phrases[:, 1]
    return phrase_vectors, poi_names


def get_phrases(list_of_json_tweets):
    '''This gets the tweet text and poi name
    for each tweet it is given. It returns a list of tuples
    [(text, poi_name)]'''
    phrases = np.array([(json_tweet.get('tweet_text'),
                         json_tweet.get('poi_name'))
                        for json_tweet in list_of_json_tweets])
    return phrases


def load_model_svd(fin_v, fin_svd):
    vectorizer = pickle.load(open(fin_v, 'rb'))
    svd = pickle.load(open(fin_svd, 'rb'))
    return svd, vectorizer


def build_tweet_cloud(country, all_vec, all_names):
    '''This builds the first graph with all the color
    and overlapped dots. The graph created by this is one
    of all the tweets and represents how they relate to each other
    semantically in a two dimensional space'''
    all_vec = all_vec.reshape((all_vec.shape[0], 3))
    df_base = {'name': all_names,
               'phrase_x': all_vec[:, 0],
               'phrase_y': all_vec[:, 1],
               'phrase_z': all_vec[:, 2]}
    df = pd.DataFrame(df_base)
    encoder = LabelEncoder()
    df['code'] = encoder.fit_transform(df['name'])
    fig = plt.figure()
    cmap = plt.get_cmap('Accent')
    ax = fig.add_subplot(111, projection='3d')
    s = [.7 for n in all_names]
    s[-1] = 21
    scatter = ax.scatter(df['phrase_x'], df['phrase_y'], df['phrase_z'],
                         c=df['code'], marker='o', cmap=cmap, s=s, alpha=.7)
    leg = ax.legend(*scatter.legend_elements(), title='Person of Interest')
    for i, label in enumerate(encoder.classes_):
        leg.get_texts()[i].set_text(label)
    ax.set_title('Tweet Cloud')
    ax.view_init(32, -17)
    #plt.show()
    plt.savefig(country+'_tweet_cloud')


def tweet_cloud(tweet_file, query):
    tweets = load_json(tweet_file)
    country_tweets = separate_by_country(tweets)
    for tw in country_tweets:
        if len(tw) > 0:
            country = tw[0].get('country')
            svd, tfidf = load_model_svd('models/' + country + '_tfidf_model.pickle',
                                        'models/' + country + '_svd_model.pickle')
            phrases = get_phrases(tw)
            phrase_vec, poi_names = get_phrase_vectors(phrases, svd, tfidf)
            # Get Query Vector
            ex = tfidf.transform([query])
            Q_POINT = svd.transform(ex)
            # Combine vectors
            all_vec = np.append(phrase_vec, [Q_POINT], axis=0)
            all_names = np.append(poi_names, 'Query')
            build_tweet_cloud(country, all_vec, all_names)

def topic_chart(tweet_file, country):
    tweets = load_json(tweet_file)
    all_t = separate_by_country(tweets)
    fin_lda = 'models/' + country+'_lda_model.pickle'
    fin_v = 'models/' + country + '_vec_model.pickle'
    lda, vec = load_model_lda(fin_v, fin_lda)
    topics = [np.argmax(lda.transform(vec.transform([tweet.get('tweet_text')])))
              for tweet in tweets]
    df_base = {'Topics': topics}
    df = pd.DataFrame(df_base)
    cmap = plt.get_cmap('Accent')
    df1  = df['Topics'].value_counts()
    df1.plot.bar()
    #plt.show()
    plt.savefig(country+'top_chart')


def load_model_lda(fin_v, fin_lda):
    vectorizer = pickle.load(open(fin_v, 'rb'))
    lda = pickle.load(open(fin_lda, 'rb'))
    return lda, vectorizer

if flag in ('--svdcreate', '-svd'):
    create_models_svd(option)
if flag in ('--ldacreate', '-lda'):
    create_models_lda(option)
if flag in ('--label', '-l'):
   print(label_tweet(option))
if flag in ('--tweetcloud', '-tc'):
    tweet_cloud(option, query)
if flag in('--topicgraph', '-topg'):
    topic_chart(option, query)
