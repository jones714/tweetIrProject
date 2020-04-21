from flask import Flask, request, render_template, Response, session, redirect, url_for
import json
from twpy import TwpyClient
from twpy.serializers import to_json, to_list
import re 
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob 

import nltk
nltk.download('punkt')
nltk.download('words')
SENT_DETECTOR = nltk.data.load('tokenizers/punkt/english.pickle')
from nltk.tokenize import word_tokenize
from textblob.classifiers import NaiveBayesClassifier

tc = TwpyClient()

app = Flask(__name__)


train = [
('I love China!', 'pos'),
('China is helping people', 'pos'),
('I feel very good about Wuhan', 'pos'),
('This Corona pandemic is looking up', 'pos'),
("Don't blame China", 'pos'),
('I do not like China', 'neg'),
('I am tired of this pandemic', 'neg'),
("who's to blame, oh wait its china", 'neg'),
('Corona virus was created in china', 'neg'),
('Wuhan is responsible', 'neg')
]

ChinaAccuracy = {
    "TP": 0,
    "TN": 0,
    "FP": 0,
    "FN": 0
}

WuhanAccuracy = {
    "TP": 0,
    "TN": 0,
    "FP": 0,
    "FN": 0
}

CVAccuracy = {
    "TP": 0,
    "TN": 0,
    "FP": 0,
    "FN": 0
}


cl = NaiveBayesClassifier(train)

Chinajson_tweetsC = []
with open('FinalChinaDataClean.txt') as json_file:
    Chinajson_tweetsC = json.load(json_file)

Chinajson_tweets = []
with open('FinalChinaData.txt') as json_file:
    Chinajson_tweets = json.load(json_file)

Wuhanjson_tweets = []
with open('FinalWuhanData.txt') as json_file:
    Wuhanjson_tweets = json.load(json_file)

Wuhanjson_tweetsC = []
with open('FinalWuhanDataClean.txt') as json_file:
    Wuhanjson_tweetsC = json.load(json_file)

CVjson_tweets = []
with open('FinalCVData.txt') as json_file:
    CVjson_tweets = json.load(json_file)

CVjson_tweetsC = []
with open('FinalCVDataClean.txt') as json_file:
    CVjson_tweetsC = json.load(json_file)

#for tweet in json_tweets:
#    print(tweet["content"])
words = set(nltk.corpus.words.words())
def main(json_tweets, ctrl, acc):

    class TwitterClient(object): 
        ''' 
        Generic Twitter Class for sentiment analysis. 
        '''

    
        def clean_tweet(self, tweet): 
            ''' 
            Utility function to clean tweet text by removing links, special characters 
            using simple regex statements. 
            '''
            #remove all links
            link = ' '.join(re.sub(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', " ", tweet).split())
            
            #remove non english words based on corpus
            eng = " ".join(w for w in nltk.wordpunct_tokenize(link) if w.lower() in words or not w.isalpha()) 

            #remove special characters
            return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", eng).split())

        def strip_tweet(self, tweet): 
            ''' 
            Utility function to clean tweet text by removing links, special characters 
            using simple regex statements. 
            '''
            stop_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]

            tweet_without_sc = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
            tweet_tokens = word_tokenize(tweet_without_sc)
            tweets_without_sw = [word for word in tweet_tokens if not word in stop_words]

            return ''.join(tweets_without_sw)
    
        def get_tweet_sentiment(self, tweet): 
            ''' 
            Utility function to classify sentiment of passed tweet 
            using textblob's sentiment method 
            '''
            # create TextBlob object of passed tweet text 
            analysis = TextBlob(self.clean_tweet(tweet))

            # set sentiment 
            if analysis.sentiment.polarity > .4: 
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

                    #Gets sentiment based on test
                    testSentiment = cl.classify(tweet['content'])

                    # empty dictionary to store required params of a tweet 
                    parsed_tweet = {} 
                    
                    if ctrl == 1:
                        tweet['content'] = self.clean_tweet(tweet['content'])

                    # saving text of tweet 
                    parsed_tweet["text"] = tweet['content']
                    # saving sentiment of tweet 
                    parsed_tweet["sentiment"] = self.get_tweet_sentiment(tweet['content']) 
                    tweet["sentiment"] = parsed_tweet["sentiment"]

                    if acc != 0:
                        #Update Accuracy
                        if testSentiment == 'pos' and tweet["sentiment"] == "Positive":
                            acc["TP"] +=1
                        if testSentiment == 'pos' and tweet["sentiment"] == "Negative":
                            acc["FP"] +=1
                        if testSentiment == 'neg' and tweet["sentiment"] == "Positive":
                            acc["FN"] +=1
                        if testSentiment == 'neg' and tweet["sentiment"] == "Negative":
                            acc["TN"] +=1    

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
    #print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets))) 
    # picking negative tweets from tweets 
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'Negative'] 
    # percentage of negative tweets 
    #print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets))) 
    # percentage of neutral tweets
    
    count = 0
    for twt in tweets:
        if twt not in ntweets and twt not in ptweets:
            count+= 1

    #print("Neutral tweets percentage: {} % \ ".format(100*(count/len(tweets)))) 
  
    # printing positive
    #print("\n\nPositive tweets:") 
    #for tweet in ptweets: 
    #    print(tweet['text']) 
  
    # printing negative 
    #print("\n\nNegative tweets:") 
    #for tweet in ntweets: 
    #    print(tweet['text'])


    ## ********* Note *********************************************************
    ## To access the sentimental value of tweet from JSON file, USE:
    #    for tweet in json_tweets:
    #        if tweet["sentiment"] == 'negative':
    #           print(tweet["content"])
    # This will give you the negative tweets


    return json_tweets


ChinaData = main(Chinajson_tweets, 0, ChinaAccuracy)
WuhanData = main(Wuhanjson_tweets, 0, WuhanAccuracy)
CVData = main(CVjson_tweets, 0, CVAccuracy)

ChinaDataClean = main(Chinajson_tweetsC, 1, 0)
WuhanDataClean = main(Wuhanjson_tweetsC, 1, 0)
CVDataClean = main(CVjson_tweetsC, 1, 0)


#print(WuhanAccuracy["TP"])

@app.route('/')
@app.route('/main')
def main():
    return render_template('main.html')

#Dictonary that stores the {tweet:rating} from the sentiment analysis
#jsontest = {}

#This is a test dictonary if the sentiment returns a dictonary.
testlist = {'Erik is a really good programmer, lol just kidding':'Positive','Carl is really good at video games':'Positive','Bob really sucks at programing':'Negative','This is a neutral tweet, be yellow please': 'Neutral',
'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD' : 'Positive'}

#This gets a .json from post and returns the data to jsontest that is then used in /tweets (Couldnt figure out how to use this so just commented it out)
#@app.route("/info", methods = ['GET', 'POST'])
#def index():
#    #value = request.json
#    req_data = request.get_json()
#    the_tweets = list(req_data['Tweets'])
#    while len(the_tweets) != 0:
#        getpair = the_tweets.pop()
#        tweet = getpair.get('tweet')
#        rating = getpair.get('rating')
#        jsontest.update({tweet:rating})
#    print(jsontest)
#    return jsontest

@app.route("/tweetsChina")
def TweetChina():
    tweets_list  = {}
    for twt in ChinaData:
        tweets_list.update({twt['content']:twt['sentiment']})
    return render_template("ChinaIndex.html", bigwholetest = tweets_list)

@app.route("/tweetsWuhan")
def TweetWuhan():
    tweets_list  = {}
    for twt in WuhanData:
        tweets_list.update({twt['content']:twt['sentiment']})
    return render_template("WuhanIndex.html", bigwholetest = tweets_list)

@app.route("/tweetsCV")
def TweetCV():
    tweets_list  = {}
    for twt in CVData:
        tweets_list.update({twt['content']:twt['sentiment']})
    return render_template("CVIndex.html", bigwholetest = tweets_list)

@app.route("/tweetsChinaClean")
def TweetChinaC():
    tweets_list  = {}
    for twt in ChinaDataClean:
        tweets_list.update({twt['content']:twt['sentiment']})
    return render_template("ChinaIndexClean.html", bigwholetest = tweets_list)

@app.route("/tweetsWuhanClean")
def TweetWuhanC():
    tweets_list  = {}
    for twt in WuhanDataClean:
        tweets_list.update({twt['content']:twt['sentiment']})
    return render_template("WuhanIndexClean.html", bigwholetest = tweets_list)

@app.route("/tweetsCVClean")
def TweetCVC():
    tweets_list  = {}
    for twt in CVDataClean:
        tweets_list.update({twt['content']:twt['sentiment']})
    return render_template("CVIndexClean.html", bigwholetest = tweets_list)

@app.route('/graphsChina')
def graphChina():
    testData = {}
    for twt in ChinaData:
        #print(twt['sentiment'])
        testData[twt['content']] = twt['sentiment']

    listofvalues = list(testlist.values())
    Tlistofvalues = list(testData.values())
    #print(Tlistofvalues)
    return render_template('graphpageChina.html', keys = Tlistofvalues)

@app.route('/graphsWuhan')
def graphWuhan():
    testData = {}
    for twt in WuhanData:
        #print(twt['sentiment'])
        testData[twt['content']] = twt['sentiment']

    listofvalues = list(testlist.values())
    Tlistofvalues = list(testData.values())
    #print(Tlistofvalues)
    return render_template('graphpageWuhan.html', keys = Tlistofvalues)

@app.route('/graphsCV')
def graphCV():
    testData = {}
    for twt in CVData:
        #print(twt['sentiment'])
        testData[twt['content']] = twt['sentiment']

    listofvalues = list(testlist.values())
    Tlistofvalues = list(testData.values())
    #print(Tlistofvalues)
    return render_template('graphpageCV.html', keys = Tlistofvalues)

@app.route('/discussion')
def result():
    return render_template("discussion.html")


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=False)