import switch_utils
import strategy_template


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the strategy submission
        self.title_ = "[Strategy Market] [Switch] Helix Composition"
        self.author_ = "Brourd"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch-helix-composition")

        # Default strategy parameters
        # Row 1: penalties/awards for active helices
        # Row 2: thresholds for active helices
        # Row 3: penalties for passive helices
        # Row 4: thresholds for passive helices
        self.default_params_ = [1.0, 1.0, -1.0, -2.0, -1.0, -1.0,
                                2, 2, 0, 3, 2, 0, 1, 0, 2,
                                -1.0, -1.0, -1.0,
                                3, 2.0, 7, 0.05, 0.05, 0
                                ]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 81

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def findRNAElement(self, type, bplist, elements):

        for i in range(0, len(elements)):
            if elements[i].type_ != type:
                continue

            match = True
            for n in bplist:
                if n not in elements[i].indices_:
                    match = False
                    break
            if match:
                return elements[i]
        return None

    def calculateBPAmount(self, element, sequence, secstruct, pmap):

        bpGC = bpGU = bpAU = 0

        # Theoretically, numBP = bpGC + bpGU + bpAU
        numBP = float(len(element.indices_)) / 2

        for i in element.indices_:
            # Avoid double counting by only looking forwards at "(" basepairs
            if secstruct[i] != '(':
                continue
            if ((sequence[i] == 'G' and sequence[pmap[i]] == 'C') or
                    (sequence[i] == 'C' and sequence[pmap[i]] == 'G')):
                bpGC += 1
            if ((sequence[i] == 'G' and sequence[pmap[i]] == 'U') or
                    (sequence[i] == 'U' and sequence[pmap[i]] == 'G')):
                bpGU += 1
            if ((sequence[i] == 'A' and sequence[pmap[i]] == 'U') or
                    (sequence[i] == 'U' and sequence[pmap[i]] == 'A')):
                bpAU += 1

        return (bpGC, bpGU, bpAU, numBP)

    def score(self, design, params):

        score = 100

        for n in range(1, 3):

            actives = []
            passives = []
            otherstate = (n % 2) + 1
            state = 'state' + str(n)

            elems = design[state]['default']['secstruct_elements']

            for i in range(0, len(elems)):

                if elems[i].type_ != switch_utils.RNAELEMENT_STACK:
                    continue

                rnaelem = self.findRNAElement(
                    switch_utils.RNAELEMENT_STACK,
                    elems[i].indices_,
                    design['state' + str(otherstate)]['default']['secstruct_elements']
                )
                if rnaelem is not None:
                    passives.append(elems[i])
                else:
                    actives.append(elems[i])

            for i in range(0, len(actives)):
                bpGC, bpGU, bpAU, numBP = self.calculateBPAmount(
                    actives[i],
                    design['sequence'],
                    design[state]['default']['secstruct'],
                    design[state]['default']['pairmap']
                )

                if bpGC == params[6]:
                    score += params[0]
                elif bpGC > params[7] and bpGU == params[8]:
                    score += params[1] * (bpGC - params[7])
                elif ((bpGC > params[9] and bpGU <= params[10]) or
                        (bpGC <= params[9] and bpGU > params[10])):
                    score += params[2]

                elif bpGC == params[11]:
                    score += params[3]
                elif bpGC == params[12] and bpGU > params[13]:
                    score += params[4]

                if numBP <= params[14]:
                    score += params[5]

            for i in range(0, len(passives)):
                bpGC, bpGU, bpAU, numBP = self.calculateBPAmount(
                    passives[i],
                    design['sequence'],
                    design[state]['default']['secstruct'],
                    design[state]['default']['pairmap']
                )

                if numBP <= params[18]:
                    score += params[15]

                if bpGC <= (float(numBP) / params[19]) and numBP < params[20]:
                    score += params[16]

                for j in range(0, len(design[state]['default']['dotplotU'])):
                    dot = design[state]['default']['dotplotU'][j]
                    if (dot[0] in passives[i].indices_ or
                            dot[1] in passives[i].indices_ and
                            dot[2] <= params[21]):
                        # Alternative pairing
                        score += params[17]

        return (params[22] * score) + params[23]
