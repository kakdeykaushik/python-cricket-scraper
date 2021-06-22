import requests
import pandas as pd
import numpy as np


class CricInfo:

	def __init__(self, match_id):

		self.match_id = match_id

		self.series_json_url = "https://www.espncricinfo.com/matches/engine/match/{0}.json".format(match_id)

		self.series_id = self._get_series_id()

		self.json_url = "https://hs-consumer-api.espncricinfo.com/v1/pages/match/details?lang=en&seriesId={0}&matchId={1}".format(self.series_id, self.match_id)

		self.json = self._get_json()


	def _get_series_id(self):
		'''Returns series ID.'''

		page = requests.get(self.series_json_url)
		json = page.json()

		return json["series"][0]["object_id"]
		

	def _get_json(self):
		'''Returns JSON.'''

		page = requests.get(self.json_url)
		return page.json()

	def match_name(self):
		'''Returns match name.'''
		
		txt = self.json['match']['slug']
		txt = ' '.join(txt.split('-'))
		return txt.title()


	def result_text(self):
		'''Returns match result.'''

		return self.json['match']['statusText']

	def series_name(self):
		'''Returns series/tournament name.'''

		series = self.json['match']['series']
		return "{} {} - {} ({})".format(series['name'], series['description'], series['year'], series['season'])

	def venue(self):
		'''Returns match venue.'''
		
		return self.json["match"]["ground"]["name"] + ", " + self.json["match"]["ground"]["country"]["name"]

	def match_format(self):
		'''Returns match format.'''

		return self.json["match"]["format"]

	def match_dates(self):
		'''Returns match date(s).'''

		return self.json['match']['daysInfo']

	def tv_umpire(self):
		'''Returns TV umpire name.'''

		try:
			return self.json['match']['tvUmpires'][0]['player']['longName']
		except:
			return None

	def playing11(self):
		'''Returns DataFrame of Playing 11 of both the teams.''' 

		teams = self.json['matchPlayers']['teamPlayers']
		team1 = teams[0]
		team2 = teams[1]

		team1_name = team1['team']['name']
		team2_name = team2['team']['name']

		df = {}
		df[team1_name] = [team1["players"][i]['player']['name'] for i in range(11)]
		df[team2_name] = [team2["players"][i]['player']['name'] for i in range(11)]


		return pd.DataFrame(df)


	def best_performers_of_match(self):
		'''
		Returns a tuple(length 2) of DataFrame of best performers of the match.

		Note - Best performer are highest run getters and wicket getter. It is different from Player of the match.
		'''

		batsmen = self.json['bestPerformance']['batsmen']
		bowlers = self.json['bestPerformance']['bowlers']



		batter, baller = {}, {}
		batter['name'] =  [batsmen[i]['player']['name'] for i in range(len(batsmen))]
		batter['team'] =  [batsmen[i]['teamAbbreviation'] for i in range(len(batsmen))]
		batter['runs'] =  [batsmen[i]['runs'] for i in range(len(batsmen))]
		batter['balls'] =  [batsmen[i]['balls'] for i in range(len(batsmen))]
		batter['fours'] =  [batsmen[i]['fours'] for i in range(len(batsmen))]
		batter['sixes'] =  [batsmen[i]['sixes'] for i in range(len(batsmen))]
		batter['strikerate'] =  [batsmen[i]['strikerate'] for i in range(len(batsmen))]

		baller['team'] =  [bowlers[i]['teamAbbreviation'] for i in range(len(bowlers))]
		baller['name'] =  [bowlers[i]['player']['name'] for i in range(len(bowlers))]
		baller['overs'] =  [bowlers[i]['overs'] for i in range(len(bowlers))]
		baller['maidens'] =  [bowlers[i]['maidens'] for i in range(len(bowlers))]
		baller['conceded'] =  [bowlers[i]['conceded'] for i in range(len(bowlers))]
		baller['wickets'] =  [bowlers[i]['wickets'] for i in range(len(bowlers))]
		baller['economy'] =  [bowlers[i]['economy'] for i in range(len(bowlers))]


		df_batsman = pd.DataFrame(batter)
		df_bowler = pd.DataFrame(baller)
		return (df_batsman, df_bowler)


	def summary(self):
		'''Returns a tuple(length 2) of DataFrame of batter and bowler summary.'''

		inning = self.json['scorecardSummary']['innings']
		number_of_innings = len(inning)


		def copy_list(list):
			# [1, 2] -> [1, 1, 2, 2]
			return pd.Series(np.concatenate([([i]*2) for i in list], axis=0))


		team = {}
		team['batting team'] = copy_list([inning[i]['team']['name'] for i in range(number_of_innings)])
		team['team total'] = copy_list([inning[i]['runs'] for i in range(number_of_innings)])
		team['team wickets'] = copy_list([inning[i]['wickets'] for i in range(number_of_innings)])
		team['team overs'] = copy_list([inning[i]['overs'] for i in range(number_of_innings)])
		

		batter = {}
		batter['batsman name'] = [inning[i]['inningBatsmen'][j]['player']['name'] for i in range(number_of_innings) for j in range(2)]
		batter['runs scored'] = [inning[i]['inningBatsmen'][j]['runs'] for i in range(number_of_innings) for j in range(2)]
		batter['balls faced'] = [inning[i]['inningBatsmen'][j]['balls'] for i in range(number_of_innings) for j in range(2)]
		batter['isOut'] = [inning[i]['inningBatsmen'][j]['isOut'] for i in range(number_of_innings) for j in range(2)]

		bowler = {}
		bowler['bowler name'] = [inning[i]['inningBowlers'][j]['player']['name'] for i in range(number_of_innings) for j in range(len(inning[i]['inningBowlers']))]
		
		bowler['runs conceded'] = [inning[i]['inningBowlers'][j]['conceded'] for i in range(number_of_innings) for j in range(len(inning[i]['inningBowlers']))]

		bowler['overs'] = [inning[i]['inningBowlers'][j]['overs'] for i in range(number_of_innings) for j in range(len(inning[i]['inningBowlers']))]

		bowler['wickets'] = [inning[i]['inningBowlers'][j]['wickets'] for i in range(number_of_innings) for j in range(len(inning[i]['inningBowlers']))]


		batter = pd.DataFrame(batter).assign(**team)	
		bowler = pd.DataFrame(bowler)
		bowler = bowler.assign(**team)
		

		return batter, bowler		


	def scorecard(self):
		'''Returns a tuple(length 3) of DataFrame of batter scorecard, bowler scorecard and teamdata.'''

		inning = self.json['scorecard']['innings']
		number_of_innings = len(inning)

		batter_scorecard, bowler_scorecard, team_data = {}, {}, {}

		team_data['team'] = [inning[i]['team']['name'] for i in range(number_of_innings)]
		team_data['runs'] = [inning[i]['runs'] for i in range(number_of_innings)]
		team_data['wickets'] = [inning[i]['wickets'] for i in range(number_of_innings)]
		team_data['overs'] = [inning[i]['overs'] for i in range(number_of_innings)]
		team_data['extras'] = [inning[i]['extras'] for i in range(number_of_innings)]
		team_data['byes'] = [inning[i]['byes'] for i in range(number_of_innings)]
		team_data['legbyes'] = [inning[i]['legbyes'] for i in range(number_of_innings)]
		team_data['wides'] = [inning[i]['wides'] for i in range(number_of_innings)]
		team_data['noballs'] = [inning[i]['noballs'] for i in range(number_of_innings)]
		team_data['noballs'] = [inning[i]['noballs'] for i in range(number_of_innings)]

		batter_scorecard['batsman'] = [inning[i]['inningBatsmen'][j]['player']['name'] for i in range(number_of_innings) for j in range(11)]
		batter_scorecard['runs'] = [inning[i]['inningBatsmen'][j]['runs'] for i in range(number_of_innings) for j in range(11)]
		batter_scorecard['balls'] = [inning[i]['inningBatsmen'][j]['balls'] for i in range(number_of_innings) for j in range(11)]
		batter_scorecard['4s'] = [inning[i]['inningBatsmen'][j]['fours'] for i in range(number_of_innings) for j in range(11)]
		batter_scorecard['6s'] = [inning[i]['inningBatsmen'][j]['sixes'] for i in range(number_of_innings) for j in range(11)]
		batter_scorecard['strikerate'] = [inning[i]['inningBatsmen'][j]['strikerate'] for i in range(number_of_innings) for j in range(11)]

		# wicket_map as per espn data
		wicket_map = {
			1: "caught",
			2: "bowled",
			3: "lbw",
			4: "run out",
			5: "stumping",
			6: "hitwicket",
			7: "handled the ball",
			8: "obstructing the field",
			11: "retired out",
			12: "not out",
			13: "retired not out",
			None: "DNB",
		}

		batter_scorecard['wicket type'], batter_scorecard['fielders'], batter_scorecard['bowler'] = [], [], []
		for i in range(number_of_innings):
			for j in range(11):
				dismissal_type = inning[i]['inningBatsmen'][j]['dismissalType']
				kind_of_wicket = wicket_map[dismissal_type]
				fielders, bowler = np.nan, np.nan

				if (dismissal_type ==  1) or (dismissal_type ==  5):
					field = inning[i]['inningBatsmen'][j]['dismissalFielders']
					try: 
						fielders = [ field[i]['player']['name'] for i in range(len(field))]
					except:
						fielders = None			


					try:
						bowler = inning[i]['inningBatsmen'][j]['dismissalBowler']['name']
					except:
						bowler = None


				elif (dismissal_type ==  2) or (dismissal_type ==  3) or (dismissal_type ==  6):
					try:
						bowler = inning[i]['inningBatsmen'][j]['dismissalBowler']['name']
					except:
						bowler = None

				elif (dismissal_type ==  4): # F
					field = inning[i]['inningBatsmen'][j]['dismissalFielders']
					try:
						fielders = [ field[i]['player']['name'] for i in range(len(field))]	
					except:
						fielders = None	



				elif (dismissal_type ==  12) or (dismissal_type ==  13):
					fielders = ['-']				
					bowler = '-'
					

				batter_scorecard['wicket type'].append(kind_of_wicket)
				batter_scorecard['fielders'].append(fielders)
				batter_scorecard['bowler'].append(bowler)


		bowler_scorecard['name'] = [inning[i]['inningBowlers'][j]['player']['name'] for i in range(number_of_innings) for j in range(len(inning[i]['inningBowlers']))]

		bowler_scorecard['overs'] = [inning[i]['inningBowlers'][j]['overs'] for i in range(number_of_innings) for j in range(len(inning[i]['inningBowlers']))]

		bowler_scorecard['maidens'] = [inning[i]['inningBowlers'][j]['maidens'] for i in range(number_of_innings) for j in range(len(inning[i]['inningBowlers']))]
		bowler_scorecard['conceded'] = [inning[i]['inningBowlers'][j]['conceded'] for i in range(number_of_innings) for j in range(len(inning[i]['inningBowlers']))]
		bowler_scorecard['wickets'] = [inning[i]['inningBowlers'][j]['wickets'] for i in range(number_of_innings) for j in range(len(inning[i]['inningBowlers']))]
		bowler_scorecard['economy'] = [inning[i]['inningBowlers'][j]['economy'] for i in range(number_of_innings) for j in range(len(inning[i]['inningBowlers']))]


		batter_scorecard = pd.DataFrame(batter_scorecard).astype({"runs": np.int}, errors="ignore")
		bowler_scorecard = pd.DataFrame(bowler_scorecard)
		teamdata = pd.DataFrame(team_data)
		return batter_scorecard, bowler_scorecard, teamdata


	def fow(self):
		'''Returns DataFrame of fall of wickets.'''

		inning = self.json['scorecard']['innings'] # list

		df = {}
		df['team'] = [inning[i]['team']['name'] for i in range(len(inning)) for j in range(len(inning[i]['inningWickets']))]
		df['player'] = [inning[i]['inningWickets'][j]['player']['name'] for i in range(len(inning)) for j in range(len(inning[i]['inningWickets']))]
		df['wicket'] = [inning[i]['inningWickets'][j]['fowWicketNum'] for i in range(len(inning)) for j in range(len(inning[i]['inningWickets']))]
		df['over'] = [inning[i]['inningWickets'][j]['fowOvers'] for i in range(len(inning)) for j in range(len(inning[i]['inningWickets']))]
		df['runs'] = [inning[i]['inningWickets'][j]['fowRuns'] for i in range(len(inning)) for j in range(len(inning[i]['inningWickets']))]
		df = pd.DataFrame(df)

		return df


	def partnerships(self):
		'''Returns DataFrame of batting partnership.'''

		inning = self.json['scorecard']['innings']

		df = {}

		df['for wicket'] = [j+1 for i in range(len(inning)) for j in range((len(inning[i]['inningPartnerships'])))]
		df['team'] = [inning[i]['team']['name'] for i in range(len(inning)) for j in range(len(inning[i]['inningPartnerships']))]

		df['player1'] = [inning[i]['inningPartnerships'][j]['player1']['name'] for i in range(len(inning)) for j in range(len(inning[i]['inningPartnerships'])) ]
		df['player2'] = [inning[i]['inningPartnerships'][j]['player2']['name'] for i in range(len(inning)) for j in range(len(inning[i]['inningPartnerships'])) ]

		df['player1 runs'] = [inning[i]['inningPartnerships'][j]['player1Runs'] for i in range(len(inning)) for j in range(len(inning[i]['inningPartnerships'])) ]
		df['player2 runs'] = [inning[i]['inningPartnerships'][j]['player2Runs'] for i in range(len(inning)) for j in range(len(inning[i]['inningPartnerships'])) ]

		df['player1 balls'] = [inning[i]['inningPartnerships'][j]['player1Balls'] for i in range(len(inning)) for j in range(len(inning[i]['inningPartnerships'])) ]
		df['player2 balls'] = [inning[i]['inningPartnerships'][j]['player2Balls'] for i in range(len(inning)) for j in range(len(inning[i]['inningPartnerships'])) ]
		
		df['partnership runs'] = [inning[i]['inningPartnerships'][j]['runs'] for i in range(len(inning)) for j in range(len(inning[i]['inningPartnerships'])) ]
		df['partnership balls'] = [inning[i]['inningPartnerships'][j]['balls'] for i in range(len(inning)) for j in range(len(inning[i]['inningPartnerships'])) ]

		
		df = pd.DataFrame(df)

		return df
