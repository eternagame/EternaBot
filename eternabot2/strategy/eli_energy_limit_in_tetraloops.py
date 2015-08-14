import switch_utils
import strategy_template

class Strategy(strategy_template.Strategy):
	def __init__(self):
		strategy_template.Strategy.__init__(self)
		
		self.title_ = "Energy Limit in Tetraloops"
		self.author_ = "Eli Fisker"
		self.url_ = "http://getsatisfaction.com/eternagame/topics/_strategy_market_energy_limit_in_tetraloops"
		self.default_params_ = [4.5, -10, 0.05, 0] # Max allowed energy, penalization increment, amount over max per penalization
		self.code_length_ = 14
		self.publishable_ = True
		self.denormalized_ = True
		self.comprehensive_ = False

	def score(self, design, params):

		totalscore = 0
		states = range(1, 3)

		for state in states:
			n = 'state' + str(state)

			elements = design[n]['default']['secstruct_elements']
			tetraloop_found = False
			score = 100

			for element in elements:
				if element.type_ != switch_utils.RNAELEMENT_LOOP: continue

				closing_pairs = element.get_loop_closing_pairs(design['sequence'],design[n]['default']['pairmap'])
				if len(closing_pairs) == 1 and len(element.indices_) == 4:
					tetraloop_found = True
					if (element.score_ > params[0]): score += params[1]
	                                
			
			if not tetraloop_found:
				return switch_utils.UNSCORABLE
			totalscore += score

		totalscore = float(totalscore) / len(states)
		return (params[2] * totalscore) + params[3]
