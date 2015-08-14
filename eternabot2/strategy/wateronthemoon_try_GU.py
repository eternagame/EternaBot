import strategy_template
import switch_utils


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the strategy submission
        self.title_ = "[Strategy Market] [Switch]"
        self.author_ = "wateronthemoon"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch-6qj7skjnahh4r")

        # Default strategy parameters
        # First param is the bonus for GU stacks state1 => loops in state2
        # Second param is the bonus for GU stacks state2 => loops in state1
        self.default_params_ = [1.0, 1.0, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 33

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def findRNAElement(self, type, bp1, bp2, elements):
        for i in range(0, len(elements)):
            if (elements[i].type_ == type and bp1 in elements[i].indices_ and
                    bp2 in elements[i].indices_):
                return elements[i]
        return None

    def score(self, design, params):

        score = 100
        seq = design['sequence']
        states = range(1, 3)

        # Iterate over the two states: [1, 3] = 1, 2
        for n in states:

            bpm = design['state' + str(n)]['default']['pairmap']
            ss = design['state' + str(n)]['default']['secstruct']
            elems1 = design['state' + str(n)]['default']['secstruct_elements']
            elems2 = design['state' + str(((n%2) + 1))]['default']['secstruct_elements']
            bonus = params[n-1]

            for i in range(0, len(seq)):

                # Find GU/UG base pair. Avoid double counting by looking at the
                # first half, where it the pair is opened (where in the SS
                # there is an opening parantheses.)

                if ((seq[i] == 'G' and bpm[i] != -1 and seq[bpm[i]] == 'U') or
                        (seq[i] == 'U' and bpm[i] != -1 and
                            seq[bpm[i]] == 'G') and ss[i] == '('):

                    # Find if the GU pair was in a stack and moved to a loop
                    elem1 = self.findRNAElement(
                        switch_utils.RNAELEMENT_STACK,
                        i,
                        bpm[i],
                        elems1
                    )
                    elem2 = self.findRNAElement(
                        switch_utils.RNAELEMENT_LOOP,
                        i,
                        bpm[i],
                        elems2
                    )
                    if elem1 is not None and elem2 is not None:
                        score += bonus

        return (params[2] * score ) + params[3]
