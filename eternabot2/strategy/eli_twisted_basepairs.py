import strategy_template
import switch_utils

class Strategy(strategy_template.Strategy):
	def __init__(self):
		
		strategy_template.Strategy.__init__(self)
		
		self.title_ = "Twisted Basepairs"
		self.author_ = "Eli Fisker"
		self.url_ = "http://getsatisfaction.com/eternagame/topics/_strategy_market_twisted_basepairs"
		self.default_params_ = [0.05, 0]
		self.code_length_ = 15
		self.publishable_ = True
		self.denormalized_ = True
		self.comprehensive_ = False

	def score(self, design, params):

		totalscore = 0
		states = range(1, 3)

		for state in states:
			n = 'state' + str(state)
			score = 100
			
			elements = design[n]['default']['secstruct_elements']
			pairmap = design[n]['default']['pairmap']
			sequence = design['sequence']
			
			for ii in range(0,len(elements)):
				if(elements[ii].type_ == switch_utils.RNAELEMENT_STACK):
					indices = elements[ii].indices_
					last_pair = sequence[indices[0]] + sequence[indices[1]]
					
					for jj in range(2,len(indices),2):
						current_pair = sequence[indices[jj]] + sequence[indices[jj+1]]
						if(last_pair == current_pair):
							score -= 1
						
						last_pair = current_pair
			
			totalscore += score

		totalscore = float(totalscore) / len(states)
		return (totalscore * params[0]) + params[1]
