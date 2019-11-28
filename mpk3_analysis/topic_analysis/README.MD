# Topic Modeling

This file uses LDA to find topics for each country. The topics have numerical labels currently but this can be changed to words/word clouds when I have all the tweets.  5 topics were 'found' for each country. The output corresponds to the label for each specific country.

### To create the models:
- This only needs to be done once with all of the poi tweets

>? run ta.py --create 'sample\_poi_tweets.jsonl'
>USA : Complete
>India : Complete
>Brazil : Complete
### To label text:
- This can be used to label all of the tweets by looping it over each tweet
- It can also be used to label queries

>?run ta.py --label 'The president loves fried chicken'
>{'Brazil': '3', 'India': '0', 'USA': '0'}

