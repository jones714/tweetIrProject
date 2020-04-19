from flask import Flask, request, render_template, Response, session, redirect, url_for
import json
from twpy import TwpyClient
from twpy.serializers import to_json, to_list
tc = TwpyClient()

app = Flask(__name__)

tweets = tc.search(query="china", since="2001-12-01", limit=10)
list_tweets = to_list(tweets)
json_tweets = to_json(tweets)

for tweet in json_tweets:
    print(tweet["content"])


@app.route('/')
@app.route('/main')
def main():
    return render_template('main.html')

#Dictonary that stores the {tweet:rating} from the sentiment analysis
jsontest = {}

#This is a test dictonary if the sentiment returns a dictonary.
testlist = {'Erik is a really good programmer, lol just kidding':'Positive','Carl is really good at video games':'Positive','Bob really sucks at programing':'Negative','This is a neutral tweet, be yellow please': 'Neutral',
'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD' : 'Positive', 'This is a test': 'Neutral'}

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
    listofvalues = list(testlist.values())
    return render_template('graphpage.html', keys = listofvalues)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
