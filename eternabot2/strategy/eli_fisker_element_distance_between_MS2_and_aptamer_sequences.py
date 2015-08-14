import switch_utils
import strategy_template


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the strategy submission
        self.title_ = ("[Strategy Market] [Switch]"
                       "Element: Distance between MS2 and aptamer sequences")
        self.author_ = "Eli Fisker"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch"
                     "-element-distance-between-ms2-and-aptamer-sequences")

        # Default strategy parameters
        self.default_params_ = [11, 6, 11, 5, 6, 6, 11, 3,
                                -1.0, -1.0, -1.0, 1.0, 1.0, 1.0, 3.0, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 30

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def score(self, design, params):

        score = 100

        if design['type'] == "miRNA":
            return switch_utils.UNSCORABLE
        else:
            MS2consensus = "ACAUGAGGAUCACCCAUGU"
            MS2start = design['sequence'].find(MS2consensus)
            MS2end = MS2start + len(MS2consensus)
            apstart = min(design['site'])
            apend = max(design['site'])
            dists = [abs(MS2start - apstart), abs(apend - MS2end)]
            mindist = min(dists)

            # turn on
            if "turn-off" not in design['puztitle']:

                # penalize when outside 6->11 for both inside and outside
                for dist in dists:
                    if dist > params[0]:
                        score += params[8]
                    if dist < params[1]:
                        score += params[9]

                # in between
                if MS2start > apstart and MS2end < apend:
                    if mindist <= params[2]:
                        score += params[11]
                    if params[3] <= mindist <= params[4]:
                        score += params[12]

                # outside
                else:
                    if params[5] <= mindist <= params[6]:
                        score += (params[13]) * (mindist - (params[5]-1))

            # turn off
            else:
                if mindist <= params[7]:
                    score += params[14]
                score += params[10] * (mindist)

        return (params[15] * score) + params[16]
