"""
About this file:
Contains the class Pcfg which represents a PCFG grammar 
read in from a grammar file
"""

import sys
from collections import defaultdict
from math import fsum, isclose

class Pcfg(object): 
    """
    Represent a probabilistic context free grammar 
    in Chomsky Normal Form
    """
    def __init__(self, grammar_file): 
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None 
        self.read_rules(grammar_file)      
 
    # Populate instance variables by reading grammar_file line by line
    def read_rules(self,grammar_file):
        for line in grammar_file: 
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line: 
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else: 
                    startsymbol, prob = line.rsplit(";")
                    self.startsymbol = startsymbol.strip()
    
    # Separate lhs, rhs, prob for any given rule
    def parse_rule(self,rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";",1) 
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        return (lhs, rhs, prob)

    def verify_grammar(self):
        """
        Part 1
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise return False. 
        """

        # Extract left-hand-side non-terminals using dictionary keys
        nonterminals = set(self.lhs_to_rules.keys())
        # print("Non-terminals: ", nonterminals, "\n")
        # print("Terminals: ", list(self.rhs_to_rules.keys()), "\n")

        # Check if grammar is in CNF 
        for rhs in self.rhs_to_rules.keys():
            # print(rhs, ' ---- ', len(rhs))

            # RHS with one element: one terminal
            if len(rhs) == 1:
                if(rhs[0] in nonterminals):
                    print("NT --> NT not allowed. PCFG is not in CNF")
                    return False
            # RHS with two elements: both non-terminals
            elif len(rhs) == 2:
                if(not(rhs[0] in nonterminals and rhs[1] in nonterminals)):
                    print("NT --> NT NT if two elements on RHS. PCFG is not in CNF")
                    return False
            # RHS with 2+ elements
            else:
                print("Cannot have more than 2 nonterminals or terminals on RHS. PCFG is not in CNF")
                return False

        # Check if all probabilities for the same lhs (non-terminal) symbol approx sum to 1.0
        lhs_sum = defaultdict(int)
        for lhs in nonterminals:
            
            # Calculate sum of probabilities of each rhs for each non-terminal
            # print("LHS --> RHS:\n" self.lhs_to_rules[lhs], "\n")
            for rhs in range(len(self.lhs_to_rules[lhs])):
                lhs_sum[lhs] += self.lhs_to_rules[lhs][rhs][2]
            
            # Compare summation to 1.0
            if (not isclose(1.0, lhs_sum[lhs])):
                print("Probabilities for non-terminal-- ", lhs, " --do not sum to approx 1.0")
                return False

        # print("Summations:\n", dict(lhs_sum))

        print("The PCFG is in CNF")
        return True 


if __name__ == "__main__":
    with open(sys.argv[1],'r') as grammar_file:
        grammar = Pcfg(grammar_file)
        
    grammar.verify_grammar()