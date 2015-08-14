import switch_utils
import strategy_template


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the strategy submission
        self.title_ = ("[Strategy Market] [Switch]"
                       "How MicroRNA likes to bind: Turnoff labs")
        self.author_ = "Eli Fisker"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch"
                     "-how-microrna-likes-to-bind-turnoff-labs")

        # Default strategy parameters
        self.default_params_ = [18, 19, 3, -1, -0.5, -1,
                                -1, 1, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 54

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def canPair(self, b1, b2):
        return ((b1 == 'G' and (b2 == 'U' or b2 == 'C')) or
                (b1 == 'U' and (b2 == 'A' or b2 == 'G')) or
                (b1 == 'A' and (b2 == 'U')) or
                (b1 == 'C' and (b2 == 'G')))

    def weakPair(self, i, comp, miRNA, seq):
        if comp[i] == -1:
            return False
        return ((miRNA[i] == 'G' and seq[comp[i]] == 'U') or
                (miRNA[i] == 'U' and seq[comp[i]] == 'G'))

    def score(self, design, params):

        score = 100

        # Turn off labs
        if design['type'] == "miRNA" and "turn-off" in design['puztitle']:

            # get miRNA bases
            miRNA = design['oligoseq']
            seq = design['sequence']

            # find longest complementary strand in the RNA design
            # complement: each pos has an index 'i', if i == -1 then no pair
            # if i != -1 then complement[pos] pairs with seq[i]

            # Note that len(complement) is not the same as complen
            # complement has bases that are paired and unpaired and its
            # len(complement) will always be the same as the length of miRNA
            # whereas complen is the number of paired bases (the number of
            # complements)
            complement = []
            complen = -1

            for i in range(0, len(seq) - len(miRNA) + 1):

                pcomp = []
                pcomplen = 0

                for n in range(0, len(miRNA)):
                    base1 = seq[i + n]
                    base2 = miRNA[n]
                    if self.canPair(base1, base2):
                        pcomp.append(i+n)
                        pcomplen += 1
                    else:
                        pcomp.append(-1)

                if pcomplen > complen:
                    complement = pcomp
                    complen = pcomplen

            # if strand.length = 18-19 give +3
            # if strand.length < 18, give (-1)*(18 - strand.length)
            # if strand.lengh > 19, give (-1)*(strand.length - 19)
            if params[0] <= complen <= params[1]:
                score += params[2]
            elif complen < params[0]:
                score += params[3] * (params[0] - complen)
            elif complen > params[1]:
                score += params[3] * (complen - params[1])

            # iterate to first 2 miRNA, if G and complement is U, give -0.5
            # iterate to first 2 miRNA, if U and complement is G, give -0.5
            # iterate to last 2 miRNA, if G and complement is U, give -0.5
            # iterate to last 2 miRNA, if U and complement is G, give -0.5

            ends = range(0, 2)
            ends.extend(range(len(complement) - 2, len(complement)))

            for i in ends:
                if self.weakPair(i, complement, miRNA, seq):
                    score += params[4]

            # iterate to remaining miRNA, if G and complement is U, give -1
            # iterate to remaining miRNA, if U and complement is G, give -1
            others = range(2, len(complement) - 2)
            for i in others:
                if self.weakPair(i, complement, miRNA, seq):
                    score += params[5]

            # for each bases 12->14
                # if paired, give -1
            for i in range(12, 14 + 1):
                if complement[i] != -1:
                    score += params[6]

            # for each bases 1-11 and 15-22
                # if paired, give +1

            shouldpairs = range(1, 11 + 1)
            shouldpairs.extend(range(15, 22 + 1))

            for i in shouldpairs:
                if i < len(complement) and complement[i] != -1:
                    score += params[7]

        else:
            return switch_utils.UNSCORABLE

        return (params[8] * score) + params[9]
