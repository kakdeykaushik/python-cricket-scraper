import numpy as np
from yaml import safe_load
import pandas as pd
import glob
from cricscraper.cricinfo import CricInfo
from cricscraper.matchinfo import MatchInfo

class CricSheet:
	
	innings_name = ["1st innings", "2nd innings", "3rd innings", "4th innings"]

	
	def __init__(self, files=None, folder=None):

		if folder:
			self.files = glob.glob("{}/*.yaml".format(folder))
		else:
			self.files = files

		self.dataFrame =  pd.DataFrame()

		self.__parser()
			


	@staticmethod
	def __get_fielders(wicket):
		if wicket != 0:
			try:
				return ", ".join(wicket.get('fielders'))
			except:
				return None
		return None


	def __parser(self):

		ordered_columns = ['match id', 'inning', 'delivery', 'over', 'batsman', 'non striker', 'bowler', 'runs off bat', 'extras', 'total', 'extra kind', 'wicket kind', 'player out', 'fielders', 'team1', 'team2', 'outcome', 'winner', 'by', 'win amount', 'player of match','toss winner', 'toss decision', 'match type', 'venue', 'city', 'gender', 'umpire1','umpire2']

		for filename in self.files:
			with open(filename) as f_input:
				data = safe_load(f_input)

				innings = data['innings']
				for i in range(len(innings)):
					dict_innings = {}
					try:
						inning = innings[i][CricSheet.innings_name[i]]['deliveries']
					except:
						continue

					dict_innings["inning"] = np.ones(len(inning), dtype=int) * (i+1)
					dict_innings['delivery'] = [delivery for ball in inning for delivery in ball]
					dict_innings['batsman'] = [list(ball.values())[0].get("batsman") for ball in inning]
					dict_innings['non striker'] = [list(ball.values())[0].get("non_striker") for ball in inning]
					dict_innings['bowler'] = [list(ball.values())[0].get("bowler") for ball in inning]

					dict_innings["runs"] = [list(ball.values())[0].get('runs') for ball in inning]
					dict_innings["wicket"] = [list(ball.values())[0].get('wicket', 0) for ball in inning]
					dict_innings['extra kind1'] = [list(ball.values())[0].get('extras', 0) for ball in inning]

					frame = pd.DataFrame(dict_innings)
					dict_innings['runs off bat'] = frame['runs'].apply(lambda x: x.get('batsman'))
					dict_innings['extras'] = frame['runs'].apply(lambda x: x.get('extras'))
					dict_innings['total'] = frame['runs'].apply(lambda x: x.get('total')).cumsum()
					dict_innings['extra kind'] = frame['extra kind1'].apply(lambda x: next(iter(x.keys())) if x != 0 else None)
					dict_innings['over'] = frame['delivery'].apply(lambda x: np.ceil(x))
					
					def fn(x):
						try:
							return x.get('kind') if x != 0 else None
						except:
							return None
							
					def fn1(x):
						try:
							return x.get('player_out') if x != 0 else None
						except:
							return None

					dict_innings['wicket kind'] = frame.wicket.apply(fn)
					dict_innings['player out'] = frame.wicket.apply(fn1)
					dict_innings['fielders'] = frame.wicket.apply(CricSheet.__get_fielders)


					# get match info from Info class
					match_info = MatchInfo(data["info"])
					assign_info = match_info.dict_info()
					assign_info['match id'] = int(filename.split('.')[0].split('/')[-1])
					
					frame = pd.DataFrame(dict_innings).assign(**assign_info)

					frame.drop(["runs", "wicket", "extra kind1"], axis=1, inplace=True)

					self.dataFrame = pd.concat([self.dataFrame, frame])

				self.dataFrame.reset_index(inplace=True, drop=True)
				
				self.dataFrame = self.dataFrame[ordered_columns]



	def view(self):
		'''
		Returns DataFrame.

		DataFrame can be used directly for required purposes.
		'''

		return self.dataFrame


	def save(self, filename="output"):
		'''
		Saves the converted csv file.

		Parameter:
		filename (string): name of the output csv file 
			optional: True
			default: "output.csv"
		'''

		if filename.endswith(".csv"):
			filename = filename.replace('.csv', '')
		
		filename += ".csv"

		print("File saved - {}".format(filename))
		return self.dataFrame.to_csv(filename)


	def get_more_info(self):
		'''Returns dictionary of CricInfo object'''
		
		data = {}
		for file in self.files:
			match_id = int(file.split('.')[0].split('/')[-1])
			data[str(match_id)] = CricInfo(match_id)

		return data


