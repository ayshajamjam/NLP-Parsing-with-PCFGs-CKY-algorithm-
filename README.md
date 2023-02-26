# Parsing with Probabilistic Context Free Grammars (CKY algorithm)

## Reading the grammar: verify_grammar()

In grammar.py, read_rules takes each line in the grammar file and populates the instance variables rhs_to_rules, lhs_to_rules, and start symbol. Using parse_rule, it separates the lhs, rhs, and probability in each rule in the PCFG and then populates rhs_to_rules[lhs] and lhs_to_rules[rhs] which are both lists.

First, I wrote the method for verify_grammar in grammary.py to determine if any given grammar is in Chomsky Normal Form (CNF). That is, any nonterminal points to two nonterminals or a single terminal. 

NT --> NT NT
NT --> T

I used a smaller test grammar in sample.pcfg to ensure this method worked correctly.

**Command line command to run:** python3 grammar.py sample.pcfg

## Membership Checking with CKY: is_in_language(self, tokens)

I used the CKY algorithm to determine if a given sentence is in the grammar. The CYK algorithm uses dynamic program to iterate over a table (a dictionary in this code). It first initialized the diagonal of the table with the nonterminals that point to the terminals in the grammar. Some terminals have multiple non-terminals associated with them. For this reason, each cell can have multiple non-terminals.

We then go through the rest of the table by looking at combinations of cells that could produce another non-terminal. If in the end, we have the start symbol in the upper right corner of the table (in position (0, len(sentence))), then the sentence is in the grammar.

## Parsing with backpointers: parse_with_backpointers(self, tokens)

Here, I enhanced the previous CYK algorithm to keep track of backpointers and probabilities. This allows us to traceback our parsetree and find which once is the most probable. This is necessary because a given sentence in the grammar may have multiple parse trees.

## Retrieving a parse tree: get_tree(chart, i,j, nt)

get_tree() formats the parse tree by recursively iterating through the probability table and backpointer table produced by parse_with_backpointers.
