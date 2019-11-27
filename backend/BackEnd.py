
# coding: utf-8

# In[42]:



import os
import json
import urllib.request 
from flask import Flask, request
# from flask import Flask
app = Flask(__name__)


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
        #temp = c.get('') #frontend ID
        eachquery =  jsondata.get('query')
        #print(eachquery)
        if(eachquery == ""):
            eachquery=""#"*:*"
        eachquery = eachquery.replace(":","\:")
        eachquery = urllib.parse.quote(eachquery)
        #print(eachquery)
        inputQuery = eachquery
        ip = "18.217.246.4:8984"
        ip = "13.59.238.116:8983"
        IRModel = "IRF19P1"
        # IRModel = "IRF19"

        #country = ["india","usa"]
        country = jsondata.get('country')
        lang = jsondata.get('lang')#["en","hi"]
        topic = jsondata.get('topic')
        #verified = "true"
        verified = jsondata.get('verified')
        tweetDateFrom = jsondata.get('tweetDateFrom')
        tweetDateTo =jsondata.get('tweetDateTo')
        #tweet_date:
        #poi_name:khmerblanche000 OR poi_name:sweposten
        #%7C
        #http://18.218.221.88:8984/solr/IRF19P1/select?q=*%3A*&rows=20

        #country = ["india","usa"]
        #lang =[]# ["en","hi"]
        #topic = []#["news"] 
        #inputQuery ="*%3A*"
        exactMatch = jsondata.get('exactMatch')
        fq = ""
        append ="%20OR%20"
        andAppend ="&fq="
        #2019-09-07T00:00:00Z TO 2019-09-08T00:00:00Z
        #tweet_date%3A%5B2019-09-07T00%3A00%3A00Z%20TO%202019-09-08T00%3A00%3A00Z%5D%20

        if(len(country) > 0):
            fq = "fq="
        else:
            fq = ""

        if(len(country) > 0):
            fq = fq +"country%3A"+country[0]

        for i in range(1,len(country)): 
            fq = fq +append+country[i]
            #if(i != len(country) -1)# or len(lang) > 0 or len(topic) > 0 or verified == "true"):
             #   fq = fq+append

        if(len(lang) > 0):
            if(fq == ""):
                fq = "fq="+"tweet_lang%3A"+lang[0]
            else:
                fq = fq+andAppend +"tweet_lang%3A"+lang[0]

        #if(len(lang) > 0)
        #    fq = fq +"tweet_lang%3A"+lang[0]

        for i in range(1,len(lang)):
            fq = fq +append+lang[i]
            if(i != len(lang) -1):# or len(topic) > 0 or verified == "true"):
                fq = fq+append

        if(len(topic) > 0):
             if(fq == ""):
                fq = "fq="+"poi_name%3A"+topic[0]
             else:
                fq = fq+andAppend+"poi_name%3A"+topic[0]

        for i in range(1,len(topic)):
            fq = fq +append+topic[i]
            #if(i != len(topic) -1 or verified == "true"):
             #   fq = fq+append       

        if(verified == "true"):
             if(fq == ""):
                fq = "fq=" + "verified%3Atrue"
             else:
                fq = fq+andAppend+"verified%3Atrue"

        
        #2019-09-07T00:00:00Z TO 2019-09-08T00:00:00Z
        #tweet_date%3A%5B2019-09-07T00%3A00%3A00Z%20TO%202019-09-08T00%3A00%3A00Z%5D%20
        tweetDateFrom = jsondata.get('tweetDateFrom')
        tweetDateTo =jsondata.get('tweetDateTo')
        if(tweetDateFrom !="" and tweetDateTo !=""):
            a =tweetDateFrom+" TO "+tweetDateTo

            a=a.replace(":","%3A")
            a=a.replace(" ","%20")
            #print(a)
            a="tweet_date%3A%5B"+a+"%5D%20"
            #print(a)
            if(fq == ""):
                fq = "fq=" + a
            else:
                fq = fq+andAppend+a
        elif(tweetDateFrom !=""):
            a =tweetDateFrom+" TO "

            a=a.replace(":","%3A")
            a=a.replace(" ","%20")
            #print(a)
            a="tweet_date%3A%5B"+a+"%20*%5D"
            #print(a)
            if(fq == ""):
                fq = "fq=" + a
            else:
                fq = fq+andAppend+a
        elif(tweetDateTo != ""):
        #tweet_date%3A%5B*%20TO%202019-09-08T00%3A00%3A00Z%5D
            a ="TO "+tweetDateTo

            a=a.replace(":","%3A")
            a=a.replace(" ","%20")
            #print(a)
            a="tweet_date%3A%5B*%20"+a+"%5D"
            #print(a)
            if(fq == ""):
                fq = "fq=" + a
            else:
                fq = fq+andAppend+a
            
            

        print(fq)
        #http://18.218.221.88:8984/solr/BM25/select?defType=edismax&q=ARTIKEL&wt=json
        #http://18.218.221.88:8984/solr/BM25/select?defType=edismax&q=Anti-Refugee%20Rally%20in%20Dresden&fl=id%2Cscore&wt=json&indent=true&rows=20
        #http://ec2-18-219-82-180.us-east-2.compute.amazonaws.com:8984/solr/IRF19P1/select?fq=tweet_date%3A%5B2019-09-07T00%3A00%3A00Z%20TO%202019-09-08T00%3A00%3A00Z%5D%20AND%20verified%3Atrue&q=*%3A*
        #tweet_date:[2019-09-07T00:00:00Z TO 2019-09-08T00:00:00Z] AND verified:true 
        if(exactMatch):
            inurl = 'http://'+ip+'/solr/'+IRModel+'/select?'+fq+'&q='+inputQuery #+'&rows=20'
        else:
            inurl = 'http://'+ip+'/solr/'+IRModel+'/select?defType=edismax&fq='+fq+'&q='+inputQuery #+'&rows=20'


        print(inurl)
        data = urllib.request.urlopen(inurl)
        docs = json.load(data)['response']['docs']
        #print(docs)
        print("leng",len(docs))
        print(docs)
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


if __name__ == "__main__":
    app.run()