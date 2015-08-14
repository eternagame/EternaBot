from switch_utils import *
import strategy_template


class Strategy(strategy_template.Strategy):
    def __init__(self):
        strategy_template.Strategy.__init__(self)

        self.title_ = "Tetraloop Pattern"
        self.author_ = "Ding"
        self.url_ = "http://getsatisfaction.com/eternagame/topics/tell_us_about_your_eterna_lab_algorithms"
        self.default_params_ = [-5, 0.05, 0]
        self.code_length_ = 0
        self.publishable_ = False
        self.is_part_of_ensemble_ = False
        self.optimized_ = False

    def score(self, design, params):

        totalscore = 0
        states = range(1, 3)
        for state in states:
            n = 'state' + str(state)

            score = 100
            sequence = design['sequence']
            elements = design[n]['default']['secstruct_elements']

            for element in elements:
                if (element.type_ != RNAELEMENT_LOOP): continue
                if (len(element.get_loop_closing_pairs(design['sequence'], design[n]['default']['pairmap'])) == 1) and (len(element.indices_) == 4):
                    tetraloop_string = "{0}{1}{2}{3}".format(sequence[element.indices_[0]], sequence[element.indices_[1]], sequence[element.indices_[2]], sequence[element.indices_[3]])
                    if tetraloop_string != "AAAA":
                        score += params[0]

        totalscore = float(totalscore)/len(states)
        return (totalscore * params[1]) + params[2]
