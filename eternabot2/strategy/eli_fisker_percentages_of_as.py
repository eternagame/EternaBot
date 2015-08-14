import strategy_template


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of submission
        self.title_ = "[Strategy Market] [Switch] Percentages of A's."
        self.author_ = "Eli Fisker"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch-percentages-of-a-s")

        # Default strategy parameters
        self.default_params_ = [0.29, 0.35, 0.31, 0.33, 1, 2, 1.0, 1.0, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 11

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def score(self, design, params):

        perA = float(design['sequence'].count('A')) / len(design['sequence'])

        score = 100
        if params[0] < perA < params[1]:
            score += params[4]
        if params[2] < perA < params[3]:
            score += params[5]
        if perA > params[1]:
            score -= ((perA - params[1])*100*params[6])
        if perA < params[0]:
            score -= ((params[0] - perA)*100*params[7])

        return (params[8] * score) + params[9]
