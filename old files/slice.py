import json
from twpy import TwpyClient
from twpy.serializers import to_json, to_list

finaldata = []
with open('WuhanData.txt') as json_file:
    r = json.load(json_file)
    count = 0

    for tweet in r:
        if count < 200:
            finaldata.append(tweet)
            count+=1
with open('FinalWuhanData.txt', 'w') as outfile:
    json.dump(finaldata, outfile)
print("GOT ALL THE TWEETS!")