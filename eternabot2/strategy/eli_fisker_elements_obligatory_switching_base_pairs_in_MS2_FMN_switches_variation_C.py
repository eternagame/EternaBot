import switch_utils
import strategy_template


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the strategy submission
        # Note: This strategy is variation C by Omei of Eli's original strategy
        self.title_ = ("[Strategy Market] [Switch]"
                       "Elements: Obligatory switching base pairs in"
                       "MS2 FMN switches varC")

        self.author_ = "Eli Fisker"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch-obligatory-switching-base-pairs"
                     "-in-ms2-fmn-switches")

        # Default strategy parameters
        self.default_params_ = [10, 12, 2.0, 1.0, -1.0, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 23

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def score(self, design, params):

        score = 100
        seqlength = len(design['sequence'])
        seq_range = range(0, seqlength)

        switchbp = 0

        for n in range(1, 3):  # [1, 2]
            state = 'state' + str(n)
            otherstate = str((n % 2) + 1)
            for i in seq_range:

                if (design[state]['default']['secstruct'][i] !=
                        design['state' + otherstate]['default']['secstruct'][i] or
                        design[state]['default']['pairmap'][i] !=
                        design['state' + otherstate]['default']['pairmap'][i]):
                    switchbp += 1

        switchbp = float(switchbp) / 2

        if (design['type'] == "miRNA"):
            return switch_utils.UNSCORABLE
        elif switchbp <= params[0]:
            score += params[2]
        elif switchbp <= params[1]:
            score += params[3]
        elif switchbp > params[1]:
            score += ((switchbp - params[1]) * params[4])

        return (params[5] * score) + params[6]
