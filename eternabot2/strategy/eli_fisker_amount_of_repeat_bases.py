import switch_utils
import strategy_template


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the strategy submission
        self.title_ = "[Strategy Market] [Switch] Amount of repeat bases"
        self.author_ = "Eli Fisker"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch-amount-of-repeat-bases"
                     )

        # Default strategy parameters
        # Row 1 is turn on labs, row 2 is turn off labs
        # row 3 is awards/penalties for turn on labs
        # row 4 is awards/penalties for turn off labs
        self.default_params_ = [.40, .50, .35, .39, .51, .55, 0, .35, .55, 1,
                                .30, .40, .25, .29, .40, .50, 0, .25, .45, 1,
                                2.0, 1.0, -1.0,
                                2.0, 1.0, -1.0,
                                0.05, 0
                                ]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 35

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def score(self, design, params):

        percentrepeats = 0
        score = 100

        seq = design['sequence']
        seqlength = len(seq)
        seq_range = range(0, seqlength)

        for i in seq_range:
            if ((i > 0 and seq[i] == seq[i-1]) or
                    (i < seqlength - 1 and seq[i] == seq[i + 1])):
                percentrepeats += 1

        # convert from a count to a percentage
        percentrepeats = (float(percentrepeats) / seqlength)

        # Turn on labs
        if("Same State" in design['puztitle']):
            if (params[0] < percentrepeats < params[1]):
                score += params[20]
            if (params[2] < percentrepeats < params[3]):
                score += params[21]
            if (params[4] < percentrepeats < params[5]):
                score += params[21]
            if (params[6] <= percentrepeats < params[7]):
                score += params[22]
            if (params[8] < percentrepeats <= params[9]):
                score += params[22]

        # Turn off labs
        elif("Exclusion" in design['puztitle']):
            if (params[10] < percentrepeats < params[11]):
                score += params[23]
            if (params[12] < percentrepeats < params[13]):
                score += params[24]
            if (params[14] < percentrepeats < params[15]):
                score += params[24]
            if (params[16] <= percentrepeats < params[17]):
                score += params[25]
            if (params[18] < percentrepeats <= params[19]):
                score += params[25]

        else:
            return switch_utils.UNSCORABLE

        return (params[26] * score) + params[27]
