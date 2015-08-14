import switch_utils
import strategy_template

class Strategy(strategy_template.Strategy):
	def __init__(self):
		strategy_template.Strategy.__init__(self)
		
		self.title_ = "Green with Red"
		self.author_ = "Eli Fisker"
		self.url_ = "http://getsatisfaction.com/eternagame/topics/_strategy_market_green_paired_with_red"
		self.default_params_ = [0.05, 0]
		self.code_length_ = 10
		self.publishable_ = True


	def score(self, design, params):

		totalscore = 0
		states = range(1, 3)

		for n in states:

			sequence = design['sequence']
			secstruct = design['state' + str(n)]['default']['secstruct']
			
			score = 100
			
			for ii in range(2,len(secstruct)- 20):
				if(secstruct[ii] == "."):
					if(sequence[ii] == "C"):
						score -= 1
			
			totalscore += score
		
		totalscore = float(totalscore)/len(states)
		return (totalscore * params[0]) + params[1]
