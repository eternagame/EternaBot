import switch_utils
import strategy_template

class Strategy(strategy_template.Strategy):
	def __init__(self):
		strategy_template.Strategy.__init__(self)
		
		self.title_ = "Base Pair Percentages"
		self.author_ = "Edward Lane"
		self.url_ = "http://getsatisfaction.com/eternagame/topics/_strategy_market_base_pair_percentages"
		self.default_params_ = [0.55, 0.35, 0.20, -20, -65, 10, 10, 10, 10, 0.05, 0]
		self.code_length_ = 20
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
			
			if(float(gcs)/npairs > params[0]):
				score -= params[5]
			
			if(float(aus)/npairs < params[1]):
				score -= params[6]
			
			if(float(gus)/npairs > params[2]):
				score -= params[7]
			
			if(fe > params[3] or fe < params[4]):
				score -= params[8]
			totalscore += score

		totalscore = float(totalscore)/len(states)
		return (totalscore * params[9]) + params[10]
