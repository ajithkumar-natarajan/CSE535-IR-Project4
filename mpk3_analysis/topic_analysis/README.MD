# Topic Modeling

This file uses LDA to find topics for each country. The topics have numerical labels currently but this can be changed to words/word clouds when I have all the tweets.  5 topics were 'found' for each country. The output corresponds to the category the text belongs to for each specific country. The poi tweets only need to be labeled according to the country group they belong to. If we use this model to label queries you could use all three labels to show how the query fits in to each country group. For a little more detail check out the script. The models are fit on the poi tweets and these models then predict the label of the input text

### To create the models:
- This only needs to be done once with all of the poi tweets
- The file should be a jsonl file of all of the tweets

> python ta.py --create 'sample\_poi_tweets.jsonl'

>> USA : Complete

>> India : Complete

>> Brazil : Complete

### To label text:
- This can be used to label all of the tweets by looping it over each tweet
- It can also be used to label queries

> python ta.py --label 'The president loves fried chicken'

>> {'Brazil': '3', 'India': '0', 'USA': '0'}
