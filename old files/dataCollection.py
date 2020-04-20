import json
from twpy import TwpyClient
from twpy.serializers import to_json, to_list


twitterData = []
with open('CVData.txt') as json_file:
    r = json.load(json_file)
    count = 0
    twtContent = []
    for tweet in r:
        twitterData.append(tweet)
        twtContent.append(tweet['content'])
        count += 1
    print(count)

    while(count < 200):
        tc = TwpyClient()

        Chinatweets = tc.search(query="china", since="2019-12-01", limit=100)
        Chinalist_tweets = to_list(Chinatweets)
        Chinajson_tweets = to_json(Chinatweets)

        for tweet in Chinajson_tweets:
            if tweet['content'] not in twtContent:
                twtContent.append(tweet['content'])
                twitterData.append(tweet)
                count+=1
        print(count)

    with open('CVData.txt', 'w') as outfile:
        json.dump(twitterData, outfile)
    print("GOT ALL THE TWEETS!")



#tc = TwpyClient()

#Chinatweets = tc.search(query="china", since="2019-12-01", limit=100)
#Chinalist_tweets = to_list(Chinatweets)
#hinajson_tweets = to_json(Chinatweets)


#data = []

#twtContent = []
#for tweet in Chinajson_tweets:
#    if tweet['content'] not in twtContent:
#        twtContent.append(tweet['content'])
#        data.append(tweet)


#with open('ChinaData.txt', 'w') as outfile:
#    json.dump(data, outfile)


