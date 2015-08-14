import strategy_template

class Strategy(strategy_template.Strategy):
	def __init__(self):
		
		strategy_template.Strategy.__init__(self)
		
		self.title_ = "[Example] 60% of pairs should be GC pairs"
		self.author_ = "Example"
		self.url_ = "http://getsatisfaction.com/eternagame/topics/_strategy_market_example_60_of_pairs_must_be_gc_pairs-1erc6"
		self.default_params_ = [0.6, 0.05, 0]
		self.code_length_ = 1
		self.publishable_ = True
		self.denormalized_ = True
		self.comprehensive = False
		

	def score(self, design, params):

		totalscore = 0
		states = range(1, 3)

		for state in states:

			n = 'state' + str(state)
			score = 100-(abs(params[0] - float(design[n]['default']['gc']) / (design[n]['default']['gu'] + design[n]['default']['gc'] + design[n]['default']['ua']))) * 100
			totalscore += score

		totalscore = float(totalscore) / len(states)
		return (totalscore * params[1]) + params[2]