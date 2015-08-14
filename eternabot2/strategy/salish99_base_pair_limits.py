import strategy_template


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the submission
        self.title_ = "[Strategy Market][Switch]Base Pair limits"
        self.author_ = "salish99"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch-base-pair-limits")

        # Default strategy parameters
        # Two copies of params for state 1 and state 2. Organized GU, GC, AU
        # Afterwards is the penalties/awards
        self.default_params_ = [0, 0.1, 0.25,
                                0.2, 0.25, 0.15, 0.35, 0.6,
                                0.12, 0.22, 0.5, 0.08, 0.32, 0.6,
                                -1.0, 1.0, 1.5, 2.0,
                                0, 0.1, 0.25,
                                0.2, 0.25, 0.15, 0.35, 0.6,
                                0.12, 0.22, 0.5, 0.08, 0.32, 0.6,
                                -1.0, 1.0, 1.5, 2.0, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 27

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def score(self, design, params):

        states = ['1', '2']
        extra = [0, 18]

        score = 100

        for i in range(0, len(states)):

            total = (design['state' + states[i]]['default']['gu'] + design['state' + states[i]]['default']['gc'] +
                     design['state' + states[i]]['default']['ua'])
            perGU = float(design['state' + states[i]]['default']['gu']) / total
            perGC = float(design['state' + states[i]]['default']['gc']) / total
            perAU = float(design['state' + states[i]]['default']['ua']) / total

            if perGU > params[2 + extra[i]]:
                score += params[14 + extra[i]]
            if (params[0 + extra[i]] < perGU < params[1 + extra[i]]):
                score += params[16 + extra[i]]

            if perGC > params[7 + extra[i]]:
                score += params[14 + extra[i]]
            if (params[3 + extra[i]] < perGC < params[4 + extra[i]]):
                score += params[17 + extra[i]]
            elif (params[5 + extra[i]] < perGC < params[6 + extra[i]]):
                score += params[15 + extra[i]]

            if perAU > params[13 + extra[i]]:
                score += params[14 + extra[i]]
            if ((params[8 + extra[i]] < perAU < params[9 + extra[i]]) or
                    (perAU == params[10 + extra[i]])):
                score += params[17 + extra[i]]
            elif (params[11 + extra[i]] < perAU < params[12 + extra[i]]):
                score += params[15 + extra[i]]

        return (params[36] * score) + params[37]
