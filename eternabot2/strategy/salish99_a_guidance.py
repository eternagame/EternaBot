import strategy_template
import re
import switch_utils


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the submission
        self.title_ = "[Strategy Market][Switch]A guidance"
        self.author_ = "salish99"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch-a-guidance")

        # Default strategy parameters

        # params organization:
        self.default_params_ = [0.4, -1, 3, -1.0, 3.0, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 31

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def findRNAElement(self, type, bp, elements):

        for i in range(0, len(elements)):
            if elements[i].type_ == type and bp in elements[i].indices_:
                return elements[i]

        return None

    def score(self, design, params):

        score = 100

        perA = 0
        for i in range(0, len(design['sequence'])):
            if design['sequence'][i] == "A":
                perA += 1

        perA = float(perA) / len(design['sequence'])

        # Limit the number of As by percentage - 40%
        if perA > params[0]:
            score += params[1]

        # count AA (2), AAA (3), AAAA (4), AAAAA(5) occurences and penalize
        for i in range(2, 5 + 1):
            seq = "A" * i
            count = design['sequence'].count(seq)
            if count > params[2]:
                score += (params[3] * (count - params[2]))

        # big bonus to quad(4) A when 1 or more A is in a loop (creates hinge)
        quadlocs = [m.start() for m in re.finditer("AAAA", design['sequence'])]

        # get all RNA elements in both states
        elems = design['state1']['default']['secstruct_elements']
        elems.extend(design['state2']['default']['secstruct_elements'])

        for loc in quadlocs:
            for i in range(loc, loc+4):
                elem = self.findRNAElement(
                    switch_utils.RNAELEMENT_LOOP,
                    i,
                    elems
                )
                if elem is not None:
                    score += params[4]
                    break

        return (params[5] * score) + params[6]
