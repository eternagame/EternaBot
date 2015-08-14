import switch_utils
import strategy_template


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the strategy submission
        self.title_ = "[Strategy Market] [Switch] Element: Aptamer Gate"
        self.author_ = "Eli Fisker"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch-elements")

        # Default strategy parameters
        self.default_params_ = [3, 3.0, 4, 2.0, -1.0,
                                3, 1.0, 4, 2.0, 5, 3.0, 6, 1.0, -1.0, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 31

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def score(self, design, params):

        score = 100

        if design['type'] == "miRNA":
            return switch_utils.UNSCORABLE
        else:
            aptamer = min(design['site'])
            states = [1, 2]
            for state in states:

                for elem in design['state' + str(state)]['default']['secstruct_elements']:
                    if (min(elem.indices_) < aptamer < max(elem.indices_) and
                            elem.type_ == switch_utils.RNAELEMENT_STACK):
                        length = len(elem.indices_)
                        if "turn-off" in design['puztitle']:
                            if length == params[0]:
                                score += params[1]
                            elif length == params[2]:
                                score += params[3]
                            elif length > params[2]:
                                score += (params[3] +
                                          (params[4] * (length - params[2])))
                        else:
                            if length == params[5]:
                                score += params[6]
                            if length == params[7]:
                                score += params[8]
                            if length == params[9]:
                                score += params[10]
                            if length == params[11]:
                                score += params[12]
                            elif length > params[11]:
                                score += (params[13] * (length - params[11]))

        return (params[14] * score) + params[15]
