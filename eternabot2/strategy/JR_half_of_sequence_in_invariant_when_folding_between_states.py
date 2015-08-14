import strategy_template
import switch_utils


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the submission
        self.title_ = ("[Strategy Market][Switch] "
                       "half of sequence in invariant when "
                       "folding between states")
        self.author_ = "JR"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch-strategy")

        # Default strategy parameters

        # params organization:
        self.default_params_ = [0.3, 0.5, 1.0, 0.7, 1.0, -1.0, 1, -2.0, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 29

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def score(self, design, params):

        score = 100
        seqlen = len(design['sequence'])
        change = 0
        states = range(1, 3)

        for i in range(0, seqlen):

            if design['state1']['default']['pairmap'][i] != design['state2']['default']['pairmap'][i]:
                change += 1

        change = float(change) / seqlen

        if params[0] < change < params[1]:
            score += params[2]
        elif params[3] < change < params[4]:
            score += params[5]

        # Determine twists and turns
        for n in states:
            elems = design['state' + str(n)]['default']['secstruct_elements']
            for elem in elems:
                if elem.type_ == switch_utils.RNAELEMENT_LOOP:
                    # Find loop strands
                    ind = sorted(elem.indices_)
                    seg = []
                    strand = [ind[0]]
                    for i in range(1, len(ind)):
                        if ind[i] - ind[i - 1] > 1:
                            seg.append(strand)
                            strand = []
                        strand.append(ind[i])
                    seg.append(strand)

                    # Twists
                    if (len(seg) == 2 and abs(len(seg[1]) - len(seg[0])) >
                            params[6]):
                        score += params[7]

        return (params[8] * score) + params[9]
