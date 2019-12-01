import tweepy as tw
import pytz
import datetime
import time
import numpy as np

NUM_POI_TWEETS = 3000
NUM_REPLY_TWEETS = 3000


users = ["mikeallen",
         "seanhannity",
         "daveweigel",
         "jaketapper",
         "maddow",
         "BDUTT",
         "sardesairajdeep",
         "sagarikaghose",
         "narendramodi",
         "vikramchandra",
         "marcofeliciano",
         "BolsonaroSP",
         "jairbolsonaro",
         "MarinaSilva",
         "PastorMalafaia"]

india = {"BDUTT",
         "sardesairajdeep",
         "sagarikaghose",
         "narendramodi",
         "vikramchandra"}

usa = {"mikeallen",
       "seanhannity",
       "daveweigel",
       "jaketapper",
       "maddow"}

brazil = {"marcofeliciano",
          "BolsonaroSP",
          "jairbolsonaro",
          "MarinaSilva",
          "PastorMalafaia"}

debug = False
oauth_consumer_key = 'XXX'
oauth_consumer_secret = 'XXX'
oauth_access_token = 'XXXX'
oauth_access_token_secret = 'XXXX'

auth = tw.OAuthHandler(oauth_consumer_key, oauth_consumer_secret)
auth.set_access_token(oauth_access_token, oauth_access_token_secret)

# Authentication Check

api = tw.API(auth)
# api.update_status('instance check')


def load_json(jsonl_fin):
    ''' Method for loading jsonl files'''
    tweet_json_lines = np.array([])
    with open(jsonl_fin) as fin:
        line = fin.readline()
        while line:
            tweet_json_lines = np.append(tweet_json_lines, eval(line))
            line = fin.readline()
    return tweet_json_lines


def limiter(cursor):
    while 1:
        try:
            yield cursor.next()
        except tw.RateLimitError:
            print("RLE" + str(datetime.datetime.now()))
            time.sleep(15*60)
        except tw.TweepError as e:
            print(e)
            time.sleep(15*60)


def get_tweets(users):
    for user in users:
        for status in limiter(
                tw.Cursor(api.user_timeline(), username=user).pages(1)):
            print(status.text)


def loc_check(user):
    if user in usa:
        loc = 'USA'
    if user in india:
        loc = 'India'
    if user in brazil:
        loc = 'Brazil'
    return loc


def gmt_round_hour(date):
    gmt = pytz.timezone('GMT')
    dt = date.astimezone(gmt)
    if dt.minute == 30 and dt.second > 0:
        dt = dt + datetime.timedelta(hours=1)
        dt = dt.replace(minute=0)
        dt = dt.replace(second=0)
    if dt.minute > 30:
        dt = dt + datetime.timedelta(hours=1)
        dt = dt.replace(minute=0)
        dt = dt.replace(second=0)
    else:
        dt = dt - datetime.timedelta(hours=1)
        dt = dt.replace(minute=0)
        dt = dt.replace(second=0)
    return dt.isoformat()


# Driver
poi_id_numbers = {}
statuses = []
for name in users:
    loc = loc_check(name)
    print('Statuses ' + name + ' ' + str(datetime.datetime.now()))
    for status in limiter(tw.Cursor(api.user_timeline, screen_name=name, tweet_mode="extended")
                          .items(NUM_POI_TWEETS)):
        poi_id_numbers[name] = status.user.id_str
        statuses.append({'tweet_text': status.full_text,
                         'id_str': status.id_str,
                         'replied_to_tweet_id': None,
                         'replied_to_user_id': None,
                         'reply_text': None,
                         'tweet_lang': status.lang,
                         'hashtags': status.entities.get('hashtags'),
                         'mentions': [mention.get('screen_name')
                                      for mention in
                                      status.entities.get('user_mentions')],
                         'tweet_urls': [url.get('expanded_url') for url in
                                        status.entities.get('urls')],
                         'tweet_emoticons': [],
                         'tweet_date': gmt_round_hour(status.created_at),
                         'poi_name': status.user.screen_name,
                         'poi_id': status.user.id_str,
                         'verified': status.user.verified,
                         'country': loc})

statuses = load_json('/home/mpk3/Desktop/IR_Final/twitter/poi_tweets.jsonl')
id_names = [(ob.get('poi_name'), ob.get('id_str')) for ob in statuses]


def check_tweet_unique(idnames):
    idnames = np.split(np.array(idnames), 15)
    for poi in idnames:
        num_poi = len(np.unique(poi.T[0]))
        num_uniq_tweets = len(np.unique(poi.T[1]))
        if num_poi != 1:
            print(poi.T[0][0] + ' ' + str(num_poi) + ' poicount')
        if num_uniq_tweets != 3000:
            print(poi.T[0][0] + ' ' + str(num_uniq_tweets) + ' tweetcount')
        else:
            print(poi.T[0][0] + ' '+'All good')


def out_jsonl(tweetarray, handle):
    handle = handle + '.jsonl'
    with open(handle, 'w+') as fout:
        for tweet in tweetarray:
            fout.write('%s\n' % tweet)


out_jsonl(statuses, 'poi_tweets')
print('Poi tweets complete')

def reply_id_check(tweet):
    if tweet.in_reply_status_id is not None:
        return True
    else:
        return False

split = {} 
for x, y in id_names: 
    if x in split: 
        split[x].append((x, y))
    else: 
        split[x] = [(x, y)]
# Driver for response tweets

AXIS_NUM = 2999
replies = []
for user_set in split.keys():
    username = user_set
    print('Replies ' + username + ' ' + str(datetime.datetime.now()))
    q_string = 'to%3A' + username
    lowest_id = int(split[username][-1][1])
    id_set = set([i[1] for i in split[username]])
    for status in limiter(
            tw.Cursor(api.search, q=q_string,
                      since_id=lowest_id, tweet_mode='extended').items(NUM_REPLY_TWEETS)):
        if status.in_reply_to_status_id is not None:
            if status.in_reply_to_status_id_str in id_set:
                replies.append({'tweet_text': status.full_text,
                                'id_str': status.id_str,
                                'replied_to_tweet_id':
                                status.in_reply_to_status_id_str,
                                'replied_to_user_id':
                                status.in_reply_to_user_id_str,
                                'reply_text': status.full_text,
                                'tweet_lang': status.lang,
                                'hashtags': status.entities.get('hashtags'),
                                'mentions': [mention.get('screen_name')
                                             for mention in
                                             status.entities.
                                             get('user_mentions')],
                                'tweet_urls': [url.get('expanded_url')
                                               for url in
                                               status.entities.get('urls')],
                                'tweet_emoticons': [],
                                'tweet_date':
                                gmt_round_hour(status.created_at),
                                'poi_name': username,
                                'poi_id': poi_id_numbers.get(username),
                                'verified': status.user.verified,
                                'country': loc_check(username)})

out_jsonl(replies, 'poi_replies')
print('Poi tweets complete')
#n = np.split(np.array(statuses), 15)
#o = [(y[0].get('poi_id'), y[0].get('poi_name')) for y in n]
