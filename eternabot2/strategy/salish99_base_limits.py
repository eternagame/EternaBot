import strategy_template


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the strategy submission
        self.title_ = "[Strategy Market][Switch]Base limits"
        self.author_ = "salish99"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch-base-limits")

        # Default strategy parameters

        # params organization:
        # first row is for C% ranges
        # second row is for G% ranges
        # third row is for U% ranges
        # fourth row is for A% ranges
        # fifth row is the definition of the penalties/scores
        # fifth row is: large penalty (30), small penalty (31),
        # large award (32), medium award (33), small award (34)

        self.default_params_ = [0.0, 0.24, 0.1, 0.14, 0.14, 0.24,
                                .0, .4, .18, .25, .15, .18, .25, .3, .3, .4,
                                0.0, 0.25, 0.08, 0.2, 0.2, 0.25,
                                0.2, 0.65, 0.2, 0.25, 0.7, 0.75, 0.4, 0.58,
                                -2.0, -1.0, 3.0, 2.0, 1.0, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 48

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def score(self, design, params):

        sequence = design['sequence']
        seqlen = len(sequence)
        seq_range = range(0, len(sequence))

        perG = perC = perA = perU = 0  # percentages of each base

        for i in seq_range:
            if sequence[i] == "G":
                perG += 1
            elif sequence[i] == "C":
                perC += 1
            elif sequence[i] == "A":
                perA += 1
            else:
                perU += 1

        perG = float(perG)/seqlen
        perC = float(perC)/seqlen
        perU = float(perU)/seqlen
        perA = float(perA)/seqlen

        score = 100

        if not (params[0] < perC < params[1]):
            score += params[30]
        if (params[2] < perC < params[3]):
            score += params[32]
        if (params[4] < perC < params[5]):
            score += params[34]

        if not (params[6] < perG < params[7]):
            score += params[30]
        if (params[8] < perG < params[9]):
            score += params[32]
        if (params[10] < perG < params[11]):
            score += params[33]
        if (params[12] < perG < params[13]):
            score += params[33]
        if (params[14] < perG < params[15]):
            score += params[34]

        if not (params[16] < perU < params[17]):
            score += params[30]
        if (params[18] < perU < params[19]):
            score += params[32]
        if (params[20] < perU < params[21]):
            score += params[34]

        if not (params[22] < perA < params[23]):
            score += params[30]
        if not ((params[24] < perA < params[25]) or
                (params[26] < perA < params[27])):
            score += params[31]
        if (params[28] < perA < params[29]):
            score += params[32]

        return (params[35] * score) + params[36]
