import switch_utils
import strategy_template
import re


class Strategy(strategy_template.Strategy):
    def __init__(self):

        strategy_template.Strategy.__init__(self)

        # Title, author of the strategy submission
        self.title_ = "[Strategy Market] [Switch] JL's microRNA fish hook 1"

        self.author_ = "Eli Fisker"

        # URL where the strategy was initially submitted
        self.url_ = ("https://getsatisfaction.com/eternagame/topics/"
                     "-strategy-market-switch-jl-s-microrna-fish-hook-1")

        # Default strategy parameters
        self.default_params_ = [1, 0.5, float(1/3), 0.75, 0.25, 2.0, -1.0, 0.05, 0]

        # Number of lines of code used to implement the strategy
        self.code_length_ = 75

        self.publishable_ = True
        self.denormalized_ = True
        self.comprehensive = False

    def weakPair(self, base1, base2):
        return ((base1 == 'G' and base2 == 'U') or
                (base1 == 'U' and base2 == 'G'))

    def canPair(self, b1, b2):
        return ((b1 == 'G' and (b2 == 'U' or b2 == 'C')) or
                (b1 == 'U' and (b2 == 'A' or b2 == 'G')) or
                (b1 == 'A' and (b2 == 'U')) or
                (b1 == 'C' and (b2 == 'G')))

    def findRNAElement(self, type, bp, elements):

        for i in range(0, len(elements)):
            if ((type == "any" or elements[i].type_ == type) and
                    bp in elements[i].indices_):
                return elements[i]

        return None

    def score(self, design, params):

        score = 100

        if design['type'] != "miRNA":
            return switch_utils.UNSCORABLE
        else:
            states = range(1, 3)  # [1, 2]
            for state in states:

                # find all occurences of "."*8, including overlap
                ss = '.'* 8
                occurences = [m.start() for m in re.finditer(
                        '(?=' + ss + ')',
                        design['state' + str(state)]['default']['secstruct']
                        )]

                bestoccurence = None
                bestcomplement = None
                bestcomplength = 0

                for occ in occurences:

                    complement = []
                    complength = 0

                    for i in range(0, len(design['oligoseq']) - (len(ss))):

                        pcomp = []
                        pcomplen = 0

                        for n in range(0, len(ss)):
                            if self.canPair(
                                    design['oligoseq'][i + n],
                                    design['sequence'][n + occ]
                                    ):
                                pcomp.append(i + n)
                                pcomplen += 1
                            else:
                                pcomp.append(-1)

                        if pcomp > complength:
                            complength = pcomplen
                            complement = pcomp

                    if complength > bestcomplength:
                        bestoccurence = occ
                        bestcomplength = complength
                        bestcomplement = complement

                if bestcomplength != 0:

                    multiplier = 0

                    # 3' end
                    if bestoccurence == len(design['sequence']) - 8:
                        multiplier = params[0]

                    # 5' end
                    elif bestoccurence == 0:
                        multiplier = params[1]

                    else:

                        rnaelement = self.findRNAElement(
                                    "any",
                                    bestoccurence,
                                    design['state' + str(state)]['default']['secstruct_elements']
                                    )

                        # multiloop
                        minind = min(rnaelement.indices_)
                        maxind = max(rnaelement.indices_)

                        if (minind - 1 >= 0 and 
                                maxind + 1 < len(design['sequence']) and 
                                self.canPair(
                                    design['sequence'][min(rnaelement.indices_) - 1],
                                    design['sequence'][max(rnaelement.indices_) + 1]
                                )):
                            multiplier = params[2]

                        # gap bases
                        else:
                            multiplier = params[3]

                    # aims for anything other than first 8 bases
                    if bestcomplement[0] != 0:
                        multiplier *= params[4]

                    score += multiplier * (bestcomplength * params[5])

                    for i in range(0, len(bestcomplement)):
                        if bestcomplement[i] != -1 and self.weakPair(
                                design['sequence'][bestoccurence + i],
                                design['oligoseq'][complement[i]]):
                            score += params[6]

        return (params[7] * score) + params[8]
