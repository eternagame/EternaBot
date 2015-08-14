import switch_utils
import strategy_template


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the strategy submission
        self.title_ = ("[Strategy Market] [Switch]"
                       "Elements: When to make the tails pair")
        self.author_ = "Eli Fisker"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch"
                     "-elements-when-to-make-the-tails-pair")

        # Default strategy parameters
        self.default_params_ = [8, -1.0, 14, -1.0, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 20

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def score(self, design, params):

        score = 100
        danglingCount = 0
        states = [1, 2]

        for n in states:
            ss = design['state' + str(n)]['default']['secstruct']
            for i in range(0, len(ss)):
                if ss[i] == ".":
                    danglingCount += 1
                else:
                    break

            for i in range(len(ss) - 1, -1, -1):
                if ss[i] == ".":
                    danglingCount += 1
                else:
                    break

        if danglingCount > params[0]:
            score += params[1]

        # Yes, it is possible to get both penalties
        if danglingCount > params[2]:
            score += params[3]

        return (params[4] * score) + params[5]
