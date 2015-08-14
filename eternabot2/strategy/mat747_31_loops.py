import strategy_template
import switch_utils

class Strategy(strategy_template.Strategy):
	def __init__(self):
		
		strategy_template.Strategy.__init__(self)
		
		self.title_ = "Closing GC pairs in 3-1 internal loops"
		self.author_ = "mat747"
		self.url_ = "http://eterna.cmu.edu//sites/default/files/chat_screens/scr267_1311088579805.png"
		self.default_params_ = [1, 0.05, 0]
		self.code_length_ = 30
		self.publishable_ = True
		

	def score(self, design, params):

		totalscore = 0
		states = range(1, 3)

		for state in states:
			n = 'state' + str(state)

			elements = design[n]['default']['secstruct_elements']
			loop_count = 0
			right_loop_count = 0
			sequence = design['sequence']
			pairmap = design[n]['default']['pairmap']
			
			for ii in range(0,len(elements)):
				element = elements[ii]
				if(element.type_ == switch_utils.RNAELEMENT_LOOP):
					loop_groups = elements[ii].get_loop_groups()
					if(len(loop_groups) == 2):
						grp_1_len = len(loop_groups[0])
						grp_2_len = len(loop_groups[1])
						closing_pairs = element.get_loop_closing_pairs(sequence,pairmap)
						if len(closing_pairs) < 2:
							continue
						if(grp_1_len == 1 and grp_2_len ==3):
							loop_count += 0	
						elif(grp_1_len == 3 and grp_2_len == 1):
							loop_count += 1
							if(closing_pairs[0] == "CG" and closing_pairs[1] == "GC"):
								right_loop_count += 1
							
			
			if(loop_count == 0):
				return switch_utils.UNSCORABLE
			
			score = 100 - (loop_count - right_loop_count) * params[0]
			totalscore += score

		totalscore = float(totalscore) / len(states)
		return (totalscore * params[1]) + params[2]
