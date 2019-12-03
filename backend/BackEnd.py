import os
import json
import urllib.request 
from flask import Flask, request
from google import google
from collections import Counter
import pandas as pd

app = Flask(__name__)


@app.route('/search', methods = ['GET','POST'])
def returnJsonResult():
    if request.method =='POST':
        data = request.data
        decodeddata = data.decode('utf-8')
        jsondata =json.loads(decodeddata)
        # print(jsondata)
        
        
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
        
        if(each_query == ""):
            each_query = '#"*:*'
        each_query = each_query.replace(":", "\:")
        each_query = urllib.parse.quote(each_query)
        
        input_query = each_query
        
        ip = "13.59.238.116:8983"
        IRModel = "IRF19P1"
        
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

        if(verified == "true"):
             if(filter_query == ""):
                filter_query = "fq=" + "verified%3Atrue"
             else:
                filter_query = filter_query + and_append + "verified%3Atrue"

        
        #2019-09-07T00:00:00Z TO 2019-09-08T00:00:00Z
        #tweet_date%3A%5B2019-09-07T00%3A00%3A00Z%20TO%202019-09-08T00%3A00%3A00Z%5D%20
        tweet_date_from = jsondata.get('tweetDateFrom')
        tweet_date_to = jsondata.get('tweetDateTo')
        
        if(tweet_date_from != ""):
            tweetDateFrom = tweetDateFrom + "T00:00:00Z"
        
        if(tweet_date_to != ""):
            tweetDateTo = tweetDateTo + "T00:00:00Z"
        
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
            inurl = 'http://' + ip + '/solr/' + IRModel + '/select?' + filter_query + '&q='+ input_query #+'&rows=20'
        else:
            inurl = 'http://' + ip+'/solr/' + IRModel + '/select?defType=edismax&fq=' + filter_query +'&q=' + input_query #+'&rows=20'


        print(inurl)
        data = urllib.request.urlopen(inurl)
        docs = json.load(data)['response']['docs']
        #print(docs)
        print("length:", len(docs))
        # print(docs)

        date_list = list()
        lang_list = list()
        country_list = list()
        hashtags_list = list()
        for i in range(len(docs)):
            try:
                # date_time = docs[i].get("tweet_date")[0].find("T")
                # print(date_time)
                date_list.append(docs[i].get("tweet_date")[0][0:10])
                lang_list.append(docs[i].get("tweet_lang")[0])
                country_list.append(docs[i].get("country")[0])
                hashtags_list.append(docs[i].get("hashtags")[0])
            except:
                pass
        # print(date_list)
        date_list = dict(Counter(date_list))
        lang_list = dict(Counter(lang_list))
        country_list = dict(Counter(country_list))
        hashtags_list = dict(Counter(hashtags_list))

        print(date_list)
        print(lang_list)
        print(country_list)
        print(hashtags_list)

        country_data = {'country':['United States', 'India', 'Brazil'], 'Tweets':[country_list.get('USA'), country_list.get('India'), country_list.get('Brazil')], 'country code':['USA', 'IND', 'BRA']}
        country_df = pd.DataFrame(data)

        return json.dumps(docs)
    #print(docs[0])
    #print()
    #print(docs[1])
    #print("leng",len(docs))



# def main():
#     returnJsonResult()

# if __name__ == "__main__":
#      main()
        
#http://ec2-18-219-82-180.us-east-2.compute.amazonaws.com:8984/solr/IRF19P1/select?fq=country%3Aindia%20OR%20usa&fq=verified%3Atrue&q=*%3A*





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
    app.run()
    # returnNewsJsonResult()