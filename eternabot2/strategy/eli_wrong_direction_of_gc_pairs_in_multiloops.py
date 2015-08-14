from switch_utils import *
import strategy_template


class Strategy(strategy_template.Strategy):
    def __init__(self):
        strategy_template.Strategy.__init__(self)
        
        self.title_ = "Wrong Direction of GC-pairs in multiloops"
        self.author_ = "Eli Fisker"
        self.url_ = "http://getsatisfaction.com/eternagame/topics/_strategy_market_wrong_direction_of_gc_pairs_in_multiloops"
        self.default_params_ = [-1, 0.05, 0] # Amount to deduct per penalty
        self.code_length_ = 20
        self.publishable_ = True

    def score(self, design, params):

        totalscore = 100
        states = range(1, 3)

        for state in states:
            n = 'state' + str(state)
            elements = design[n]['default']['secstruct_elements']
            
            penalty = 0
            multiloop_found = False
            
            for element in elements:
                if (element.type_ != RNAELEMENT_LOOP): continue
                closing_pairs = element.get_loop_closing_pairs(design['sequence'],design[n]['default']['pairmap'])
                if len(closing_pairs) < 3: continue
                multiloop_found = True
                for index, pair in enumerate(closing_pairs):
                    if index == 0:
                        if pair == "GC": continue
                        elif pair == "CG": penalty += 1
                        else:
                            penalty += 2
                    else:
                        if pair == "CG": continue
                        elif pair == "GC": penalty +=1
                        else:
                            penalty += 2
                            
            if not multiloop_found: return UNSCORABLE
            score = 100 + params[0] * penalty
            totalscore += score

        totalscore = float(totalscore) / len(states)
        return (totalscore * params[1]) + params[2]
