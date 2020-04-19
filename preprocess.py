import json
import nltk
import re
from nltk.tokenize import TweetTokenizer
from nltk.stem import PorterStemmer
from collections import Counter

tknzr = TweetTokenizer()
ps = PorterStemmer()
stop_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]

keywords = ['china', 'wuhan', 'covid', 'coronavirus', 'sarscov']
repository = 'processedData.json'


tweetIds = []


def preprocessData(tweetData):
	content = {}
	vocab = Counter()
	likes = {}
	retweets = {}
	#open tweetData
	with open(tweetData) as json_file:
		data = json.load(json_file)
		for date, xVal in data['features'].items():
			#Date
			content[date] = {}
			for features in xVal:
				#tweet
				content[date][features['tweet_id']] = Counter()
				tweetTokens_preStem = tknzr.tokenize(features['content'])

				for preStem in tweetTokens_preStem:
					stemmed = ps.stem(preStem)
					# if not stop word
					if stemmed not in stop_words:
						# if not twitter handle or URL
						if not (re.findall("^@", stemmed) or re.findall("^http|.com+", stemmed)):
							if features['tweet_id'] not in tweetIds:
								content[date][features['tweet_id']].update([stemmed])
								tweetIds.append(features['tweet_id'])
					vocab.update(content[date][features['tweet_id']])
				likes[features['tweet_id']] = features['likes_count']
				retweets[features['tweet_id']] = features['retweet_count']

			#for yKey, yVal in xVal.items():
			#	print("{} {}".format(yKey, yVal))
	#print(outData)
	return content, likes, retweets, vocab


data = {}
for keyword in keywords:
	print("Processing {}".format(keyword))
	data[keyword] = {}
	data[keyword]['content'], data[keyword]['likes'], data[keyword]['retweets'], data[keyword]['vocab'] = preprocessData(repository)
