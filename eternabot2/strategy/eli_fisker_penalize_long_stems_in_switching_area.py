import strategy_template
import switch_utils


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of submission
        self.title_ = ("[Strategy Market] [Switch]"
                       "Penalize long stems in switching area")
        self.author_ = "Eli Fisker"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch"
                     "-penalize-long-stems-in-switching-area")

        # Default strategy parameters
        self.default_params_ = [6, -1.0, 2.0, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 24

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def score(self, design, params):

        score = 100
        sequence = design['sequence']

        elementss = ["state1", "state2"]

        for n in range(0, len(elementss)):
            elements = design[elementss[n]]['default']['secstruct_elements']

            for i in range(0, len(elements)):
                elem = elements[i]
                if(elem.type_ == switch_utils.RNAELEMENT_STACK):
                    stack_len = elem.get_stack_length()
                    if stack_len > params[0]:
                        score += (stack_len - params[0]) * params[1]

                        givereward = True
                        count = 0

                        for j in range(0, stack_len):
                            pair = elem.get_pair_from_stack(j, sequence)
                            count += 1
                            if(pair == "GU" or pair == "UG"):
                                count = 0
                            if count >= params[0]:
                                givereward = False
                                break

                        if givereward:
                            score += params[2]

        return (params[3] * score) + params[4]
