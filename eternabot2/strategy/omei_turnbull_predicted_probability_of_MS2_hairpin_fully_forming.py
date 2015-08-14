import strategy_template


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the strategy submission
        self.title_ = ("[Strategy Market][Switch]"
                       "Predicted probability of MS2 hairpin fully forming")
        self.author_ = "Omei Turnbull"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch"
                     "-predicted-probability-of-ms2-hairpin-fully-forming")

        # Default strategy parameters
        # 4 thresholds - physical sense range:[0, 1), 4 penalties (-1 default)
        # Order: ON/MS2, ON/miRNA, OFF/MS2, OFF/miRNA
        self.default_params_ = [0.5, 0.5, 0.5, 0.5, -1.0, -1.0, -1.0, -1.0, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 30

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def score(self, design, params):

        MS2consensus = "ACAUGAGGAUCACCCAUGU"
        score = 100

        start = design['sequence'].find(MS2consensus)
        stop = start + len(MS2consensus)

        probs = [-100, -100]
        states = range(1, 3)  # takes integers from [1, 3) = 1, 2

        for state in states:
            dotplot = design['state' + str(state)]['default']['dotplotU']
            for i in range(0, len(dotplot)):

                i_index = dotplot[i][0]
                j_index = dotplot[i][1]
                if i_index == start and j_index == stop:
                    probs[state-1] = dotplot[i][2]

            if(state == design['on_state'] and
                    design['type'] == "FMN" and
                    probs[state-1] < params[0]):
                score += (params[4])
            elif(state == design['on_state'] and
                    design['type'] == "miRNA" and
                    probs[state-1] < params[1]):
                score += (params[5])
            elif(state == design['off_state'] and
                    design['type'] == "FMN" and
                    probs[state-1] < params[2]):
                score += (params[6])
            elif(state == design['off_state'] and
                    design['type'] == "miRNA" and
                    probs[state-1] < params[3]):
                score += (params[7])

        return (params[8] * score) + params[9]
