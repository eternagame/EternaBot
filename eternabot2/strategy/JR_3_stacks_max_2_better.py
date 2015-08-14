import strategy_template
import switch_utils


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the submission
        self.title_ = "[Strategy Market][Switch] 3 stacks max. , 2 better"
        self.author_ = "JR"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch-strategy")

        # Default strategy parameters

        # params organization:
        self.default_params_ = [3, -1.0, 2, 3, 1.0, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 14

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def score(self, design, params):

        score = 100

        states = range(1, 3)  # [1, 2]

        avgstackcount = 0

        for n in states:
            elems = design['state' + str(n)]['default']['secstruct_elements']
            for elem in elems:
                if elem.type_ == switch_utils.RNAELEMENT_STACK:
                    avgstackcount += 1

        avgstackcount = float(avgstackcount) / len(states)

        if avgstackcount > params[0]:
            score += params[1]
        elif params[2] <= avgstackcount < params[3]:
            score += (params[3] - avgstackcount) * params[4]

        return (params[5] * score) + params[6]
