from flask import Flask, request, render_template, Response, session, redirect, url_for
import json
from twpy import TwpyClient
from twpy.serializers import to_json, to_list
import re 
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob 
tc = TwpyClient()

app = Flask(__name__)

tweets = tc.search(query="china", since="2001-12-01", limit=10)
list_tweets = to_list(tweets)
json_tweets = to_json(tweets)

for tweet in json_tweets:
    print(tweet["content"])

def main(json_tweets):

    class TwitterClient(object): 
        ''' 
        Generic Twitter Class for sentiment analysis. 
        '''

    
        def clean_tweet(self, tweet): 
            ''' 
            Utility function to clean tweet text by removing links, special characters 
            using simple regex statements. 
            '''
            return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split()) 
    
        def get_tweet_sentiment(self, tweet): 
            ''' 
            Utility function to classify sentiment of passed tweet 
            using textblob's sentiment method 
            '''
            # create TextBlob object of passed tweet text 
            analysis = TextBlob(self.clean_tweet(tweet)) 
            # set sentiment 
            if analysis.sentiment.polarity > 0: 
                return 'Positive'
            elif analysis.sentiment.polarity == 0: 
                return 'Neutral'
            else: 
                return 'Negative'
    
        def get_tweets(self, twitter): 
            ''' 
            Main function to fetch tweets and parse them. 
            '''
            # empty list to store parsed tweets 
            tweets = [] 
    
            try: 

                # parsing tweets one by one 
                for tweet in twitter: 
                    # empty dictionary to store required params of a tweet 
                    parsed_tweet = {} 
    
                    # saving text of tweet 
                    parsed_tweet["text"] = tweet['content']
                    # saving sentiment of tweet 
                    parsed_tweet["sentiment"] = self.get_tweet_sentiment(tweet['content']) 
                    tweet["sentiment"] = parsed_tweet["sentiment"]
    
                    # appending parsed tweet to tweets list 
                    if int(tweet['retweet_count']) > 0: 
                        # if tweet has retweets, ensure that it is appended only once 
                        if parsed_tweet not in tweets: 
                            tweets.append(parsed_tweet) 
                    else: 
                        tweets.append(parsed_tweet) 
    
                # return parsed tweets 
                return tweets 
    
            except tweepy.TweepError as e: 
                # print error (if any) 
                print("Error : " + str(e))


    # creating object of TwitterClient Class 
    api = TwitterClient() 
    # calling function to get tweets 
    tweets = api.get_tweets(twitter=json_tweets) 

    # picking positive tweets from tweets 
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'Positive'] 
    # percentage of positive tweets 
    print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets))) 
    # picking negative tweets from tweets 
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'Negative'] 
    # percentage of negative tweets 
    print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets))) 
    # percentage of neutral tweets
    
    count = 0
    for twt in tweets:
        if twt not in ntweets and twt not in ptweets:
            count+= 1

    print("Neutral tweets percentage: {} % \ ".format(100*(count/len(tweets)))) 
  
    # printing positive
    print("\n\nPositive tweets:") 
    for tweet in ptweets: 
        print(tweet['text']) 
  
    # printing negative 
    print("\n\nNegative tweets:") 
    for tweet in ntweets: 
        print(tweet['text'])


    ## ********* Note *********************************************************
    ## To access the sentimental value of tweet from JSON file, USE:
    #    for tweet in json_tweets:
    #        if tweet["sentiment"] == 'negative':
    #           print(tweet["content"])
    # This will give you the negative tweets


    return json_tweets


data = main(json_tweets)


@app.route('/')
@app.route('/main')
def main():
    return render_template('main.html')

#Dictonary that stores the {tweet:rating} from the sentiment analysis
jsontest = {}

#This is a test dictonary if the sentiment returns a dictonary.
testlist = {'Erik is a really good programmer, lol just kidding':'Positive','Carl is really good at video games':'Positive','Bob really sucks at programing':'Negative','This is a neutral tweet, be yellow please': 'Neutral',
'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD' : 'Positive'}

#This gets a .json from post and returns the data to jsontest that is then used in /tweets
@app.route("/info", methods = ['GET', 'POST'])
def index():
    #value = request.json
    req_data = request.get_json()
    the_tweets = list(req_data['Tweets'])
    while len(the_tweets) != 0:
        getpair = the_tweets.pop()
        tweet = getpair.get('tweet')
        rating = getpair.get('rating')
        jsontest.update({tweet:rating})
    print(jsontest)
    return jsontest

@app.route("/tweets")
def Tweets():
    return render_template("index.html",othertest = testlist, bigwholetest = jsontest)

@app.route('/graphs')
def graphs():
    testData = {}
    for twt in data:
        print(twt['sentiment'])
        testData[twt['content']] = twt['sentiment']

    listofvalues = list(testlist.values())
    Tlistofvalues = list(testData.values())
    print(Tlistofvalues)
    return render_template('graphpage.html', keys = Tlistofvalues)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=False)
