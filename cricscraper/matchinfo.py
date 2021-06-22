class MatchInfo:
	def __init__(self, info):
		self.info = info
	
		self.city = self._get_city()
		self.gender = self._get_gender()
		self.match_type = self._get_match_type()

		self.team1 = self._get_team()[0]
		self.team2 = self._get_team()[1]
		self.toss_winner = self._get_toss_winner()
		self.toss_decision = self._get_toss_decision()

		self.umpire1 = self._get_umpire()[0]
		self.umpire2 = self._get_umpire()[1]
		self.player_of_match = self._get_player_of_match()
		self.venue = self._get_venue()

		self.outcome = self._get_result_info()[0]
		self.by = self._get_result_info()[1]
		self.win_amount = self._get_result_info()[2]
		self.winner = self._get_result_info()[3]

	def _get_city(self):
		return self.info['city']

	def _get_gender(self):
		return self.info['gender']

	def _get_match_type(self):
		return self.info['match_type']

	def _get_player_of_match(self):
		try:
			return self.info['player_of_match'][0]
		except:
			return None

	def _get_city(self):
		try:
			return self.info['city']
		except:
			return None

	def _get_team(self):
		return self.info['teams']

	def _get_toss_winner(self):
		return self.info['toss']['winner']

	def _get_toss_decision(self):
		return self.info['toss']['decision']

	def _get_umpire(self):
		try:
			return self.info['umpires']
		except:
			return None, None

	def _get_venue(self):
		return self.info['venue']

	def _get_result_info(self):
		outcome = self.info['outcome']
		winner, by, win_amount = None, None, None
		try:
			outcome = outcome["result"]
		except:
			try:
				winner = outcome["winner"]
				win_type = outcome["by"]

				if "innings" in win_type.keys():
					by = "innings"
					win_amount = win_type['runs']
				elif "runs" in win_type.keys():
					by = "runs"
					win_amount = win_type['runs']
				elif "wickets" in win_type.keys():
					by = "wickets"
					win_amount = win_type['wickets']
				outcome = "normal"
			except:
				outcome = None


		return (outcome, by, win_amount, winner)

	
	def dict_info(self):
		"""
		Returns match info in dictionary form.
		"""

		return {
			"city": self.city,
			"gender": self.gender,
			"match type": self.match_type,
			"outcome": self.outcome,
			"winner": self.winner,
			"by": self.by,
			"win amount": self.win_amount,
			"player of match": self.player_of_match,
			"team1": self.team1,
			"team2": self.team2,
			"toss winner": self.toss_winner,
			"toss decision": self.toss_decision,
			"umpire1": self.umpire1,
			"umpire2": self.umpire2,
			"venue": self.venue,
		}

