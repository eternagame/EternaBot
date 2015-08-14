import strategy_template
import switch_utils


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the submission
        self.title_ = "[Strategy Market][Switch] few kinks in both states"
        self.author_ = "JR"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch-strategy")

        # Default strategy parameters

        # params organization:
        # penalty for each kink
        self.default_params_ = [-1.0, 0.05, 0]

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
        states = range(1, 3)  # [1, 2]

        for n in states:
            elems = design['state' + str(n)]['default']['secstruct_elements']
            for elem in elems:
                if (elem.type_ == switch_utils.RNAELEMENT_LOOP and
                        elem.score_ > 0):

                    ind = sorted(elem.indices_)
                    count = 1
                    for i in range(1, len(ind)):
                        if ind[i] - ind[i - 1] > 1:
                            count += 1

                    if count == 1:
                        elem1 = self.findRNAElement(
                            switch_utils.RNAELEMENT_STACK,
                            ind[0] - 1,
                            elems
                        )
                        elem2 = self.findRNAElement(
                            switch_utils.RNAELEMENT_STACK,
                            ind[len(ind) - 1] + 1,
                            elems
                        )

                        # Determine if the 2 neighboring stacks are distinct or
                        # the same, if distinct then this is a kink and penalty
                        if (elem1 is not None and elem2 is not None and
                                elem1.indices_[0] not in elem2.indices_):
                            score += params[0]

        return (params[1] * score) + params[2]
