import switch_utils
import strategy_template


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the strategy submission
        self.title_ = ("[Strategy Market] [Switch]"
                       "Elements: How to turn off MS2")
        self.author_ = "Eli Fisker"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch-elements-how-to-turn-off-ms2")

        # Default strategy parameters
        self.default_params_ = [3, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 100

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def getBases(self, seq, start, length):
        bases = []
        for i in range(start, start + length):
            if i < len(seq):
                bases.append(seq[i])
        return bases

    def canPair(self, b1, b2):
        return ((b1 == 'G' and (b2 == 'U' or b2 == 'C')) or
                (b1 == 'U' and (b2 == 'A' or b2 == 'G')) or
                (b1 == 'A' and (b2 == 'U')) or
                (b1 == 'C' and (b2 == 'G')))

    def score(self, design, params):

        score = 100
        MS2consensus = "ACAUGAGGAUCACCCAUGU"
        MS2start = design['sequence'].find(MS2consensus)
        MS2end = MS2start + len(MS2consensus)

        if (design['type'] == "miRNA"):
            return switch_utils.UNSCORABLE
        else:

            bases = design['site']
            bases.sort()

            FMNindices = [bases[0], -1, -1, bases[len(bases) - 1]]

            for i in range(1, len(bases)):
                if bases[i] - bases[i-1] > 1:
                    if FMNindices[1] == -1:
                        FMNindices[1] = bases[i]
                    else:
                        FMNindices[2] = bases[i]

            # Turn off labs
            if("Exclusion" in design['puztitle']):

                dist = []

                for ind in FMNindices:
                    dist.append(abs(MS2start - ind))
                    dist.append(abs(MS2end - ind))

                dist = min(dist)

                if dist < params[0]:

                    # FMN BEFORE MS2
                    complement = []
                    if (abs(MS2start - FMNindices[0]) == dist or
                            abs(MS2start - FMNindices[3]) == dist):
                        complement = self.getBases(
                                        design['sequence'],
                                        MS2end,
                                        6
                                    )

                    # FMN ATER MS2
                    else:
                        if abs(MS2end - FMNindices[0]) == dist:
                            complement = self.getBases(
                                            design['sequence'],
                                            FMNindices[1],
                                            6
                                        )
                        else:
                            complement = self.getBases(
                                            design['sequence'],
                                            FMNindices[3],
                                            6
                                        )

                    # Check if the next 5 (n-1) are complementary to the MS2
                    compindeces = []
                    complen = 0

                    for i in range(-1, len(MS2consensus) - (len(complement) - 1)):

                        pcompindices = []
                        pcomplen = 0

                        for n in range(1, len(complement)):
                            if self.canPair(MS2consensus[i + n], complement[n]):
                                pcompindices.append(i + n)
                                pcomplen += 1
                            else:
                                pcompindices.append(-1)
                                break

                        if pcomplen > complen:
                            complen = pcomplen
                            compindeces = pcompindices

                    if (compindeces[0] == -1 or
                            (complement[0] == 'G' and
                                MS2consensus[compindeces[0]] == 'U') or
                            (complement[0] == 'U' and
                                MS2consensus[compindeces[0]] == 'G')):
                        score += params[1]

                    countC = countU = 0

                    for i in range(0, len(compindeces)):
                        if i != 0 and compindeces[i] != -1:
                            score += params[2]
                        if complement[i] == "C":
                            countC += 1
                        elif complement[i] == "U":
                            countU += 1

                    # Limit to 2 rewards each
                    if countC > 2:
                        countC = 2
                    if countU > 2:
                        countU = 2

                    score += params[3]*countC + params[4]*countU
            # Turn on labs
            else:
                for state in range(1, 3):  # states 1, 2
                    for base in range(MS2start, MS2end + 1):
                        loc = design['state' + str(state)]['default']['pairmap'][base]
                        if (loc in range(FMNindices[0], FMNindices[1] + 1)):
                            score += params[5]
                        if (loc in range(FMNindices[2], FMNindices[3] + 1)):
                            score += params[6]
                        if (design['sequence'][base] == "C" and loc != -1 and
                                design['sequence'][loc] == "G"):
                            score += params[7]

        return (score * params[8]) + params[9]
