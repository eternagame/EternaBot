import switch_utils
import strategy_template
from math import pow


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the strategy submission
        self.title_ = ("[Strategy Market] [Switch] "
                       "Complementary word change game - MicroRNA Turn on lab")
        self.author_ = "Eli Fisker"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch-"
                     "complementary-word-change-game-microrna-turn-on-lab")

        # Default strategy parameters
        self.default_params_ = [3, 0, 0, 0, 2, 0, 0, 1, 0, 0, 3, -0.5, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 46

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def canPair(self, b1, b2):
        return ((b1 == 'G' and (b2 == 'U' or b2 == 'C')) or
                (b1 == 'U' and (b2 == 'A' or b2 == 'G')) or
                (b1 == 'A' and (b2 == 'U')) or
                (b1 == 'C' and (b2 == 'G')))

    def weakPair(self, b1, b2):
        return b1 == 'G' and b2 == 'U' or b1 == 'U' and b2 == 'G'

    def checkBounds(self, seq, indices):
        for i in indices:
            if i < 0 or i >= len(seq):
                return None
        return indices

    def giveReward(self, seq1, strech1, seq2, strech2,
                   strongReward, normalReward, weakReward,
                   ignoreFirst=False, ignoreLast=False):
        if strech1 is None or strech2 is None or len(strech1) != len(strech2):
            return 0

        reward = 0
        length = len(strech1)

        for i in range(0, length):
            if (i == 0 and ignoreFirst) or (i == length - 1 and ignoreLast):
                continue
            if self.canPair(seq1[strech1[i]], seq2[strech2[i]]):
                reward += normalReward
            if self.weakPair(seq1[strech1[i]], seq2[strech2[i]]):
                reward += weakReward
            else:
                reward += strongReward

        return reward

    def score(self, design, params):

        score = 100

        if design['type'] != "miRNA":
            return switch_utils.UNSCORABLE
        else:
            seq = design['sequence']
            oligo = design['oligoseq']
            MS2 = "ACAUGAGGAUCACCCAUGU"
            loc = design['sequence'].find(MS2)
            ind = loc + len(MS2)

            s1 = self.checkBounds(seq, range(loc, loc + 6))
            s2 = self.checkBounds(seq, range(ind, ind + 6))
            s3 = self.checkBounds(seq, range(loc - 6, loc))
            s4 = self.checkBounds(seq, range(ind + 6, ind + 12))
            s5 = self.checkBounds(oligo, range(0, 6))

            score += self.giveReward(seq, s2, seq, s1,
                            params[0], params[1], params[2])
            score += self.giveReward(seq, s2, seq, s3,
                            params[3], params[4], params[5], True)
            score += self.giveReward(seq, s4, seq, s3,
                            params[6], params[7], params[8], False, True)
            score += self.giveReward(seq, s4, oligo, s5,
                            params[9], params[10], params[11])

        return (params[12] * score) + params[13]
