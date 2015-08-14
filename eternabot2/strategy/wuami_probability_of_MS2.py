import strategy_template


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the strategy submission
        self.title_ = ("[Strategy Market][Switch]"
                       "Probability of MS2")
        self.author_ = "wuami"

        # URL where the strategy was initially submitted
        self.url_ = ("N/A")

        # Default strategy parameters
        self.default_params_ = [100, 1]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 12

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def score(self, design, params):

        MS2consensus = "ACAUGAGGAUCACCCAUGU"
        score = 100

        # Only look at closing base pair
        start = design['sequence'].index(MS2consensus)

        on_prob = -1
        off_prob = -1

        for dot in design['state' + str(design['on_state'])]['default']['dotplotU']:
            if dot[0] == start:
                on_prob = dot[2]

        for dot in design['state' + str(design['off_state'])]['default']['dotplotU']:
            if dot[0] == start:
                off_prob = dot[2]

        return (params[1] - (float(off_prob) / on_prob)) * params[0]
