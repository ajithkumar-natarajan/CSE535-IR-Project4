# Topic Model and TweetCloud

This file now produces a tweet cloud (a vector space 3-D representation of tweets and queries) and a bar graph for topics. Given a list of jsonl tweets , this file can create a tweet cloud of the results and the query. Given a list of jsonl tweets and a country, this file will create a bar graph showing the how the topics are split in the results. The json objects in the jsonl file passed to it just need values for 'tweet_text', 'country', and 'poi\_name'. The final models are in the models/ file. They do not need to be updated. I uploaded two sample files. The samples are pretty simple because I only created them with files that only had 1-3 pois in them. If you run this with jsonl files that have more hetergenous pois they will look a lot better. 

### To create Topic bar graph:
> python ta.py --topicgraph results.jsonl USA 
>> USA , India, or Brazil 
### To create TweetCloud:
> python ta.py --tweetcloud results.jsonl 'this is my query' 

### Output:
When run these files will output png files of each of the graphs. 
This can be changed if you want the figure to be interactive.
The files output are country+'\_tweet_cloud.png' and 'country+\_top\_chart.png'
The Topic Bar output is always only one graph.
The TweetCloud output is as many graphs as there are countries in the results file passed to it.
ex: If there are tweets from two countries in the results tweets a tweetcloud graph will be produced
for each country

###
all_tweets.jsonl is a file of roughly 90k tweets. Most are POI tweets. Only about 4k response tweets. These are the files I used to train my models on.
