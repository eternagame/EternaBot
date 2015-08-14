import strategy_template
import switch_utils


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the submission
        self.title_ = ("[Strategy Market][Switch] "
                       "molecule is partially free in state 1")
        self.author_ = "JR"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch-strategy")

        # Default strategy parameters

        # params organization:
        # first is threshold for energy (how well bound), second is penalty
        self.default_params_ = [-1.0, -1.0, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 21

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

        bases = design['site']
        loop = None

        for base in bases:
            elem = self.findRNAElement(
                switch_utils.RNAELEMENT_LOOP,
                base,
                design['state' + str(design['on_state'])]['default']['secstruct_elements']
            )
            if elem is not None:
                loop = elem
                break

        if design['type'] == "miRNA" or loop is None:
            return switch_utils.UNSCORABLE
        elif loop.score_ < params[0]:
            score += (params[0] - loop.score_) * params[1]

        return (params[2] * score) + params[3]
