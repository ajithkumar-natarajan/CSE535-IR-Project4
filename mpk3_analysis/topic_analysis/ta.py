from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import fasttext
import pickle
import sys
import numpy as np

'''
This file does topic analysis on POI tweets
Please make sure when you send tweets to this
file they are in a jsonl file

The point of this file is:

1) to create an LDA model 
2) Save model as a pickled file 
3) Use the pickled file to load a model
4) Use that model to classify tweets


I didnt want to create two separate fo
(1) Get tweets and separate and country
(2) Perform LDA '''
NUM_OF_TOPICS = 5
LANG_DETECT_MODEL = '/home/mpk3/Desktop/IR_Final/analytics/ft/models/lid.176.ftz'
# print(str(sys.argv[1]))
flag = sys.argv[1] # --create or --label
option = sys.argv[2]



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
    ''' This detects the language of a string of text
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
            fout_vect = country + '_vec_model.pickle'
            fout_lda = country + '_lda_model.pickle'
            pickle.dump(vectorizer, open(fout_vect, 'wb'))
            pickle.dump(lda, open(fout_lda, 'wb'))
            print(country + ' : Complete')


def create_models(fin):
    # Delete me after testing
    fin = 'poi_tweets.jsonl'
    tweet_json_lines = load_json(fin)
    all_tweets = separate_by_country(tweet_json_lines)
    stop_lists = create_stop_lists()
    build_topic_model(all_tweets, stop_lists)


def load_model(fin_v, fin_lda):
    vectorizer = pickle.load(open(fin_v, 'rb'))
    lda = pickle.load(open(fin_lda, 'rb'))
    return lda, vectorizer


def label_tweet(text):
    countries = {'Brazil', 'USA', 'India'}
    labels = {}
    for country in countries:
        fin_v = country + '_vec_model.pickle'
        fin_lda = country + '_lda_model.pickle'
        lda, vectorizer = load_model(fin_v, fin_lda)
        label = str(np.argmax(lda.transform(vectorizer.transform([text]))))
        labels[country] = label
    return labels


if flag in ('--create', '-c'):
    create_models(option)
if flag in ('--label', '-l'):
    print(label_tweet(option))


# Test
#option = ('poi_tweets.jsonl')
#create_models(option)
#option = ('the president is dumb')
#print(str(label_tweet(option)))
# This is straight out of Scikit learns tutorial
# It will not be used in our project but I am using it
# To inspect things

#def print_top_words(model, feature_names, n_top_words):
#    for topic_idx, topic in enumerate(model.components_):
#        message = "Topic #%d: " % topic_idx
#        message += " ".join([feature_names[i]
#                             for i in topic.argsort()[:-n_top_words - 1:-1]])
#        print(message)