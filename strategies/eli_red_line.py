#by Chengfu chengfuc@andrew.cmu.edu date:6.27
from eterna_utils import *
import strategy_template

class Strategy(strategy_template.Strategy):
	def __init__(self):
		strategy_template.Strategy.__init__(self)
		
		self.title_ = "Eli Red line"
		self.author_ = "Eli Fisker"
		self.url_ = "http://getsatisfaction.com/eternagame/topics/_strategy_market_red_line"
		self.default_params_ = [-1]
		self.code_length_ = 46
		self.publishable_ = True
		self.denormalized_ = True
		self.comprehensive_ = False

	def isExist(self,indices, index):
		for ii in range(0,len(indices)):
			for jj in range(0, len(indices[ii])):
				if(index==indices[ii][jj]):
					return ii
		return -1
        
	def score(self, design, params):			
		
		elements = design['secstruct_elements']
		sequence = design['sequence']
		pairmap = design['pairmap']
		
		score = 0
		stacks=[]
		multiplier=0
                for ii in range(0,len(elements)):                                                                                               
			elem = elements[ii]
                        stackIndice=[]  	
			if(elem.type_ == RNAELEMENT_STACK):
                                for jj in range(0,len(elem.indices_)):
                                        stackIndice.append(elem.indices_[jj])
                        stacks.append(stackIndice)
                for ii in range(0,len(sequence)-2):
                        if(sequence[ii]==sequence[ii+1] and\
                           sequence[ii]==sequence[ii+2] and\
                           sequence[ii]=='G'):
                                if(self.isExist(stacks,ii)>=0 and self.isExist(stacks,ii+1)>=0 and
                                   self.isExist(stacks,ii+2)>=0 and len(stacks[self.isExist(stacks,ii)])>16):
                                                continue
                                else:
                                        multiplier = multiplier+1
                                                        
                score += multiplier*params[0]
                return score
















