import strategy_template
import switch_utils

class Strategy(strategy_template.Strategy):
	def __init__(self):
		
		strategy_template.Strategy.__init__(self)
		
		self.title_ = "Tests by Region - loops"
		self.author_ = "Quasispecies"
		self.url_ = "http://getsatisfaction.com/eternagame/topics/_strategy_market_tests_by_region"
		self.default_params_ = [1, 1, 0.05, 0]
		self.code_length_ = 30
		self.publishable_ = True
		self.denormalized_ = True
		self.comprehensive_ = False

	def score(self, design, params):

		totalscore = 0
		states = range(1, 3)

		for n in states:
			score = 100
			
			elements = design['state' + str(n)]['default']['secstruct_elements']
			sequence = design['sequence']
			
			for ii in range(0,len(elements)):
				if(elements[ii].type_ == switch_utils.RNAELEMENT_LOOP):
					looplen = len(elements[ii].indices_)
					if(looplen == 0):
						continue
					if(elements[ii].score_ / looplen > 0.5):
						score -= params[0]
					
					groups = elements[ii].get_loop_groups()
					for jj in range(0,len(groups)):
						if len(groups[jj]) >= 4:
							for kk in range(0,len(groups[jj])-4):
								comp = ""
								for zz in range(3,0,-1):
									if(sequence[kk+zz] == "A"):
										comp += "U"
									elif(sequence[kk+zz] =="U"):
										comp += "A"
									elif(sequence[kk+zz] =="G"):
										comp += "C"
									else:
										comp += "G"
								
								score -= (sequence.count(comp)) * params[1]
			
			totalscore += score

		totalscore = float(totalscore) / len(states)
		return (totalscore * params[2]) + params[3]