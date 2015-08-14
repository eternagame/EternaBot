import switch_utils
import strategy_template
from math import log, pow


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the strategy submission
        self.title_ = ("[Strategy Market] [Switch]"
                       "Entropy in static area in partial switch")
        self.author_ = "Eli Fisker"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch"
                     "-entropy-in-static-area-in-partial-switch")

        # Default strategy parameters
        # First four are thresholds (< 0.7, 0.8-0.9, > 1.0)
        # Next three are awards (+2, +1) and penalty (-1)
        # Last is the exponential penalty, defined as 2^(entropy - 1)
        # 2 was chosen randomly but it should optimize to a good point
        self.default_params_ = [0.7, 0.8, 0.9, 1.0, 2.0, 1.0, -1.0, 2.0, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 39

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def score(self, design, params):

        score = 100

        # NEW: To determine if a switch is partial moving or full moving,
        # look at the entire switch. If 50% of all bases move then it is
        # only partially moving. Otherwise, it is fully moving.

        # OLD: To determine if a switch is partial moving or full moving,
        # look at the aptamer binding spots. If 50% of them or less
        # move (one stack) then it is only partially moving. Otherwise,
        # it is fully moving.

        # What the bases binding occured in were, and which state (1 or 2)
        # the binding occured in.
        # bases = design['site']
        bases = range(0, len(design['sequence']))
        state = str(design['on_state'])

        switchbp = 0
        nonswitches = []

        for base in bases:

            if design['state' + state]['default']['secstruct'][base] == '(':
                pair1 = design['sequence'][design['state1']['default']['pairmap'][base]]
                pair2 = design['sequence'][design['state2']['default']['pairmap'][base]]
                if pair1 != pair2:
                    switchbp += 1
                else:
                    nonswitches.append(base)

        if float(switchbp) / len(bases) <= 0.5:
            # Partial switch - calculate positional entropies
            # Positional entropies are computed from the pair probabilities as
            # "S(i) = - Sum_i p(ij) log(p(ij))".

            states = [1, 2]
            entropies = []

            for n in range(0, len(states)):

                if design['type'] != "miRNA":
                    entropy = [0] * len(design['sequence'])
                else:
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

                entropies.append(entropy)

                for base in range(0, len(nonswitches)):
                    ent = entropies[n][base]
                    if ent < params[0]:
                        score += params[4]
                    elif params[1] <= ent <= params[2]:
                        score += params[5]
                    elif params[3] < ent:
                        score += params[6] * pow(params[7], ent - params[3])

        else:
            return switch_utils.UNSCORABLE

        return (params[8] * score) + params[9]
