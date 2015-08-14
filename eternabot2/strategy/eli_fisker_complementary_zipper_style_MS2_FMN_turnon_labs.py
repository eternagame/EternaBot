import switch_utils
import strategy_template
import re


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the strategy submission
        self.title_ = ("[Strategy Market] [Switch]"
                       "Complementary Zipper Style - MS2 FMN Turnon labs")
        self.author_ = "Eli Fisker"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch"
                     "-complementary-zipper-style-ms2-fmn-turnon-labs")

        # Default strategy parameters
        self.default_params_ = [1.0, 0, 4, 1.0, 2, 5, 1.0, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 61

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def findRNAElement(self, type, bp, elements):

        for i in range(0, len(elements)):
            if elements[i].type_ == type and bp in elements[i].indices_:
                return elements[i]

        return None

    def getSequence(self, elem, strand, seq):

        if elem.type_ != switch_utils.RNAELEMENT_STACK:
            return None

        sequence = []
        indices = sorted(elem.indices_)  # preserve current order

        for i in range(0, len(indices)):

            if (i > 0 and indices[i] - indices[i - 1] > 1):
                strand = (strand % 2) + 1

            if strand == 1:
                sequence.append(seq[indices[i]])

        return "".join(sequence)

    def score(self, design, params):

        score = 100

        if design['type'] == "miRNA":
            return switch_utils.UNSCORABLE
        else:

            # get aptamer bases
            # find strand1, strand2, strand3, strand4
            # 10,11,12,13,14,15,16,17,35,36,37,38,39,40,41 should become
            # 10, 35

            bases = design['site']
            bases.sort()

            strands = [bases[0], 100]
            for i in range(1, len(bases)):
                if bases[i] - bases[i-1] > 1:
                    strands[1] = bases[i]
                    break

            states = range(1, 3)  # [1, 2]

            # get rnaelements containing strands
            for n in states:
                for i in range(0, len(strands)):
                    elem = self.findRNAElement(
                        switch_utils.RNAELEMENT_STACK,
                        strands[i],
                        design['state' + str(n)]['default']['secstruct_elements']
                    )
                    if elem is not None:

                        strand1 = [m.start() for m in re.finditer(
                            "CAUG",
                            self.getSequence(elem, 1, design['sequence'])
                        )]

                        strand2 = [m.start() for m in re.finditer(
                            "CAUG",
                            self.getSequence(elem, 2, design['sequence'])
                        )]

                        strand1 = sorted(
                            strand1,
                            key=lambda dist: abs(strands[i] - dist)
                        )
                        strand2 = sorted(
                            strand2,
                            key=lambda dist: abs(strands[i] - dist)
                        )

                        if len(strand1) > 0 and len(strand2) > 0:
                            score += params[0]

                            # Ideally we could just use 1 strand, but just in
                            # case average both.
                            dist = float(abs(strand1[0] - strands[i]) +
                                         abs(strand2[0] - strands[i])) / 2

                            # Early aptamer gate
                            if i == 0:
                                if params[1] <= dist <= params[2]:
                                    score += params[3]

                            # Late aptamer gate
                            else:
                                if params[4] <= dist <= params[5]:
                                    score += params[6]

        return (params[7] * score) + params[8]
