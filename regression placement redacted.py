from __future__ import division
import requests
import json
import csv
import sys
import ijson
import time
import collections
start_time = time.time()

reload(sys)
sys.setdefaultencoding("UTF-8")


# Call the bootstrap file
with open('bootstrap_good.json') as f:
	bootstrap_data = json.load(f)

first_name = []
second_name = []
player_id = []
team_id = []
total_points = []
position = []
averagescore = []
averagetotal = 0

#Extract specific lists of data for each of the 647 players
for i in xrange(647):
	first_name.append(bootstrap_data['elements'][i]['first_name'])
	second_name.append(bootstrap_data['elements'][i]['second_name'])
	player_id.append(bootstrap_data['elements'][i]['id'])
	team_id.append(bootstrap_data['elements'][i]['team'])
	total_points.append(bootstrap_data['elements'][i]['total_points'])
	position.append(bootstrap_data['elements'][i]['element_type'])

for i in range(38):
	averagescore.append(bootstrap_data['events'][i]['average_entry_score'])
	averagetotal+= bootstrap_data['events'][i]['average_entry_score']

#Create tuples from the data
bootstrap_rows = zip(first_name, second_name, player_id,team_id, position, total_points)


goalkeepers, defenders, midfielders, forwards = [], [], [], []

#To see which are the top scorers for each position we first split the players up by position
for row in bootstrap_rows:
	if row[4] == 1:
		goalkeepers.append((row[2], row[5], row[0].encode('utf-8'), row[1].encode('utf-8'),row[4], row[3]))
	if row[4] == 2:
		defenders.append((row[2], row[5], row[0].encode('utf-8'), row[1].encode('utf-8'), row[4], row[3]))
	if row[4] == 3:
		midfielders.append((row[2], row[5], row[0].encode('utf-8'), row[1].encode('utf-8'), row[4], row[3]))
	if row[4] == 4:
		forwards.append((row[2], row[5], row[0].encode('utf-8'), row[1].encode('utf-8'), row[4], row[3]))


#sorting the positions by most points obtained over the year, descending order
goalkeepers.sort(key = lambda tup: tup[1], reverse = True)
defenders.sort(key = lambda tup: tup[1], reverse = True)
midfielders.sort(key = lambda tup: tup[1], reverse = True)
forwards.sort(key = lambda tup: tup[1], reverse = True)

#create seperate lists for the top 20 scorers in each position
topgks = goalkeepers[:20]
topdefs = defenders[:20]
topmids = midfielders[:20]
topfwds = forwards[:20]
topattackers = topfwds + topmids

gk_search_ids = []
def_search_ids = []
fwdmid_search_ids = []

#Open and save the large player data file
with open('player_data.json') as f:
    players_data = json.load(f)


#create tuples of the ids of the top players from which to base our model 
for i in range(len(topgks)):
	gk_search_ids.append((topgks[i][0], topgks[i][2], topgks[i][3], topgks[i][4], topgks[i][5]))

for i in range(len(topdefs)):
	def_search_ids.append((topdefs[i][0], topdefs[i][2], topdefs[i][3], topdefs[i][4], topdefs[i][5]))

for i in range(len(topattackers)):
	fwdmid_search_ids.append((topattackers[i][0], topattackers[i][2], topattackers[i][3], topattackers[i][4], topattackers[i][5]))


# What follows are a series of functions designed to save a majority of the repetition when calling/weighting the data
def AvePtsLastThree(week):
	points_totals_so_far = []
	if week < 3:
		for w in range(week):
			points_totals_so_far.append(data['history'][w]['total_points'])
			avepts = float(sum(points_totals_so_far))/len(points_totals_so_far)
	if week >= 3:
		for w in range(week-3,week):
			points_totals_so_far.append(data['history'][w]['total_points'])
			avepts = float(sum(points_totals_so_far))/len(points_totals_so_far)
	return avepts


def AveBPSLastThree(week):
	BPS_totals_so_far = []
	if week < 3:
		for w in range(week):
			BPS_totals_so_far.append(data['history'][w]['bps'])
			aveBPS = float(sum(BPS_totals_so_far))/len(BPS_totals_so_far)
	if week >= 3:
		for w in range(week-3,week):
			BPS_totals_so_far.append(data['history'][w]['bps'])
			aveBPS = float(sum(BPS_totals_so_far))/len(BPS_totals_so_far)
	return aveBPS


def AveThreatLastThree(week):
	Threat_totals_so_far = []
	if week < 3:
		for w in range(week):
			Threat_totals_so_far.append(float(data['history'][w]['threat']))
			aveThreat = float(sum(Threat_totals_so_far))/len(Threat_totals_so_far)
	if week >= 3:
		for w in range(week-3,week):
			Threat_totals_so_far.append(float(data['history'][w]['threat']))
			aveThreat = float(sum(Threat_totals_so_far))/len(Threat_totals_so_far)
	return aveThreat

def AveCreativLastThree(week):
	Creativity_totals_so_far = []
	if week < 3:
		for w in range(week):
			Creativity_totals_so_far.append(float(data['history'][w]['creativity']))
			aveCreativity = float(sum(Creativity_totals_so_far))/len(Creativity_totals_so_far)
	if week >= 3:
		for w in range(week-3,week):
			Creativity_totals_so_far.append(float(data['history'][w]['creativity']))
			aveCreativity = float(sum(Creativity_totals_so_far))/len(Creativity_totals_so_far)
	return aveCreativity

def BigChancesLastTen(week):
	big_chances_last_ten = []
	if week < 10:
		for w in range(week):
			big_chances_last_ten.append((data['history'][w]['big_chances_created'])+(data['history'][w]['big_chances_missed']))
			chances = sum(big_chances_last_ten)
	if week >= 10:
		for w in range(week-10,week):
			big_chances_last_ten.append((data['history'][w]['big_chances_created'])+(data['history'][w]['big_chances_missed']))
			chances = sum(big_chances_last_ten)
	return chances


def CleanSheetsLastFift(week):
	clean_sheets_last_ten = []
	if week < 15:
		for w in range(week):
			clean_sheets_last_ten.append((data['history'][w]['clean_sheets']))
			sheets = sum(clean_sheets_last_ten)
	if week >= 15:
		for w in range(week-15,week):
			clean_sheets_last_ten.append((data['history'][w]['clean_sheets']))
			sheets = sum(clean_sheets_last_ten)
	return sheets

#creating lists to store specific data
gk_ave_BPS = []
gk_ave_points = []
gk_model_prediction = []
gk_id = []
gk_name = []
gk_games_played = []
gk_total_points_following_week = []
gk_position = []
gk_team_id = []

def_weighted_pts = []
def_weighted_bps = []
def_weighted_threat = []
def_total_points_following_week = []
def_clean_sheets = []
def_id = []
def_name = []
def_position = []
def_games_played = []
def_model_prediction = []
def_team_id = []


fwdmid_id = []
fwdmid_name = []
fwdmid_weighted_pts = []
fwdmid_weighted_bps = []
fwdmid_weighted_threat = []
fwdmid_weighted_creativity = []
fwdmid_total_points_following_week = []
fwdmid_weighted_chances = []
fwdmid_model_prediction = []
fwdmid_games_played = []
fwdmid_position = []
fwdmid_team_id = []

#split the 20 teams into 5 groups, with the top 4 teams being in team_group_1 etc.
team_group_1 = [11, 12, 17, 10]
team_group_2 = [5, 1, 4, 7]
team_group_3 = [9, 13, 6, 2]
team_group_4 = [20, 18, 3, 8]
team_group_5 = [14, 16, 15, 19]

### GOALKEEPER DATA
for player in gk_search_ids:
	data = players_data[str(player[0])]
	for i in range(1, len(data['history'])):
		gk_id.append(player[0])
		gk_name.append(player[1]+player[2])
		gk_games_played.append(i)
		gk_ave_points.append(AvePtsLastThree(i))
		gk_ave_BPS.append(AveBPSLastThree(i))
		gk_position.append(1)
		gk_team_id.append(player[4])
		gk_model_prediction.append(1.1809 + (AveBPSLastThree(i)*0.2056) - (AvePtsLastThree(i)*0.3889))
		gk_total_points_following_week.append(data['history'][i]['total_points'])

### DEFENDER DATA
for player in def_search_ids:
	data = players_data[str(player[0])]
	for i in range(1, len(data['history'])):
		if data['history'][i]['was_home']:
			if data['history'][i]['opponent_team'] in team_group_1:
				def_weighted_pts.append(AvePtsLastThree(i)*1.5*0.5)
				def_weighted_bps.append(AveBPSLastThree(i)*1.5*0.5)
				def_weighted_threat.append(AveThreatLastThree(i)*1.5*0.5)
			if data['history'][i]['opponent_team'] in team_group_2:
				def_weighted_pts.append(AvePtsLastThree(i)*1.5*0.85)
				def_weighted_bps.append(AveBPSLastThree(i)*1.5*0.85)
				def_weighted_threat.append(AveThreatLastThree(i)*1.5*0.85)
			if data['history'][i]['opponent_team'] in team_group_3:
				def_weighted_pts.append(AvePtsLastThree(i)*1.5)
				def_weighted_bps.append(AveBPSLastThree(i)*1.5)
				def_weighted_threat.append(AveThreatLastThree(i)*1.5)
			if data['history'][i]['opponent_team'] in team_group_4:
				def_weighted_pts.append(AvePtsLastThree(i)*1.5*1.15)
				def_weighted_bps.append(AveBPSLastThree(i)*1.5*1.15)
				def_weighted_threat.append(AveThreatLastThree(i)*1.5*1.15)
			if data['history'][i]['opponent_team'] in team_group_5:
				def_weighted_pts.append(AvePtsLastThree(i)*1.5*1.3)
				def_weighted_bps.append(AveBPSLastThree(i)*1.5*1.3)
				def_weighted_threat.append(AveThreatLastThree(i)*1.5*1.3)
		else:
			if data['history'][i]['opponent_team'] in team_group_1:
				def_weighted_pts.append(AvePtsLastThree(i)*0.5*0.5)
				def_weighted_bps.append(AveBPSLastThree(i)*0.5*0.5)
				def_weighted_threat.append(AveThreatLastThree(i)*0.5*0.5)
			if data['history'][i]['opponent_team'] in team_group_2:
				def_weighted_pts.append(AvePtsLastThree(i)*0.5*0.85)
				def_weighted_bps.append(AveBPSLastThree(i)*0.5*0.85)
				def_weighted_threat.append(AveThreatLastThree(i)*0.5*0.85)
			if data['history'][i]['opponent_team'] in team_group_3:
				def_weighted_pts.append(AvePtsLastThree(i)*0.5)
				def_weighted_bps.append(AveBPSLastThree(i)*0.5)
				def_weighted_threat.append(AveThreatLastThree(i)*0.5)
			if data['history'][i]['opponent_team'] in team_group_4:
				def_weighted_pts.append(AvePtsLastThree(i)*0.5*1.15)
				def_weighted_bps.append(AveBPSLastThree(i)*0.5*1.15)
				def_weighted_threat.append(AveThreatLastThree(i)*0.5*1.15)
			if data['history'][i]['opponent_team'] in team_group_5:
				def_weighted_pts.append(AvePtsLastThree(i)*0.5*1.3)
				def_weighted_bps.append(AveBPSLastThree(i)*0.5*1.3)
				def_weighted_threat.append(AveThreatLastThree(i)*0.5*1.3)
		def_games_played.append(i)
		def_position.append(2)
		def_id.append(player[0])
		def_team_id.append(player[4])
		def_name.append(player[1]+player[2])
		def_clean_sheets.append(CleanSheetsLastFift(i))
		def_total_points_following_week.append(data['history'][i]['total_points'])

###FORWARD AND MIDFIELDER DATA
for player in fwdmid_search_ids:
	data = players_data[str(player[0])]
	for i in range(1, len(data['history'])):
		if data['history'][i]['was_home']:
			if data['history'][i]['opponent_team'] in team_group_1:
				fwdmid_weighted_pts.append(AvePtsLastThree(i)*1.2*0.7)
				fwdmid_weighted_bps.append(AveBPSLastThree(i)*1.2*0.7)
				fwdmid_weighted_threat.append(AveThreatLastThree(i)*1.2*0.7)
				fwdmid_weighted_creativity.append(AveCreativLastThree(i)*1.2*0.7)
				fwdmid_weighted_chances.append(BigChancesLastTen(i)*1.2*0.7)
			if data['history'][i]['opponent_team'] in team_group_2:
				fwdmid_weighted_pts.append(AvePtsLastThree(i)*1.2*0.85)
				fwdmid_weighted_bps.append(AveBPSLastThree(i)*1.2*0.85)
				fwdmid_weighted_threat.append(AveThreatLastThree(i)*1.2*0.85)
				fwdmid_weighted_creativity.append(AveCreativLastThree(i)*1.2*0.85)
				fwdmid_weighted_chances.append(BigChancesLastTen(i)*1.2*0.85)
			if data['history'][i]['opponent_team'] in team_group_3:
				fwdmid_weighted_pts.append(AvePtsLastThree(i)*1.2)
				fwdmid_weighted_bps.append(AveBPSLastThree(i)*1.2)
				fwdmid_weighted_threat.append(AveThreatLastThree(i)*1.2)
				fwdmid_weighted_creativity.append(AveCreativLastThree(i)*1.2)
				fwdmid_weighted_chances.append(BigChancesLastTen(i)*1.2)
			if data['history'][i]['opponent_team'] in team_group_4:
				fwdmid_weighted_pts.append(AvePtsLastThree(i)*1.2*1.15)
				fwdmid_weighted_bps.append(AveBPSLastThree(i)*1.2*1.15)
				fwdmid_weighted_threat.append(AveThreatLastThree(i)*1.2*1.15)
				fwdmid_weighted_creativity.append(AveCreativLastThree(i)*1.2*1.15)
				fwdmid_weighted_chances.append(BigChancesLastTen(i)*1.2*1.15)
			if data['history'][i]['opponent_team'] in team_group_5:
				fwdmid_weighted_pts.append(AvePtsLastThree(i)*1.2*1.3)
				fwdmid_weighted_bps.append(AveBPSLastThree(i)*1.2*1.3)
				fwdmid_weighted_threat.append(AveThreatLastThree(i)*1.2*1.3)
				fwdmid_weighted_creativity.append(AveCreativLastThree(i)*1.2*1.3)
				fwdmid_weighted_chances.append(BigChancesLastTen(i)*1.2*1.3)
		else:
			if data['history'][i]['opponent_team'] in team_group_1:
				fwdmid_weighted_pts.append(AvePtsLastThree(i)*0.8*0.7)
				fwdmid_weighted_bps.append(AveBPSLastThree(i)*0.8*0.7)
				fwdmid_weighted_threat.append(AveThreatLastThree(i)*0.8*0.7)
				fwdmid_weighted_creativity.append(AveCreativLastThree(i)*0.8*0.7)
				fwdmid_weighted_chances.append(BigChancesLastTen(i)*0.8*0.7)
			if data['history'][i]['opponent_team'] in team_group_2:
				fwdmid_weighted_pts.append(AvePtsLastThree(i)*0.8*0.85)
				fwdmid_weighted_bps.append(AveBPSLastThree(i)*0.8*0.85)
				fwdmid_weighted_threat.append(AveThreatLastThree(i)*0.8*0.85)
				fwdmid_weighted_creativity.append(AveCreativLastThree(i)*0.8*0.85)
				fwdmid_weighted_chances.append(BigChancesLastTen(i)*0.8*0.85)
			if data['history'][i]['opponent_team'] in team_group_3:
				fwdmid_weighted_pts.append(AvePtsLastThree(i)*0.8)
				fwdmid_weighted_bps.append(AveBPSLastThree(i)*0.8)
				fwdmid_weighted_threat.append(AveThreatLastThree(i)*0.8)
				fwdmid_weighted_creativity.append(AveCreativLastThree(i)*0.8)
				fwdmid_weighted_chances.append(BigChancesLastTen(i)*0.8)
			if data['history'][i]['opponent_team'] in team_group_4:
				fwdmid_weighted_pts.append(AvePtsLastThree(i)*0.8*1.15)
				fwdmid_weighted_bps.append(AveBPSLastThree(i)*0.8*1.15)
				fwdmid_weighted_threat.append(AveThreatLastThree(i)*0.8*1.15)
				fwdmid_weighted_creativity.append(AveCreativLastThree(i)*0.8*1.15)
				fwdmid_weighted_chances.append(BigChancesLastTen(i)*0.8*1.15)
			if data['history'][i]['opponent_team'] in team_group_5:
				fwdmid_weighted_pts.append(AvePtsLastThree(i)*0.8*1.3)
				fwdmid_weighted_bps.append(AveBPSLastThree(i)*0.8*1.3)
				fwdmid_weighted_threat.append(AveThreatLastThree(i)*0.8*1.3)
				fwdmid_weighted_creativity.append(AveCreativLastThree(i)*0.8*1.3)
				fwdmid_weighted_chances.append(BigChancesLastTen(i)*0.8*1.3)
		fwdmid_games_played.append(i)
		fwdmid_id.append(player[0])
		fwdmid_team_id.append(player[4])
		fwdmid_name.append(player[1]+player[2])
		fwdmid_position.append(player[3])
		fwdmid_total_points_following_week.append(data['history'][i]['total_points'])




pre_def_tuples = zip(def_weighted_pts, def_weighted_bps, def_weighted_threat, def_clean_sheets, def_total_points_following_week)

pre_fwdmid_full_tuples = zip(fwdmid_id, fwdmid_name, fwdmid_weighted_pts, fwdmid_weighted_bps, fwdmid_weighted_threat, fwdmid_weighted_creativity, fwdmid_weighted_chances, fwdmid_total_points_following_week)

#Assign predictions based on linear regression output of R statistical analysis software

'''

REDACTED

'''

gk_tuples = zip(gk_id, gk_name, gk_team_id, gk_games_played, gk_position, gk_model_prediction, gk_total_points_following_week)
def_tuples = zip(def_id, def_name, def_team_id, def_games_played, def_position, def_model_prediction, def_total_points_following_week)
fwdmid_tuples = zip(fwdmid_id, fwdmid_name, fwdmid_team_id, fwdmid_games_played, fwdmid_position,fwdmid_model_prediction, fwdmid_total_points_following_week)

predictions_data = gk_tuples+def_tuples+fwdmid_tuples

initial_team = []
def getFifth(item):
    return item[5]

# Calculating initial team as a test
initial_team.append(max((p for p in predictions_data if p[3] == 1 and p[4] ==1), key=getFifth))
initial_team.append(tuple(sorted((p for p in predictions_data if p[3] == 1 and p[4] ==2), key=getFifth, reverse=True)[:3]))
initial_team.append(tuple(sorted((p for p in predictions_data if p[3] == 1 and p[4] ==3), key=getFifth, reverse=True)[:4]))
initial_team.append(tuple(sorted((p for p in predictions_data if p[3] == 1 and p[4] ==4), key=getFifth, reverse=True)[:3]))



#initial_team = [z for y in (x if isinstance(x[0],tuple) else [x] for x in initial_team) for z in y]

def flatten(tup):
    for t in tup:
        if isinstance(t, tuple) and any(isinstance(sub, tuple) for sub in t):
            for sub in flatten(t):
                yield sub
        else:
            yield t

initial_team =  list(flatten(initial_team))


print "Predicted Points in round 2: {}".format(sum(i[5] for i in initial_team))
print "Actual Points in round 2: {}".format(sum(i[6] for i in initial_team))


# Creating a dictionary with each team chosen by the models predictions, stored under key: 'team_1' for the team chosen AFTER the first week. 
# Chosen playing formations can be changed by changing the numbers on the right hand side of lines 408,409,410. eg. 3-5-2
# Iterate through tuples where p[3] = games played and p[4] = position, and 
# getFifth returns p[5] = predicted score, which we sort by reverse and grab the top 1,2,3,4,5 elements depending on playing formation being tested
best_team_dict = {}
for i in range(1,38):
	team_for_week = []
	team_for_week.append(max((p for p in predictions_data if p[3] == i and p[4] ==1), key=getFifth))
	team_for_week.append(tuple(sorted((p for p in predictions_data if p[3] == i and p[4] ==2), key=getFifth, reverse=True)[:3]))
	team_for_week.append(tuple(sorted((p for p in predictions_data if p[3] == i and p[4] ==3), key=getFifth, reverse=True)[:5]))
	team_for_week.append(tuple(sorted((p for p in predictions_data if p[3] == i and p[4] ==4), key=getFifth, reverse=True)[:2]))
		
	flattened_team_for_week = list(flatten(team_for_week))
	best_team_dict['team_%s' % i] = flattened_team_for_week



# Calculate the total predicted score and total 'Actual' score achieved by the model

totalprediction = 0
totalptswon = 0
predscore, actscore, week = [], [], []
for i in range(1,38):
	captain = max(best_team_dict['team_'+str(i)],key=getFifth)
	totalprediction += ((sum(p[5] for p in best_team_dict['team_'+str(i)]))+captain[5])
	totalptswon += ((sum(p[6] for p in best_team_dict['team_'+str(i)]))+captain[6])
	predscore.append((sum(p[5] for p in best_team_dict['team_'+str(i)]))+captain[5])
	actscore.append((sum(p[6] for p in best_team_dict['team_'+str(i)]))+captain[6])
	week.append(i+1)

score_tups = zip(week, averagescore, predscore, actscore)
headers = ("Round", "Average", "Predicted", "Actual")


#Print results, with formation. Multiplied by 38/37 to simulate the missing first weeks score based on the models average score.

print "predic points over season 3-5-2	: 	{}".format(totalprediction*38.0/37.0)
print "actual points over season 	    : 	{}".format(totalptswon*38.0/37.0)




'''
#Save to csv file
with open('model_pred.csv', 'wb') as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    for row in score_tups:
        writer.writerow(row)
'''


print("--- %s seconds ---" % (time.time() - start_time))