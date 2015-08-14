import switch_utils
import strategy_template

class Strategy(strategy_template.Strategy):
	def __init__(self):
		strategy_template.Strategy.__init__(self)
		
		self.title_ = "deivad's strategy"
		self.author_ = "deivad"
		self.url_ = "http://getsatisfaction.com/eternagame/topics/_strategy_market_deivads_strategy"
		self.default_params_ = [1, 1, 4 , -1, 1, -1, 2, -2, -1, -10.0, -2, -5, 20, 0.05, 0]
		self.code_length_ = 60
		self.publishable_ = True
		self.comprehensive_ = True
		self.denormalized_ = True

	def score(self, design, params):
		
		totalscore = 0
		states = range(1, 3)
		for state in states:

			n = 'state' + str(state)

			elements = design[n]['default']['secstruct_elements']
			pairmap = design[n]['default']['pairmap']
			sequence= design['sequence']
			fe = design[n]['default']['fe']
			meltpoint = design[n]['default']['meltpoint']
			score = 80
			total_pairs= design[n]['default']['gc'] + design[n]['default']['gu'] + design[n]['default']['ua']
			gc_rate = float(design[n]['default']['gc']) / total_pairs
			gu_rate = float(design[n]['default']['gu']) / total_pairs
			
			for ii in range(0,len(elements)):
				if(elements[ii].type_ == switch_utils.RNAELEMENT_LOOP):
					if(elements[ii].score_ < params[0]):
						score += params[1]
					elif(elements[ii].score_ > params[2]):
						score += params[3]
					elif(elements[ii].score_ > params[6]):
						closing_pairs = elements[ii].get_loop_closing_pairs(sequence,pairmap)
						is_there_gu = False
						for jj in range(0,len(closing_pairs)):
							pair = closing_pairs[jj]
							if(pair == "GU" or pair == "UG"):
								is_there_gu = True
								break
						
						if(is_there_gu):
							score += params[7]
				else:
					stacklen = len(elements[ii].indices_) / 2
					gc_count = 0
					gu_count = 0
					if(stacklen <= 5):
						for jj in range(0,len(elements[ii].indices_),2):
							pair = sequence[elements[ii].indices_[jj]] + sequence[elements[ii].indices_[jj+1]]
							if(pair == "GC" or pair == "CG"):
								gc_count += 1
							if(pair == "GU" or pair == "UG"):
								gu_count += 1
						if(gc_count > 1):
							score += params[4]
						if(gu_count > 0):
							score += params[5]
							
			
			for ii in range(0,len(sequence)):
				if(sequence[ii] == "C" and pairmap[ii] < 0):
					score += params[8]
			
			score += fe / params[9]
			
			if(gc_rate > 0.5):
				score += params[10]
			
			if(gu_rate > 0.15):
				score += params[11]
			
			score += meltpoint/params[12]
			totalscore += score

		totalscore = float(totalscore) / len(states)
		return (params[13] * totalscore) + params[14]
		 