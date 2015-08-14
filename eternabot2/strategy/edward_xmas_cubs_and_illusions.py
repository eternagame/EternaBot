import switch_utils
import strategy_template

class Strategy(strategy_template.Strategy):
	def __init__(self):
		strategy_template.Strategy.__init__(self)
		
		self.title_ = "Xmas, cubs and illusions"
		self.author_ = "Edward Lane"
		self.url_ = "http://getsatisfaction.com/eternagame/topics/_strategy_market_xmas_cubs_and_illusions"
		self.default_params_ = [0.05, 0]
		self.code_length_ = 10
		self.publishable_ = True


	def score(self, design, params):

		totalscore = 0
		states = range(1, 3)

		for state in states:
			n = 'state' + str(state)

			gcs = design[n]['default']['gc']
			gus = design[n]['default']['gu']
			aus = design[n]['default']['ua']
			
			score = 100
			
			if(gus + aus == 0):
				score -= 100
			elif(gcs + aus == 0):
				score -= 100
			elif(gcs + gus == 0):
				score -= 100

			totalscore += score
			
		totalscore = float(totalscore) / len(states)
		return (totalscore * params[0]) + params[1]
