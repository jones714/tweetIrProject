from flask import Flask
from twpy import TwpyClient
from twpy.serializers import to_json, to_list
tc = TwpyClient()

app = Flask(__name__)

tweets = tc.search(query="china", since="2001-12-01", limit=10)
list_tweets = to_list(tweets)


@app.route('/home')
def api_home():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
