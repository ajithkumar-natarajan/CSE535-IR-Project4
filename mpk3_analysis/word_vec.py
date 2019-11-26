from sklearn.decomposition import PCA
from sklearn import preprocessing
import fasttext
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

### All of this stuff is specific to my computer and needs to be changed
model_lang = '/home/mpk3/Desktop/IR_Final/analytics/ft/models/lid.176.ftz'
models = {}
models['hi'] = '/home/mpk3/Desktop/IR_Final/analytics/ft/models/wiki.hi.bin'
models['en'] = '/home/mpk3/Desktop/IR_Final/analytics/ft/models/wiki.en.bin'
models['pt'] = '/home/mpk3/Desktop/IR_Final/analytics/ft/models/wiki.pt.bin'

# These are files and stuff specific to my computer because something is
# wrong with my tweets so I had to separate them out in a weird way.
test_tweet_fin = '/home/mpk3/Desktop/IR_Final/analytics/test_tweets.jsonl'
trial = '/home/mpk3/Desktop/IR_Final/analytics/poi.jsonl'
eng_poi_dict = {"KimKardashian",
         "katyperry",
         "joerogan",
         "jaketapper",
         "maddow"}

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
    detector = fasttext.load_model(model_lang)
    return detector.predict(tweet)[0][0][-2:]


def get_model(language):
    ''' This loads a language model based on the
    text value returned by detect_language'''
    model_fin = models.get(language)
    model = fasttext.load_model(model_fin)
    return model


def get_phrases(list_of_json_tweets):
    '''This gets the tweet text and poi name
    for each tweet it is given. It returns a list of tuples
    [(text, poi_name)]'''
    phrases = np.array([(json_tweet.get('tweet_text'),
                         json_tweet.get('poi_name'))
                        for json_tweet in list_of_json_tweets])
    return phrases


def get_phrase_vectors(phrases, model):
    ''' This converts the list of tweets returned by
    get_phrases and returns two lists. The indexes of
    each of the returned lists are important so these 
    lists should never be shuffled or rearranged
    return: 
    phrase_vectors is a list of all the 300-D vectors
    for each tweet
    poi_names is a list of the corresponding names'''
    # splitline is there to handle newline characters
    # rstrip does not work for this
    phrase_vectors = np.array(
        [model.get_sentence_vector(
            ' '.join(phrase[0].splitlines()))
         for phrase in phrases])
    poi_names = phrases[:, 1]
    return phrase_vectors, poi_names


def create_pca(phrase_vectors):
    '''This builds a PCA model based on the
    the phrase_vectors returned by get_phrase_vectors
    return:
    PCA model used to convert the 300-D vectors to 2-D'''
    pca = PCA(n_components=2)
    pca.fit(phrase_vectors)
    return pca


def pca_all_tweets_2D(pca, phrase_vectors):
    ''' Convert 300D vectors to 2D
    return: List of 2-D vectors'''
    phrase_vec_2D = pca.transform(phrase_vectors)
    # zero mean; unit variance; makes things easier
    standardized_vectors_2D = preprocessing.scale(phrase_vec_2D)
    return standardized_vectors_2D


def build_tweet_graph(phrase_vectors_2D, poi_names):
    '''This builds the first graph with all the color
    and overlapped dots. The graph created by this is one
    of all the tweets and represents how they relate to each other
    semantically in a two dimensional space'''
    df_base = {'name': poi_names,
               'phrase_x': phrase_vectors_2D[:, 0],
               'phrase_y': phrase_vectors_2D[:, 1]}
    df = pd.DataFrame(df_base)
    encoder = preprocessing.LabelEncoder()
    df['code'] = encoder.fit_transform(df['name'])
    df.plot(x='phrase_x', y='phrase_y',
            c='code', colormap='viridis', kind='scatter')
    plt.show()


def build_poi_graph(phrase_vectors_2D, poi_names):
    '''Creates the graph with the POI names'''
    df_base = {'name': poi_names,
               'phrase_x': phrase_vectors_2D[:, 0],
               'phrase_y': phrase_vectors_2D[:, 1]}
    df = pd.DataFrame(df_base)
    encoder = preprocessing.LabelEncoder()
    df['code'] = encoder.fit_transform(df['name'])
    # df = df.groupby('code', as_index=False)['phrase_x', 'phrase_y'].mean()
    df = df.groupby(['code', 'name'], as_index=False)['phrase_x', 'phrase_y'].mean()
    plotty = sns.regplot(data=df, x='phrase_x', y='phrase_y', fit_reg=False,
                         marker='o', color='skyblue', scatter_kws={'s': 400})
    for line in range(0, df.shape[0]):
        plotty.text(df.phrase_x[line], df.phrase_y[line], df.name[line],
                    horizontalalignment='left', size='medium',
                    color='black', weight='semibold')
    # df.plot(x='phrase_x', y='phrase_y',
    #        c='code', colormap='viridis', kind='scatter')
    plt.show()


def build_and_graph(tweets):
    '''This is a utility function for creating the PCA model
    and the graphs. This requires a global variable 'mod' in order to work
    mod is a loaded language model from fasttext'''
    phrases = get_phrases(tweets)
    phrase_vec, poi_names = get_phrase_vectors(phrases, mod)
    pca = create_pca(phrase_vec)
    phrase_vectors_2D = pca_all_tweets_2D(pca, phrase_vec)
    build_tweet_graph(phrase_vectors_2D, poi_names)
    build_poi_graph(phrase_vectors_2D, poi_names)
    # Then I want to have a different color on thi same graph for each POI
# Then I want have a phrase be put on this graph


#########################################################
# Driver
# This will be changed for implementation
# Loading a model takes about 1.5 mins
# This should not be done everytime a query is posed
# It should be set up so this and the PCA models are already loaded

x = detect_language('This is english you dumbass')  # returns 'en'
mod = get_model(x)  # needs bin model from fasttext
tweets = load_json(trial)  # Trial should be changed to where your tweets are

# This is the only thing needed to be done by anyone trying to test this out
# besides loading the appropriate models
# en just needs to be a list of all of the tweets in English
en = tweets[np.array([tweet.get('poi_name')
                      in eng_poi_dict for tweet in tweets])]
# hi = tweets[np.array([tweet.get('country') is 'India' for tweet in tweets])]
# pt = tweets[np.array([tweet.get('country') is 'Brazil' for tweet in tweets])]

# This does everything including building the PCA models that are
# used. I will change this
build_and_graph(en)
