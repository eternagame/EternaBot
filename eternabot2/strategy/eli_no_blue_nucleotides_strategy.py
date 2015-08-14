#by Chengfu chengfuc@andrew.cmu.edu date:6.21
from switch_utils import *
import re
import strategy_template

class Strategy(strategy_template.Strategy):
    def __init__(self):
        
        strategy_template.Strategy.__init__(self)
        
        self.title_ = "No blue nucleotides in multiloop ring"
        self.author_ = "Eli Fisker"
        self.url_ = "http://getsatisfaction.com/eternagame/topics/_strategy_market_no_blue_nucleotides_in_multiloop_ring"
        self.default_params_ = [1, 0.05, 0]
        self.code_length_ = 10
        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive_ = False
        
    def score(self, design, params):            
        
        totalscore = 0
        states = range(1, 3)
        for n in states:

            elements = design['state' + str(n)]['default']['secstruct_elements']
            sequence = design['sequence']
            
            score = 100
            for ii in range(0,len(elements)):                                                                                               
                elem = elements[ii]
                if(elem.type_ == RNAELEMENT_LOOP):
                    loop_groups = elem.get_loop_groups()
                    if(len(loop_groups) > 2 or (len(loop_groups) == 2 and elem.parent_ == False)):
                        for kk in range(0,len(loop_groups)):
                            for mm in range(0,len(loop_groups[kk])):
                                if(sequence[loop_groups[kk][mm]]=='U'):
                                    score -= params[0]
                                                           
            totalscore += score

        totalscore = float(totalscore) / len(states)
        return (totalscore * params[1]) + params[2]
















