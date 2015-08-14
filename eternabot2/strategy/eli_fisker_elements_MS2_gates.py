import switch_utils
import strategy_template
from math import pow


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the strategy submission
        self.title_ = "[Strategy Market] [Switch] Elements: MS2 Gates"
        self.author_ = "Eli Fisker"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch-elements-ms2-gates")

        # Default strategy parameters
        self.default_params_ = [2, 3.0, -1.0, 1.0, 4, -1.0, 2,
                                3.0, 5, -1.0, 6, 9, 3.0, -1.0, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 37

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def score(self, design, params):

        score = 100

        MS2consensus = "ACAUGAGGAUCACCCAUGU"
        minpos = design['sequence'].find(MS2consensus)
        maxpos = minpos + len(MS2consensus)
        states = [1, 2]
        for state in states:

            for elem in design['state' + str(state)]['default']['secstruct_elements']:
                minind = min(elem.indices_)
                maxind = max(elem.indices_)
                if minind < minpos and maxpos < maxind:
                    length = len(elem.indices_)

                    # Turn off labs
                    if("Same State" not in design['puztitle']):
                        if (elem.type_ == switch_utils.RNAELEMENT_STACK and
                                length >= params[0]):
                            score += ((params[2] * (length - params[0])) +
                                      params[1])
                        elif elem.type_ == switch_utils.RNAELEMENT_LOOP:
                            score += params[3]

                    # Turn on labs
                    elif("Exclusion" in design['puztitle'] and
                            elem.type_ == switch_utils.RNAELEMENT_STACK):
                        if (abs(minpos - minind) <= params[4] and
                                abs(maxpos - maxind) <= params[4]):
                            score += params[5] * pow(params[6], length)

                    # miRNA lab
                    elif (design['type'] == "miRNA" and
                            elem.type_ == switch_utils.RNAELEMENT_STACK):
                        # miRNA - turn on
                        if "turn-off" not in design['puztitle']:
                            score += ((abs(length - params[8]) * params[9]) +
                                      params[7])

                        # miRNA - turn off
                        else:
                            if length > params[11]:
                                score += ((length - params[11]) * params[13] +
                                          params[12])
                            elif length < params[10]:
                                score += ((length - params[10]) * params[13] +
                                          params[12])
                            else:
                                score += params[12]

        return (params[14] * score) + params[15]
