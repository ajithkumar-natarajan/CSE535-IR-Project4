### HEYYY
# This is not finished yet
The general goal of all of this is essentially to create embeddings/vectors for each tweet and query. These vectors are 300 dimensions so PCA is used to reduce these dimensions down to 2. These then are usewd to create a graph which can show how the queries relate semantically to tweets, topics, or specific POIs. 

This does not have the topic model included yet nor does it have a part to include a query. 

I am going to add substantially more to this README very soon.

BIG CAVEAT:

The models used in this are from fasttext. They are rather large and one model is required per language. They should be all be loaded before queries are posed for our model. 

The current file that I have loaded is a working model for the English version of this. There are a lot of unneccessary lines in this model that have to do with my local settings and a general issue I found when I was playing around with tweets I recently scraped. 

The bin models used can be found on fasttexts website: ['Models'] (https://fasttext.cc/docs/en/pretrained-vectors.html)

The pictures are a rough sketch of what some of this would look like. One is picture of all of the english tweets. It has a lot of overlap so I need to fix it so things are clearer. The second picture is created by taking the average of each pois phrases (the average of the pois phrases 2-d representation) and plotting it. I eventually will have it set up so that when a query is posed the query will show up in a red dot on a graph and maybe some kind of labeling showing which POI it is closest to. I will do the exact same thing for topics as well so users can see what topics there queries relate to the best.

More to come. I just again have to work tonight. I was given a pseudo-raise/higher level position so my responsibility has kindve gone up significantly. If you have questions send me an email or message on slack. I will try to respond ASAP



Mitch
