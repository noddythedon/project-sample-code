import requests
import json
import csv
import sys
import ijson
import time
start_time = time.time()

reload(sys)
sys.setdefaultencoding("UTF-8")



base_api = "https://fantasy.premierleague.com/drf/element-summary/"
	
APIs = []
i=0
for i in xrange(1,650):
	APIs.append(base_api + str(i))


all_data = []


with open ('all_game_data_new.json', 'w') as fp:
	for i in xrange(1,650):
   		response = requests.get(base_api + str(i))
   		if response.status_code == 200:
   			player_data = response.json()
   			x={i:player_data}
			json.dump(x, fp, indent=2)
			print "dumped data for player id: {}".format(i)

print("--- %s seconds ---" % (time.time() - start_time))


