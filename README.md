# Parsing with Probabilistic Context Free Grammars (CKY algorithm)

In grammar.py, read_rules takes each line in the grammar file and populates the instance variables rhs_to_rules, lhs_to_rules, and start symbol. Using parse_rule, it separates the lhs, rhs, and probability in each rule in the PCFG and then populates rhs_to_rules[lhs] and lhs_to_rules[rhs] which are both lists.


First, I wrote the method for verify_grammar in grammary.py to determine if any given grammar is in Chomsky Normal Form (CNF). That is, any nonterminal points to two nonterminals or a single terminal. 

NT --> NT NT
NT --> T

I used a smaller test grammar in sample.pcfg to ensure this method worked correctly.

**Command line command to run:** python3 grammar.py sample.pcfg
