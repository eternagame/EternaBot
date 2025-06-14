#by Chengfu chengfuc@andrew.cmu.edu date:6.19
import re
from eternabot.eterna_utils import *
from eternabot import strategy_template

class Strategy(strategy_template.Strategy):
	def __init__(self):
		strategy_template.Strategy.__init__(self)
		
		self.title_ = "Green and blue nucleotides a strand + Strong middle half"
		self.author_ = "Eli Fisker"
		self.url_ = "http://getsatisfaction.com/eternagame/topics/_strategy_market_green_and_blue_nucleotides_a_strand_strong_middle_half"
		self.default_params_ = [-1]
		self.code_length_ = 190
		self.publishable_ = True
	
		
	def score(self, design, params):			
		
		elements = design['secstruct_elements']
		sequence = design['sequence']
		pairmap = design['pairmap']
		
		score = 100
		for ii in range(0,len(elements)):                                                                                               
			elem = elements[ii]

			if(elem.type_ == RNAELEMENT_STACK):
				first_string = ""
				second_string = ""
				
				for jj in range(0,len(elem.indices_),2):
					first_string += sequence[elem.indices_[jj]]
					second_string += sequence[elem.indices_[jj+1]]
				
				first_string = first_string.upper()
				second_string = second_string.upper()
				
				if len(elem.indices_) < 12:
					banned = "^[U|C][U|C][U|C][U|C]"
				else:
					banned = "^[U|C][U|C][U|C][U|C][U|C]"
				
				if ii ==0:
					banned = "^[U|C][U|C][U|C][U|C][U|C][U|C][U|C]"
				
				for jj in range(0,len(first_string)):
					if re.search(banned,first_string[jj:]) != None:
						score += params[0]
					if re.search(banned,second_string[jj:]) != None:
						score += params[0]
		
		return score		

