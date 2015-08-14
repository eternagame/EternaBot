import switch_utils
import strategy_template
from math import log, pow


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the strategy submission
        self.title_ = ("[Strategy Market] [Switch]"
                       "Entropy in MS2 microRNA designs")
        self.author_ = "Eli Fisker"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch-entropy-in-ms2-microrna-designs")

        # Default strategy parameters
        # First numbers are thresholds: 0.6, 0.6-0.8, 0.9-1.5, 1.6
        # Next numbers are penalties/awards: exponents have an extra parameter
        # Eg: -1 * 2^X, +1, +3, -1*(2^x) + 2
        self.default_params_ = [.6, .6, .8, .9, 1.5, 1.6,
                                -1, 2, 1, 3, -1, 2, 2, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 27

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def score(self, design, params):

        score = 100

        if design['type'] != "miRNA":
            return switch_utils.UNSCORABLE
        else:

            # Calculate positional entropies
            # Positional entropies are computed from the pair probabilities as
            # "S(i) = - Sum_i p(ij) log(p(ij))".

            states = [1, 2]

            for n in range(0, len(states)):

                entropy = [0] * (len(design['sequence']) + len(design['oligoseq']))

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

                if maxe < params[0]:
                    score += params[6] * pow(abs(params[7]), params[0] - maxe)
                elif params[1] <= maxe <= params[2]:
                    score += params[8]
                elif params[3] <= maxe <= params[4]:
                    score += params[9]
                elif maxe >= params[5]:
                    score += ((params[10] *
                               pow(abs(params[11]), maxe - params[5])) + params[12])

        return (params[13] * score) + params[14]
