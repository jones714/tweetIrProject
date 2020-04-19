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


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
