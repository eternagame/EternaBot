from eternabot.eterna_utils import *
from eternabot import strategy_template

class Strategy(strategy_template.Strategy):
	def __init__(self):
		strategy_template.Strategy.__init__(self)
		self.title_ = "Repetition"
		self.author_ = "aldo"
		self.url_ = "http://getsatisfaction.com/eternagame/topics/_strategy_market_repetition"
		#ratio of gc pairs in junctions
		self.default_params_ = [0,0,5,5,5,5]
		self.code_length_ = 30
		self.publishable_ = True

	def score(self, design, params):
		sequence = design['sequence']			
		length = len(sequence)
		rep_cnt = [0] * 6
		n_gram = {}
		for ii in range(0,length):
			for jj in range(2,6):
				if(ii+jj>=length):
					break
				substring=sequence[ii:(ii+jj)]
				if (substring in n_gram):
					n_gram[substring] += 1
				else:
					n_gram[substring] = 0
		
		score=100
		for substring in n_gram.keys():
			rep_cnt[len(substring)] += n_gram[substring]
		for ii in range(1,6):
			#normalize by sequence length
			score -= float(params[ii] * rep_cnt[ii])/length
			#score -= float(params[ii] * rep_cnt[ii])
		return score
		
