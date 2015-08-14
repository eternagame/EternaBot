import strategy_template
import switch_utils

class Strategy(strategy_template.Strategy):
	def __init__(self):
		
		strategy_template.Strategy.__init__(self)
		
		self.title_ = "No boost in small multiloops"
		self.author_ = "Eli Fisker"
		self.url_ = "http://getsatisfaction.com/eternagame/topics/_strategy_market_no_boost_in_small_multiloops"
		self.default_params_ = [0.05, 0]
		self.code_length_ = 20
		self.publishable_ = True

		

	def score(self, design, params):

		totalscore = 0
		states = range(1, 3)

		for state in states:

			n = 'state' + str(state)

			sequence = design['sequence']
			secstruct = design[n]['default']['secstruct']
			elements = design[n]['default']['secstruct_elements']
			
			score = 100
			
			for ii in range(0,len(elements)):
				if(elements[ii].type_ == switch_utils.RNAELEMENT_LOOP):
					loop_groups = elements[ii].get_loop_groups()
					if(len(loop_groups) > 2):
						num_bases = len(elements[ii].indices_)
						if(num_bases > 0 and num_bases / float(len(loop_groups)) < 2.0):
							for jj in range(0,len(elements[ii].indices_)):
								if(sequence[elements[ii].indices_[jj]] != "A"):
									score -=1
									
									
			totalscore += score

		totalscore = float(totalscore) / len(states)
		return (totalscore * params[0]) + params[1]
