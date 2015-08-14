import strategy_template


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the strategy submission
        self.title_ = ("[Strategy Market][Switch]"
                       "Penalize large amounts of GC pairs")
        self.author_ = "vineetkosaraju"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch"
                     "-penalize-large-amounts-of-gc-pairs")

        # Default strategy parameters
        self.default_params_ = [0.4, 0.2, 0.4, 0.2, 1.0, 1.0, 1.0, 1.0, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 14

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def score(self, design, params):

        perGCstate1 = (float(design['state1']['default']['gc']) /
                       (design['state1']['default']['gu'] + design['state1']['default']['gc'] + design['state1']['default']['ua']))
        perGCstate2 = (float(design['state2']['default']['gc']) /
                       (design['state2']['default']['gu'] + design['state2']['default']['gc'] + design['state2']['default']['ua']))

        score = 100

        if perGCstate1 > params[0]:
            score -= ((perGCstate1 - params[0]) * 100 * params[4])
        elif perGCstate1 < params[1]:
            score -= ((params[1] - perGCstate1) * 100 * params[5])

        if perGCstate2 > params[2]:
            score -= ((perGCstate2 - params[0]) * 100 * params[6])
        elif perGCstate2 < params[3]:
            score -= ((params[1] - perGCstate2) * 100 * params[7])

        return (params[8] * score) + params[9]
