"""
COMS W4705 - Natural Language Processing - Spring 2023
Homework 2 - Parsing with Probabilistic Context Free Grammars 
Daniel Bauer

About this file:
contains your parser and initially only contained scaffolding
code
"""
import math
import sys
from collections import defaultdict
import itertools
from grammar import Pcfg

### Use the following two functions to check the format of your data structures in part 3 ###
def check_table_format(table):
    """
    Return true if the backpointer table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Backpointer table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and \
          isinstance(split[0], int)  and isinstance(split[1], int):
            sys.stderr.write("Keys of the backpointer table must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of backpointer table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            bps = table[split][nt]
            if isinstance(bps, str): # Leaf nodes may be strings
                continue 
            if not isinstance(bps, tuple):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Incorrect type: {}\n".format(bps))
                return False
            if len(bps) != 2:
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Found more than two backpointers: {}\n".format(bps))
                return False
            for bp in bps: 
                if not isinstance(bp, tuple) or len(bp)!=3:
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has length != 3.\n".format(bp))
                    return False
                if not (isinstance(bp[0], str) and isinstance(bp[1], int) and isinstance(bp[2], int)):
                    print(bp)
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has incorrect type.\n".format(bp))
                    return False
    return True

def check_probs_format(table):
    """
    Return true if the probability table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Probability table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and isinstance(split[0], int) and isinstance(split[1], int):
            sys.stderr.write("Keys of the probability must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of probability table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            prob = table[split][nt]
            if not isinstance(prob, float):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a float.{}\n".format(prob))
                return False
            if prob > 0:
                sys.stderr.write("Log probability may not be > 0.  {}\n".format(prob))
                return False
    return True



class CkyParser(object):
    """
    A CKY parser.
    """

    def __init__(self, grammar): 
        """
        Initialize a new parser instance from a grammar. 
        """
        self.grammar = grammar

    def is_in_language(self,tokens):
        """
        Membership checking. Parse the input tokens and return True if 
        the sentence is in the language described by the grammar. Otherwise
        return False
        Use CYK algorithm
        """

        table = defaultdict(tuple)
        
        # Initialize diagonal
        # dict(tuple : list); ex: (5,6):['NP', 'N']
        for i in range(0, len(tokens)):
            terminal_tup = tuple(tokens[i].split())
            nonterminal = []
            # find all rules where lhs --> terminal
            for lhs in self.grammar.rhs_to_rules[terminal_tup]:
                nonterminal.append(lhs[0])
                # print(lhs[0], ' -> ', terminal_tup)
            table[(i, i+1)] = nonterminal

        # Main loop
        n = len(tokens)
        for length in range(2,n+1):
            # print('Level: ', length, '\n')
            for i in range(0, (n-length)+1):
                j = i + length
                table[i,j] = []
                for k in range(i+1, j):
                    B = table[(i,k)]
                    C = table[(k,j)]
                    # Each cell in B and C can have multiple non-terminals
                    for nt_b in B:
                        for nt_c in C:
                            rhs = tuple([nt_b, nt_c])
                            # Check if the rule is in the grammar
                            if(self.grammar.rhs_to_rules[rhs]):
                                for lhs in self.grammar.rhs_to_rules[rhs]:
                                    # print('grammar contains rule: ', lhs[0], ' -> ', rhs)
                                    # Handle duplicates like (1,6):['VP','VP'];
                                    if(lhs[0] not in table[(i,j)]):
                                        table[(i,j)].append(lhs[0])
        # print("CYK Table:\n", dict(table), "\n")

        # Check if list in upper-right corner is nonempty so you can access first element in list (prevents index error)
        # Check if upper-right corner contains start symbol
        if(table[(0,n)] and self.grammar.startsymbol in table[(0,n)]):
            # The sentence is in the grammar
            return True

        # The sentence is NOT in the grammar
        return False 
       
    def parse_with_backpointers(self, tokens):
        """
        Parse the input tokens and return a parse table and a probability table.
        """
        table = defaultdict(tuple)  #table containing backpointers
        probs = defaultdict(tuple)  #table containing probabilities

        # Initialize diagonal
        # dict(tuple : list); ex: (5,6):['NP', 'N']
        for i in range(0, len(tokens)):
            terminal_tup = tuple(tokens[i].split())
            nonterminal_ptr = {}
            nonterminal_prob = {}
            for lhs in self.grammar.rhs_to_rules[terminal_tup]:
                nonterminal_ptr[lhs[0]] = tokens[i]  # terminals are just strings (no backpointers)
                nonterminal_prob[lhs[0]] = math.log2(lhs[2]) # add to probs table
                # print(lhs[0], ' -> ', terminal_tup)
            table[(i, i+1)] = nonterminal_ptr
            probs[(i, i+1)] = nonterminal_prob

        # Main loop
        n = len(tokens)
        for length in range(2,n+1):
            # print('Level: ', length, '\n')
            for i in range(0, (n-length)+1):
                j = i + length
                table[i,j] = {}
                probs[i,j] = {}
                for k in range(i+1, j):
                    B = table[(i,k)]
                    C = table[(k,j)]
                    # Each cell in B and C can have multiple non-terminals
                    for nt_b in B.keys():
                        for nt_c in C.keys():
                            rhs = tuple([nt_b, nt_c])
                            # print(rhs)
                            # Check if the rule is in the grammar
                            if(self.grammar.rhs_to_rules[rhs]):
                                for lhs in self.grammar.rhs_to_rules[rhs]:
                                    # print('grammar contains rule: ', lhs[0], ' -> ', rhs)
                                    
                                    # Rule probability
                                    prob_rule = lhs[2]  # Ex: NP -> D N

                                    # Probability of left NT on RHS
                                    prob_left = probs[(i,k)][nt_b]  # Ex: Prob(D)

                                    # Probability of right NT on RHS
                                    prob_right = probs[(k,j)][nt_c] # Ex: Prob(N)

                                    # Log probability: sum of 3 calculations (logs)
                                    log_prob = math.log2(prob_rule) + prob_left + prob_right

                                    # Deals with case where two of the same non-terminals appear in the same cell
                                    # Ex: (1,6): two VP options
                                    if(lhs[0] in table[(i,j)].keys()):
                                        # Check which log_prob is higher
                                        if((log_prob) > (probs[(i,j)][lhs[0]])):
                                            table[(i,j)][lhs[0]] = ((nt_b, i, k),(nt_c, k, j))
                                            probs[(i,j)][lhs[0]] = log_prob
                                    else:
                                        table[(i,j)][lhs[0]] = ((nt_b, i, k),(nt_c, k, j))
                                        probs[(i,j)][lhs[0]] = log_prob

        # Sentence not in grammar
        if(not(table[(0,n)] and self.grammar.startsymbol in table[(0,n)])):
            return {}, {}

        return table, probs

def get_tree(chart, i,j,nt): 
    """
    Return the parse-tree rooted in non-terminal nt and covering span i,j.
    """
    tree = tuple([nt])

    # Terminal reached then return (NT, string)
    if(type(chart[(i,j)][nt]) is str):
        tree = tuple((nt, chart[(i,j)][nt]))
        return tree
    
    # Left subtree
    left_i = chart[(i,j)][nt][0][1]
    left_j = chart[(i,j)][nt][0][2]
    left_nt = chart[(i,j)][nt][0][0]
    tree = (*tree, get_tree(chart, left_i, left_j, left_nt))

    # Right subtree
    right_i = chart[(i,j)][nt][1][1]
    right_j = chart[(i,j)][nt][1][2]
    right_nt = chart[(i,j)][nt][1][0]
    tree = (*tree, get_tree(chart, right_i, right_j, right_nt))
    
    return tree
    
if __name__ == "__main__":
    
    with open('atis3.pcfg','r') as grammar_file: 
        grammar = Pcfg(grammar_file)
        parser = CkyParser(grammar)

        # Test Part 1
        # grammar.verify_grammar()

        # Test Part 2, 3

        # Test atis3.pcfg: valid
        toks = ['flights', 'from','miami', 'to', 'cleveland','.']
        print("Sentence in grammar? ", parser.is_in_language(toks))

        # Test atis3.pcfg: invalid
        # toks = ['miami', 'flights','cleveland', 'from', 'to','.']
        # print("Sentence in grammar? ", parser.is_in_language(toks))

        # Test sample.pcfg: valid
        # toks = ['she', 'saw', 'the', 'cat', 'with', 'glasses']
        # print("Sentence in grammar? ", parser.is_in_language(toks))

        # Test sample.pcfg: invalid
        # toks = ['with', 'glasses', 'she', 'saw', 'the', 'cat']
        # print("Sentence in grammar? ", parser.is_in_language(toks))

        # Test Part 3
        table, probs = parser.parse_with_backpointers(toks)
        assert check_table_format(table)
        assert check_probs_format(probs)

        print("Table: ", dict(table), '\n')
        print("Probs: ", dict(probs), '\n')

        # Test Part 4
        print(get_tree(table, 0, len(toks), grammar.startsymbol),'\n')

