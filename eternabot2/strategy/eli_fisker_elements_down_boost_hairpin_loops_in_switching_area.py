import switch_utils
import strategy_template


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the strategy submission
        self.title_ = ("[Strategy Market] [Switch]"
                       "Elements: Down boost hairpin loops in switching area")
        self.author_ = "Eli Fisker"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch"
                     "-elements-down-boost-hairpin-loops-in-switching-area")

        # Default strategy parameters
        self.default_params_ = [0.5, -1.0, 5, 0.5, 2.0, 1, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 28

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def score(self, design, params):

        score = 100
        states = [1, 2]

        for state in states:
            otherstate = (state % 2) + 1

            elems = design['state' + str(state)]['default']['secstruct_elements']
            for elem in elems:
                if elem.type_ == switch_utils.RNAELEMENT_LOOP:
                    hairpin = True
                    switching = False
                    upboosts = 0
                    for i in range(0, len(elem.indices_)):
                        if (design['state' + str(state)]['default']['secstruct'][i] !=
                                design['state' + str(otherstate)]['default']['secstruct'][i]):
                            switching = True
                        if (i > 0 and
                                elem.indices_[i] - elem.indices_[i-1] != 1):
                            hairpin = False
                        if design['sequence'][i] == 'U':
                            upboosts += 1
                    if hairpin and switching:
                        energy = elem.score_
                        if energy < params[0]:
                            score += params[1]
                        if len(elem.indices_) >= params[2]:
                            score += (params[4] * (energy - params[3]))
                        if len(elem.indices_) < params[2]:
                            score += (upboosts * params[5])
        return (params[6] * score) + params[7]
