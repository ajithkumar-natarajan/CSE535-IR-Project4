import os
import json
import urllib.request 
from flask import Flask, request
from google import google
from collections import Counter
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
import re 
import tweepy
from tweepy import OAuthHandler 
from textblob import TextBlob
from flask_cors import CORS, cross_origin


app = Flask(__name__)
CORS(app)


@app.route('/search', methods = ['GET','POST'])
def returnJsonResult():
    if request.method =='POST':
        data = request.data
        decodeddata = data.decode('utf-8')
        jsondata =json.loads(decodeddata)
        print(jsondata)
        
        
        # jsondata = {"query":"Lula", 
        #             "country":[], 
        #             "lang":[], 
        #             "verified":"",
        #             "topic":[],
        #             "tweetDateFrom":"",
        #             "tweetDateTo":"",
        #             "exactMatch":"true"}
        # jsondata = {"query":"modi", 
        #             "country":["india","usa"], 
        #             "lang":["en","hi"], 
        #             "verified":"false",
        #             "topic":[],
        #             "tweetDateTo":"2019-08-08T00:00:00Z",
        #             "tweetDateFrom":"2019-09-07T00:00:00Z",
        #             "exactMatch":"false"}
        each_query =  jsondata.get('query')
        
        each_query = each_query.replace(" ", "%20")
        if(each_query == ""):
            each_query = '#"*:*'
        else:
            each_query = "text_hi%3A"+each_query+"%20or%0A"+"text_en%3A"+each_query+"%20or%0A"+"text_pt%3A"+each_query
        # each_query = each_query.replace(":", "\:")
        # each_query = urllib.parse.quote(each_query)
        print(each_query)
        
        input_query = each_query
        
        ip = "18.191.55.237:8984"
        # IRModel = "IRF19P1"
        IRModel = "test"
        
        #country = ["india","usa"]
        country = jsondata.get('country')
        lang = jsondata.get('lang')#["en","hi"]
        topic = jsondata.get('topic')
        #verified = "true"
        verified = jsondata.get('verified')
        tweet_date_from = jsondata.get('tweetDateFrom')
        tweet_date_to = jsondata.get('tweetDateTo')
        
        #http://13.59.238.116:8983/solr/IRF19P1/select?q=*%3A*&rows=20

        #topic = []#["news"] 
        #inputQuery ="*%3A*"
        exact_match = jsondata.get('exactMatch')
        filter_query = ""
        append = "%20OR%20"
        and_append = "&fq="
        #2019-09-07T00:00:00Z TO 2019-09-08T00:00:00Z
        #tweet_date%3A%5B2019-09-07T00%3A00%3A00Z%20TO%202019-09-08T00%3A00%3A00Z%5D%20

        if(len(country) > 0):
            filter_query = "fq="
        else:
            filter_query = ""

        if(len(country) > 0):
            filter_query = filter_query +"country%3A"+country[0]

        for i in range(1,len(country)):
            filter_query = filter_query + append + country[i]
            #if(i != len(country) -1)# or len(lang) > 0 or len(topic) > 0 or verified == "true"):
             #   fq = fq+append

        # if(each_query != "ptshrikant"):
        if(len(lang)>0):
            if(filter_query == ""):
                filter_query = "fq=" + "tweet_lang%3A" + lang[0]
            else:
                filter_query = filter_query+and_append + "tweet_lang%3A" + lang[0]

        #if(len(lang) > 0)
        #    fq = fq +"tweet_lang%3A"+lang[0]

            for i in range(1, len(lang)):
                filter_query = filter_query + append + lang[i]
                if(i != len(lang) - 1):# or len(topic) > 0 or verified == "true"):
                    filter_query = filter_query + append

        if(len(topic) > 0):
             if(filter_query == ""):
                filter_query = "fq=" + "poi_name%3A" + topic[0]
             else:
                filter_query = filter_query + and_append + "poi_name%3A"+topic[0]

        for i in range(1, len(topic)):
            filter_query = filter_query + append + topic[i]
            #if(i != len(topic) -1 or verified == "true"):
             #   fq = fq+append       


        if(verified == True):
             if(filter_query == ""):
                filter_query = "fq=" + "verified%3Atrue"
             else:
                filter_query = filter_query + and_append + "verified%3Atrue"
        
        if(verified == False):
             if(filter_query == ""):
                filter_query = "fq=" + "verified%3Afalse"
             else:
                filter_query = filter_query + and_append + "verified%3Afalse"

        
        #2019-09-07T00:00:00Z TO 2019-09-08T00:00:00Z
        #tweet_date%3A%5B2019-09-07T00%3A00%3A00Z%20TO%202019-09-08T00%3A00%3A00Z%5D%20
        tweet_date_from = jsondata.get('tweetDateFrom')
        tweet_date_to = jsondata.get('tweetDateTo')
        
        if(tweet_date_from != ""):
            tweet_date_from = tweet_date_from + "T00:00:00Z"
        
        if(tweet_date_to != ""):
            tweet_date_to = tweet_date_to + "T00:00:00Z"
        
        if(tweet_date_from != "" and tweet_date_to != ""):
            date_filter = tweet_date_from + " TO " + tweet_date_to

            date_filter = date_filter.replace(":", "%3A")
            date_filter = date_filter.replace(" ", "%20")
            #print(date_filter)
            date_filter = "tweet_date%3A%5B" + date_filter + "%5D%20"
            #print(date_filter)
            if(filter_query == ""):
                filter_query = "fq=" + date_filter
            else:
                filter_query = filter_query + and_append + date_filter
        elif(tweet_date_from != ""):
            date_filter = tweet_date_from + " TO "

            date_filter = date_filter.replace(":", "%3A")
            date_filter = date_filter.replace(" ", "%20")
            #print(date_filter)
            date_filter = "tweet_date%3A%5B" + date_filter + "%20*%5D"
            #print(date_filter)
            if(filter_query == ""):
                filter_query = "fq=" + date_filter
            else:
                filter_query = filter_query + and_append + date_filter
        elif(tweet_date_to != ""):
        #tweet_date%3A%5B*%20TO%202019-09-08T00%3A00%3A00Z%5D
            date_filter = "TO " + tweet_date_to

            date_filter = date_filter.replace(":","%3A")
            date_filter = date_filter.replace(" ","%20")
            #print(date_filter)
            date_filter = "tweet_date%3A%5B*%20" + date_filter + "%5D"
            #print(date_filter)
            if(filter_query == ""):
                filter_query = "fq=" + date_filter
            else:
                filter_query = filter_query + and_append + date_filter

        print(filter_query)
        #http://18.218.221.88:8984/solr/BM25/select?defType=edismax&q=ARTIKEL&wt=json
        #http://18.218.221.88:8984/solr/BM25/select?defType=edismax&q=Anti-Refugee%20Rally%20in%20Dresden&fl=id%2Cscore&wt=json&indent=true&rows=20
        #http://ec2-18-219-82-180.us-east-2.compute.amazonaws.com:8984/solr/IRF19P1/select?fq=tweet_date%3A%5B2019-09-07T00%3A00%3A00Z%20TO%202019-09-08T00%3A00%3A00Z%5D%20AND%20verified%3Atrue&q=*%3A*
        #tweet_date:[2019-09-07T00:00:00Z TO 2019-09-08T00:00:00Z] AND verified:true 
        if(exact_match):
            inurl = 'http://' + ip + '/solr/' + IRModel + '/select?' + filter_query + '&q='+ input_query +'&rows=1000'
            # if(jsondata.get('query') == "isro"):
            #     inurl = 'http://' + ip + '/solr/' + IRModel + '/select?' + filter_query + '&q='+ input_query +'&rows=124'
        else:
            inurl = 'http://' + ip+'/solr/' + IRModel + '/select?defType=edismax&' + filter_query +'&q=' + input_query +'&rows=1000'


        print(inurl)
        data = urllib.request.urlopen(inurl)
        docs = json.load(data)['response']['docs']
        #print(docs)
        print("length:", len(docs))

        sentiment_list = dict()
        sentiment_list['positive'] = 0
        sentiment_list['neutral'] = 0
        sentiment_list['negative'] = 0
        for tweet_texts in docs:
            sentiment = sentiment_analyse(tweet_texts['tweet_text'][0])
            tweet_texts['sentiment'] = sentiment
            sentiment_list[sentiment] = sentiment_list.get(sentiment)+1
            # print(tweet_texts)

        date_list = list()
        lang_list = list()
        country_list = list()
        hashtags_list = list()
        mentions_list = list()
        date_lang_list = dict()
        topics = dict()

        for i in range(len(docs)):
            try:
                # date_time = docs[i].get("tweet_date")[0].find("T")
                # print(date_time)
                date_list.append(docs[i].get("tweet_date")[0][0:10])
                doc_tweet_lang = docs[i].get("tweet_lang")[0]
                lang_list.append(doc_tweet_lang)
                tweet_topic = docs[i].get("topic")[0]
                if(doc_tweet_lang in date_lang_list):
                    date_lang_list[doc_tweet_lang].append(docs[i].get("tweet_date")[0][0:10])
                else:
                    date_lang_list[doc_tweet_lang] = list()
                    date_lang_list[doc_tweet_lang].append(docs[i].get("tweet_date")[0][0:10])
                if(tweet_topic in topics):
                    topics[tweet_topic] = topics.get(tweet_topic)+1
                else:
                    topics[tweet_topic] = 1
                
                country_list.append(docs[i].get("country")[0])
                hashtags_list.append(docs[i].get("hashtags")[0])
                mentions_list.append(docs[i].get("mentions")[0])
            except:
                pass
        # print(date_list)
        # try:
        date_list = dict(Counter(date_list))
        lang_list = dict(Counter(lang_list))
        country_list = dict(Counter(country_list))
        hashtags_list = dict(Counter(hashtags_list))
        mentions_list = dict(Counter(mentions_list))

        for key in date_lang_list:
            date_lang_list[key] = dict(Counter(date_lang_list[key]))

        # print(date_list)
        # print(lang_list)
        # print(country_list)
        # print(hashtags_list)
        # print(mentions_list)
        # print(date_lang_list)

        country_data = {'country':['United States', 'India', 'Brazil'], 'Tweets':[country_list.get('USA'), country_list.get('India'), country_list.get('Brazil')], 'country code':['USA', 'IND', 'BRA']}
        country_df = pd.DataFrame(country_data)


        fig = px.choropleth(country_df, locations="country code",
                            color="Tweets",
                            hover_name="country",
                            color_continuous_scale='plasma')
        # pio.show(fig)
        # pio.write_html(fig, file='Location.html', default_width='370px', default_height='370px')
        fig.update_layout(title="Heatmap of count of tweets from different countries")
        pio.write_html(fig, file='Location.html')

        fig = go.Figure(data=[go.Pie(labels=list(lang_list.keys()), values=list(lang_list.values()))])
        # pio.show(fig)
        # pio.write_html(fig, file='Language.html', default_width='370px', default_height='370px')
        fig.update_layout(title="Pie chart of count of tweets in different languages")
        pio.write_html(fig, file='Language.html')


        date_list_key_sorted = list()
        date_list_value_sorted = list()
        for i in sorted (date_list.keys()):
            date_list_key_sorted.append(i)
            date_list_value_sorted.append(date_list.get(i))
        fig = go.Figure(go.Scatter(x=date_list_key_sorted, y=date_list_value_sorted))
        fig.update_xaxes(title_text='Dates')
        fig.update_yaxes(title_text='No of tweets')
        fig.update_layout(title="Number of tweet on different dates")
        # pio.show(fig)
        # pio.write_html(fig, file='TimeSeries.html', default_width='370px', default_height='370px')
        pio.write_html(fig, file='TimeSeries.html')

        fig = go.Figure()
        for key in date_lang_list:
            date_lang_list_key_sorted = list()
            date_lang_list_value_sorted = list()
            for i in sorted (date_lang_list[key].keys()):
                date_lang_list_key_sorted.append(i)
                date_lang_list_value_sorted.append(date_lang_list[key].get(i))

            fig.add_trace(go.Scatter(
                    x=date_lang_list_key_sorted,
                    y=date_lang_list_value_sorted,
                    name=key,
                    # line_color='deepskyblue',
                    opacity=0.8))

            # print(date_lang_list_key_sorted, date_lang_list_value_sorted)
        fig.update_xaxes(title_text='Dates')
        fig.update_yaxes(title_text='No of tweets')
        # fig.update_layout(title={'text':"Number of tweet on different dates", 'xanchor': 'left'})
        fig.update_layout(title="Number of tweet in different languages on different dates")
        # pio.write_html(fig, file='TimeSeriesLanguage.html', default_width='370px', default_height='370px')
        pio.write_html(fig, file='TimeSeriesLanguage.html')

# fig.add_trace(go.Scatter(
#                 x=date_list_key_sorted_1,
#                 y=date_list_value_sorted_1,
#                 name="AAPL Low",
#                 line_color='dimgray',
#                 opacity=0.8))

# Use date string to set xaxis range
# fig.update_layout(xaxis_range=['2016-07-01','2016-12-31'],
                  # title_text="Manually Set Date Range")
# fig.show()

        fig = {
            "data": [{"type": "bar",
            "x": list(hashtags_list.keys()),
            "y": list(hashtags_list.values())}],
            "layout": {"title": {"text": "Number of tweets per hashtag"}}
            }
        # fig.update_xaxes(title_text='Hashtags')
        # fig.update_yaxes(title_text='No of tweets')

        # pio.show(fig)
        # pio.write_html(fig, file='Hashtags.html', default_width='370px', default_height='370px')
        pio.write_html(fig, file='Hashtags.html')

        fig = {
            "data": [{"type": "bar",
            "x": list(mentions_list.keys()),
            "y": list(mentions_list.values())}],
            "layout": {"title": {"text": "Number of tweets per mention"}}
            }
        # fig.update_xaxes(title_text='Mention')
        # fig.update_yaxes(title_text='No of tweets')

        # pio.show(fig)
        # pio.write_html(fig, file='Mentions.html', default_width='370px', default_height='370px')
        pio.write_html(fig, file='Mentions.html')

        fig = go.Figure(data=[go.Pie(labels=list(topics.keys()), values=list(topics.values()))])
        # pio.show(fig)
        # pio.write_html(fig, file='Topics.html', default_width='370px', default_height='370px')
        fig.update_layout(title="Pie chart of count of tweets in different languages")
        pio.write_html(fig, file='Topics.html')

        fig = go.Figure(data=[go.Pie(labels=list(sentiment_list.keys()), values=list(sentiment_list.values()))])
        # pio.show(fig)
        # pio.write_html(fig, file='Language.html', default_width='370px', default_height='370px')
        fig.update_layout(title="Result of sentiment analysis on the query result")
        pio.write_html(fig, file='Sentiments.html')

        # except:
            # pass

#         labels = date_list_key_sorted
# values = date_list_value_sorted

    #print(docs[0])
    #print()
    #print(docs[1])
    #print("leng",len(docs))


        return json.dumps(docs)

# def main():
#     returnJsonResult()

# if __name__ == "__main__":
#      main()
        
#http://ec2-18-219-82-180.us-east-2.compute.amazonaws.com:8984/solr/IRF19P1/select?fq=country%3Aindia%20OR%20usa&fq=verified%3Atrue&q=*%3A*



def clean_tweet(tweet):
    
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

def sentiment_analyse(tweet_text_to_analyse): 

    analysis = TextBlob(clean_tweet(tweet_text_to_analyse)) 
    
    if analysis.sentiment.polarity > 0: 
        return 'positive'
    elif analysis.sentiment.polarity == 0: 
        return 'neutral'
    else: 
        return 'negative'


# @app.route("/")

"""
INSATLL THE MODULE USING THIS COMMAND:
pip install git+https://github.com/abenassi/Google-Search-API
"""

@app.route('/news', methods = ['GET','POST'])
def returnNewsJsonResult():
    if request.method =='POST':
        data = request.data
        decodeddata = data.decode('utf-8')
        jsondata =json.loads(decodeddata)
        
        each_query =  jsondata.get('query')
        
        
        num_page = 1
        # query = "Modi"
        search_results = google.search(each_query + "news", num_page)
        newsList = list()
        for result in search_results:
            newsJson = dict()
            http_loc = result.name.find("http")
            newsJson['title'] = result.name[0: http_loc]
            newsJson['desc'] = result.description
            newsJson['url'] = result.link
            newsList.append(newsJson)

        print(json.dumps(newsList))
        return json.dumps(newsList)


if __name__ == "__main__":
    # print("In program")
    #Uncomment below line to run in local system (Comment below line to in server)
    app.run()
    #Comment below line to run in local system (Uncomment below line to in server)
    app.run(host= '0.0.0.0')
    # returnNewsJsonResult()
