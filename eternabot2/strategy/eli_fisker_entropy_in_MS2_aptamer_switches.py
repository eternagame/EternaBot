import switch_utils
import strategy_template
from math import log, pow


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the strategy submission
        self.title_ = ("[Strategy Market] [Switch]"
                       "Entropy in MS2 aptamer switches")
        self.author_ = "Eli Fisker"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch-entropy-in-ms2-aptamer-switches")

        # Default strategy parameters
        # First row: turnoff switches,
        # Second row: turnon switches,
        # Third row: general switches
        self.default_params_ = [1, 1.4, 1.5, 2, 2, 3,
                                1, 1.4, 1.5, 2, 3, 2,
                                0.9, 2.1, 3.0, 3.0, -2, 1, 0, 2, 1, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 34

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def score(self, design, params):

        score = 100

        if design['type'] == "miRNA":
            return switch_utils.UNSCORABLE
        else:

            # Calculate positional entropies
            # Positional entropies are computed from the pair probabilities as
            # "S(i) = - Sum_i p(ij) log(p(ij))".

            states = [1, 2]

            for n in range(0, len(states)):

                entropy = [0] * len(design['sequence'])

                dotplot = design['state' + str(states[n])]['default']['dotplotU']
                for i in range(0, len(dotplot)):
                    prob = dotplot[i][2]
                    if prob > 0:
                        prob = float(prob) * log(prob)
                    else:
                        prob = 0
                    entropy[dotplot[i][0]] += prob
                    entropy[dotplot[i][1]] += prob

                maxe = -100

                for i in range(0, len(entropy)):
                    if entropy[i] > maxe:
                        maxe = entropy[i]

                amount = -1

                # Turn on labs
                if("Same State" in design['puztitle']):
                    amount = 0

                # Turn off labs
                elif("Exclusion" in design['puztitle']):
                    amount = 6

                if amount != -1:

                    if params[0 + amount] < maxe < params[1 + amount]:
                        score += params[4 + amount]
                    elif params[2 + amount] < maxe < params[3 + amount]:
                        score += params[5 + amount]

                if maxe < params[12]:
                    score += params[16]
                elif params[13] < maxe < params[14]:
                    # Linear score of reward from +1 to 0 if closer to 2.1 then 3
                    score += ((maxe - params[13]) * (params[17] - params[18]))
                elif maxe > params[15]:
                    # Exponential penalty of A * (B^(entropy above 3))
                    # B = 2, A = 1 (default)
                    score += params[20] * pow(abs(params[19]), (maxe - params[15]))

        return (params[21] * score) + params[22]
