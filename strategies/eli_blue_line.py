#by Chengfu chengfuc@andrew.cmu.edu date:6.27
from eterna_utils import *
import strategy_template

class Strategy(strategy_template.Strategy):
	def __init__(self):
		strategy_template.Strategy.__init__(self)
		
		self.title_ = "Eli Blue line"
		self.author_ = "Eli Fisker"
		self.url_ = "http://getsatisfaction.com/eternagame/topics/_strategy_market_blue_line"
		self.default_params_ = [-1]
		self.code_length_ = 45
		self.publishable_ = True

        def isExist(self, array, element):
                for ii in range(0,len(array)):
                        for jj in range(0, len(array[ii])):
                                if(array[ii][jj]==element):
                                        return True
                return False
	def score(self, design, params):			
		
		elements = design['secstruct_elements']
		sequence = design['sequence']
		pairmap = design['pairmap']
		
		score = 100
		indice=[]
		stacks=[]
		multiplier=0
                for ii in range(0,len(elements)):                                                                                               
			elem = elements[ii]
                        stackIndice=[]  	
			if(elem.type_ == RNAELEMENT_STACK):
                                for jj in range(0,len(elem.indices_)):
                                        stackIndice.append(elem.indices_[jj])
                        if(len(stackIndice)>0):
                                stacks.append(stackIndice)
               #print(stacks)
		
                for ii in range(0,len(sequence)-2):
                        if(sequence[ii]==sequence[ii+1] and\
                           sequence[ii]==sequence[ii+2] and\
                           self.isExist(stacks,ii) and self.isExist(stacks,ii+1) and self.isExist(stacks,ii+2)and\
                           sequence[ii]=='U'):
                                        multiplier=multiplier+1;
                score += multiplier*params[0]
                return score
















