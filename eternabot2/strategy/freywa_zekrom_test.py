import switch_utils
import strategy_template

class Strategy(strategy_template.Strategy):
	def __init__(self):
		strategy_template.Strategy.__init__(self)
		
		self.title_ = "Zekrom Test"
		self.author_ = "Freywa"
		self.url_ = "http://getsatisfaction.com/eternagame/topics/_strategy_market_zekrom_test"
		self.default_params_ = [0.5, 100, 2, 0.05, 0]
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
			fe = design[n]['default']['fe']
			npairs = gcs + gus + aus
			
			score = 0
			
			gcp = float(gcs)/npairs
			score -= abs(gcp - params[0]) * params[1]
			
			score -= gus * params[2]
			
			totalscore += score

		totalscore = float(totalscore) / len(states)
		return (totalscore * params[3]) + params[4]
		
