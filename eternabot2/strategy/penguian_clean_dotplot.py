import switch_utils
import strategy_template

class Strategy(strategy_template.Strategy):
	def __init__(self):
		strategy_template.Strategy.__init__(self)
		
		self.title_ = "Clean Dot Plot"
		self.author_ = "penguian"
		self.url_ = "http://getsatisfaction.com/eternagame/topics/_strategy_market_clean_dot_plot"
		self.default_params_ = [0.05, 0]
		self.code_length_ = 10
		self.publishable_ = True
		self.is_part_of_ensemble_ = False
		self.denormalized_ = True
		self.comprehensive_ = False

	def score(self, design, params):			
		
		totalscore = 0
		states = range(1, 3)

		for state in states:
			ns = 'state' + str(state)
			penalty = 0.0
			
			n = len(design['sequence'])
			npairs = design[ns]['default']['gc'] + design[ns]['default']['gu'] + design[ns]['default']['ua']
			dotplot = design[ns]['default']['dotplotU']
			pairmap = design[ns]['default']['pairmap']
			
			for ii in range(0,len(dotplot)):
				i_index = dotplot[ii][0]
				j_index = dotplot[ii][1]

				if(i_index < len(pairmap) and pairmap[i_index] != j_index):
					penalty += dotplot[ii][2]
						
			score = 100 -(penalty / npairs)
			totalscore += score

		totalscore = float(totalscore) / len(states)
		return (totalscore*params[0]) + params[1]