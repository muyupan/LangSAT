"""
Input:
Logical form from GPT-4o-mini: And(Not(Or(P, Q)), Implies(R, Not(S)))

Intermeidate step: 
Parsed expression: (Implies(R, ~S)) & ~(P | Q)

Output:
CNF expression: ~P & ~Q & (~R | ~S)
"""

from sympy import symbols, And, Or, Not, Implies, Equivalent
from sympy.logic.boolalg import to_cnf
from lark import Lark, Transformer
import json

def text_to_cnf(logical_form):
        """*******************
        BEGIN SETUP
        *******************"""
        # Define the grammar for propositional logic in function notation
        grammar = """
            ?start: expr

            ?expr: func_call
                | SYMBOL

            func_call: NAME "(" [expr_list] ")"

            ?expr_list: expr ("," expr)*

            SYMBOL: /[A-Za-z][A-Za-z0-9_]*/

            NAME: "And" | "Or" | "Not" | "Implies" | "Equivalent"

            %import common.WS
            %ignore WS
        """

        # Create the parser
        parser = Lark(grammar, start='start')

        # Define the transformer to convert the parse tree to SymPy expressions
        class LogicTransformer(Transformer):
            def __init__(self):
                # Dynamically create symbols as needed
                self.vars = {}
                self.functions = {
                    'And': And,
                    'Or': Or,
                    'Not': Not,
                    'Implies': Implies,
                    'Equivalent': Equivalent,
                }

            def SYMBOL(self, token):
                name = str(token)
                if name not in self.vars:
                    self.vars[name] = symbols(name)
                return self.vars[name]

            def func_call(self, items):
                func_name = str(items[0])
                func = self.functions.get(func_name)
                if func is None:
                    raise ValueError(f"Unknown function '{func_name}'")
                args = items[1] if len(items) > 1 else []
                if not isinstance(args, list):
                    args = [args]
                return func(*args)

            def expr_list(self, items):
                return items

            def start(self, items):
                return items[0]
        """*******************
        END SETUP
        *******************"""

        # Instantiate the transformer
        transformer = LogicTransformer()

        # Parse the logical expression using Lark
        parse_tree = parser.parse(logical_form)

        # Transform the parse tree into a SymPy expression
        expr = transformer.transform(parse_tree)

        cnf_expr = to_cnf(expr, simplify=True, force=True)
        return cnf_expr, expr

def disp(statement, logical_form, parsed_expr, cnf_expr):
    print("VALID" if len(str(cnf_expr).split('&')) == 4 else 'INVALID')

    print(statement)
    print(f"Logical form    ->    Parsed expression    ->    CNF expression ")
    print(f"{logical_form}    ->    {parsed_expr}    ->    {cnf_expr}", end="\n\n")

def add_sample(data, statement, logical_form, parsed_expr, cnf_expr):
    data.append({
        "statement": statement,
        "logical_form": logical_form,
        "parsed_expr": str(parsed_expr),
        "cnf_expr": str(cnf_expr)
    })

# Samples
if __name__ == "__main__":
    # 4 variables, 4 clauses, SAT instances
    # Each sentence is a clause, where 4 variables are used throughout
    # Data will be represented as a JSON list

    data = []

    # 1
    statement = """
The sky is blue, the grass is green, or the sun is yellow. 
The clouds are white, the sky is blue, or the grass is green. 
The sun is yellow, the clouds are white, or the sky is blue. 
The grass is green, the sun is yellow, or the clouds are white.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A,B,C), Or(D,A,B), Or(C,D,A), Or(B,C,D))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 2
    statement = """
If Adam plays the guitar, then Bernard plays the piano. 
Adam plays the guitar or Charlie plays the drums. 
Bernard does not play the piano or Donald learns to sing. 
Donald does not learn to sing or Adam plays the guitar.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Implies(A,B), Or(A,C), Or(Not(B),D), Or(Not(D), A))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 3
    statement = """
The sun is not shining. 
The grass is dry if and only if the sun is not shining and the rain is falling. 
The sea is calm.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Not(A), Equivalent(B, And(Not(A), C)), D)"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 4
    statement = """
If Plan A and Plan B are unsuccessful, then Plan C is successful. 
Plan A or Plan B is succesful. 
Plan B or Plan D is successful. 
Plan C is successful. 
Plan A is succesful, or Plan D is successful.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Implies(And(Not(A), Not(B)), C), Or(A, B), Or(B, D), C, Or(A, D))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 5
    statement = """
Adam has a pet dog. 
The dog eats bones and the dog eats meat. 
If the dog eats bones, then the dog is happy.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(A, And(B, C), Implies(B, D))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 6
    statement = """
Adam has a pet cat, or Barry has a pet dog. 
If Barry has a pet dog, then Barry does not buy fish. 
Adam buys fish or Barry buys fish. 
Adam has a pet cat and Barry has a pet dog if and only if Adam buys fish.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B), Implies(B, Not(C)), Or(D, C), Equivalent(And(A, B), D))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 7
    statement = """
1 is an odd number, or 2 is an even number. 
3 is an odd number if 2 and 4 are even numbers. 
2 is an even number or 3 is an even number or 4 is an odd number. 
1 is an odd number or 4 is an odd number.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B), Implies(And(B, D), C), Or(B,Not(C),Not(D)), Or(A, Not(D)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 8
    statement = """
Apples are red, or bananas are yellow, or carrots are orange. 
Carrots are orange if and only if durians are spiky. 
Durians are spiky, or apples are red, or carrots are purple. 
Bananas are yellow if and only if durians are spiky.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B, C), Equivalent(C, D), Or(D, A, Not(C)), Equivalent(B, D))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 9
    statement = """
The circus has a ferris wheel or the circus has a rollercoaster. 
The circus does not have a carousel if and only if the circus has a ferris wheel and the circus has a rollercoaster. 
If the circus does not have a carousel, then the circus has a trapese. 
The circus does not have a trapese and the circus has a rollercoaster.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B), Equivalent(Not(C), And(A, B)), Implies(Not(C), D), And(Not(D), B))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 10
    statement = """
Alex owns a car if Bob has a truck. 
It is not the case that Bob has a truck or Charlie has a bike. 
Charlie has a bike if Daniel has a scooter. 
Daniel has a scooter if Alex owns a car.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Implies(B, A), Not(Or(B, C)), Implies(D, C), Implies(A, D))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 11
    statement = """
It will be sunny tomorrow if it is raining today. 
Yesterday was not sunny, or it is not raining today, or it will be sunny tomorrow. 
Today is warm, or it is raining today, or it is not sunny tomorrow. 
It is raining today, or it is not warm today, or yesterday was not sunny.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Implies(B, A), Or(Not(A), Not(B), C), Or(D, B, Not(C)), Or(B, Not(D), Not(A)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 12
    statement = """
XCo spends over $100,000 on advertising, XCo spends over $300,000 on developers, or XCo spends over $500,000 on servers. 
XCo spends under $20,000 on rent, XCo does not spend over $300,000 on developers, or XCo spends over $100,000 on advertising. 
XCo spends over $500,000 on servers if and only if XCo does not spend over $300,000 on developers. 
Xco does not spend under $20,000 on rent, XCo spends over $300,000 on developers, or XCo spends under $500,000 on servers.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B, C), Or(D, Not(B), A), Equivalent(C, Not(B)), Or(Not(D), B, Not(C)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 13
    statement = """
The red ball is 4kg if and only if the green ball is 2kg. 
It is not true that the red ball is 4kg or the blue ball is 3kg. 
If the green ball is 2kg, then the orange ball is 1kg. 
The orange ball is 1kg, or the blue ball is 3kg and the red ball is 4kg.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Equivalent(A, B), Not(Or(A, C)), Implies(B, D), Or(D, And(C, A)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 14
    statement = """
The zoo has a lion, the zoo has a tiger, or the aquarium has a shark and a dolphin. 
If the aquarium has a shark, the zoo does not have a tiger. 
The zoo does not have a tiger, the aquarium does not have a dolphin, or the zoo has a lion. 
The zoo has a lion, the aquarium has a shark, or the zoo has a tiger. 
The zoo has a tiger, the aquarium does not have a dolphin.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B, And(C, D)), Implies(C, Not(B)), Or(Not(B), Not(D), A), Or(A, C, B), Or(B, Not(D)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 15
    statement = """
The stars are bright, or the moon is full. 
The satellite passes overhead, or the night is dark. 
The stars are not bright, or the night is not dark. 
The satellite passes overhead, or the moon is not full.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B), Or(C, D), Or(Not(A), Not(C)), Or(C, Not(B)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 16
    statement = """
The desert is dry, the rainforest is wet, or the tundra is cold. 
The tundra is not cold, the desert is not dry, or the savannah is hot. 
It is not true that the savannah is hot if and only if the tundra is cold and the desert is dry. 
The savannah is not hot, the rainforest is not wet, or the desert is not dry.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B, C), Or(Not(C), Not(A), D), Not(Equivalent(D, And(C, A))), Or(Not(D), Not(B), Not(A)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 17
    statement = """
The father is bald, or the mother has a bob. 
If the son has a mohawk, the sister has a ponytail. 
If the father is bald, the son has a mohawk. 
The mother does not have a bob, or the sister does not have a ponytail.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B), Implies(C, D), Implies(A, C), Or(Not(B), Not(D)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 18
    statement = """
The circle is red, the square is blue, the triangle is green, or the hexagon is yellow.
The hexagon is not yellow if and only if the circle is red and the square is blue.
If the triangle is green, then the square is blue.
The hexagon is yellow, or the circle is not red, or the square is blue, or the circle is red.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B, C, D), Equivalent(Not(D), And(A, B)), Implies(C, B), Or(D, Not(A), B, A))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 19
    statement = """
The high dive is 15m if the pool is 3m deep. 
If the pool is not 3m deep, the high dive is 10m or the pool is 25m long. 
The pool is 25m long, or the pool is 3m deep. 
The high dive is not 15m, the high dive is 10m, or the pool is not 25m long. 
The pool is 3m deep, the high dive is not 10m, or the high dive is 15m.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Implies(B, A), Implies(Not(B), Or(C, D)), Or(D, B), Or(Not(A), C, Not(D)), Or(B, Not(C), A))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 20
    statement = """
The man has a tie, the child has a toy, or the lady has a purse. 
The child has a toy, the baby has a rattle, or the lady does not have a purse. 
The lady has a purse, or the man does not have a tie. 
It is not true that the child has a toy and the baby has a rattle.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B, C), Or(B, D, Not(C)), Or(C, Not(A)), Not(And(B, D)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 21
    statement = """
John has read 10 books, Mark has read 20 books, or Luke has read 25 books. 
If John has read 10 books, then Dimitri has read 15 books. 
Mark has not read 20 books if Luke has not read 25 books. 
Dimitri has read 15 books and John has read 10 books, or Luke has read 25 books and Dimitri has not read 15 books.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B, C), Implies(A, D), Implies(Not(C), Not(B)), Or(And(D, A), And(C, Not(D))))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 22
    statement = """
The alto sings an A, the tenor sings a B, or the soprano sings a C. 
The soprano sings a C, the bass sings a D, or the tenor sings a B. 
The bass sings a D, the tenor sings a B, or the alto sings an A. 
The alto sings an A, the soprano sings a C, or the bass sings a D.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B, C), Or(C, D, B), Or(D, B, A), Or(A, C, D))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 23
    statement = """
The pen is black, or the highlighter is yellow. 
The pen is not black, or the marker is blue. 
It is impossible for both the marker and the highlighter to be blue and yellow, respectively. 
The crayon is orange.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B), Or(Not(A), C), Not(And(C, B)), D)"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 24
    statement = """
There is a football game on Sunday, there is a basketball game on Monday, or there is a baseball game on Tuesday. 
There is a baseball game on Tuesday if and only if there is a lacrosse game on Wednesday. 
There is a football game on Sunday if and only if there is a basketball game on Monday. 
There is a baseball game on Tuesday.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B, C), Equivalent(C, D), Equivalent(A, B), C)"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 25
    statement = """
Adam speaks in English, or Barry speaks in French. 
If Adam speaks in English, then Barry speaks in French or Charlie speaks in German. 
Charlie does not speak in German if Barry speaks in French. 
David speaks in Spanish, or Adam speaks in English if Charlie speaks in German.
David does not speak in Spanish, or Adam speaks in English.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B), Implies(A, Or(B, C)), Implies(B, Not(C)), Or(D, Implies(C, A)), Or(Not(D), A))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 26
    statement = """
The stapler is out of staples, or the printer is out of ink. 
The printer is out of ink, or the pencil is out of lead. 
The pencil is not out of lead, or the speaker is out of batteries. 
The speaker is out of batteries, or the stapler is out of staples.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B), Or(B, C), Or(Not(C), D), Or(D, A))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 27
    statement = """
There is a lion in the jungle, there is a squirrel in the forest, or there is a fish in the ocean. 
There is a squirrel in the forest, or there is a fish in the ocean. 
There is not a fish in the ocean, there is a bird in the sky, there is not a lion in the jungle, or there is a squirrel in the forest. 
There is not a squirrel in the forest, there is a fish in the ocean, or there is not a bird in the sky. 
If there is a bird in the sky, there is a lion in the jungle.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B, C), Or(B, C), Or(Not(C), D, Not(A), B), Or(Not(B), C, Not(D)), Implies(D, A))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 28
    statement = """
If dad has a birthday this month, mom has a birthday next month.
If grandpa has a birthday this month, grandma has a birthday next month.
If grandma has a birthday next month, mom has a birthday next month.
If grandpa has a birthday this month, dad does not have a birthday this month.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Implies(A, B), Implies(C, D), Implies(D, B), Implies(C, Not(A)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 29
    statement = """
The zebra is white, the rhino is grey, the bear is brown, or the bird is blue. 
The rhino is not grey, or the bear is not brown. 
It is not true that the zebra is white and the bird is blue. 
The rhino is grey, or the bird is not blue.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B, C, D), Or(Not(B), Not(C)), Not(And(A, D)), Or(B, Not(D)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 30
    statement = """
There are five tulips, or there are four roses. 
There are not four roses, or there are three daisies and two sunflowers. 
It is not true that if there are two sunflowers, then there are not three sunflowers and not five tulips. 
If there are three daisies, then there are four roses.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B), Or(Not(B), And(C, D)), Not(Implies(D, And(Not(C), Not(A)))), Implies(C, B))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 31
    statement = """
James is an artist, Theo is a baker, or Alex is a chef. 
If and only if Alex is chef then James is not an artist. 
Peter is a doctor, or Theo is a baker. 
Peter is not a doctor, or Theo is not a baker.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B, C), Equivalent(C, Not(A)), Or(D, B), Or(Not(D), Not(B)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 32
    statement = """
The apple is small if the blueberry is big. 
If the blueberry is big, then the cranberry is tiny and the date is medium. 
The date is not medium if the blueberry is not big.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Implies(B, A), Implies(B, And(C, D)), Implies(Not(B), Not(D)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 33
    statement = """
There are forty men in the West platoon. 
There are sixty men in the East platoon, there are seventy men in the North platoon, or there are eighty men in the South platoon. 
If there are seventy men in the North platoon, then there are not forty men in the West platoon. 
It is not true that there are sixty men in the East platoon and there are eighty men in the South platoon.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(A, Or(B, C, D), Implies(C, Not(A)), Not(And(B, D)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 34
    statement = """
The minnow is puny, or the shark is mean. 
The swordfish is cunning, the minnow is not puny, or the dolphin is happy. 
The dolphin is not happy if the shark is mean. 
The shark is mean, the swordfish is not cunning, or the dolphin is not happy.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B), Or(C, Not(A), D), Implies(B, Not(D)), Or(B, Not(C), Not(D)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 35
    statement = """
The box is tall, or the crate is short. 
The crate is short and the barrel is round, or it is not true that the container is wide. 
The container is not wide if the box is tall and the crate is not short.
if the barrel is round, then the box is tall.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B), Or(And(B, C), Not(D)), Implies(And(A, Not(B)), Not(D)), Implies(C, A))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 36
    statement = """
The picnic is at 2pm, the dinner is at 6pm, or the party is at 10pm. 
The picnic is not at 2pm, the dinner is at 6pm, or the party is at 10pm. 
The festival is at 8pm. 
It is not true that the picnic is at 2pm or the dinner is at 6pm.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B, C), Or(Not(A), B, C), D, Not(Or(A, B)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 37
    statement = """
The brocolli is steamed, the carrots are boiled, or the peas are raw.
The chicken is fried if and only if the carrots are boiled.
The peas are raw if and only if the carrots are boiled.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B, C), Equivalent(D, B), Equivalent(C, B))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 38
    statement = """
If the red button was pressed once, then the blue button was pressed twice and the green button was pressed three times. 
The green button was pressed three times, or the purple button was pressed four times. 
The purple button was pressed four times if and only if the red button was pressed once.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Implies(A, And(B, C)), Or(C, D), Equivalent(D, A))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 39
    statement = """
Classroom A has 20 students, Classroom B has 15 students, or Classroom C has 30 students. 
There are 40 students in Classroom D if there are 15 students in Classroom B. 
Classroom D has 40 students, or Classroom A does not have 20 students. 
It is not true that Classroom B has 15 students or Classroom C has 30 students.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B, C), Implies(B, D), Or(D, Not(A)), Not(Or(B, C)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 40
    statement = """
There is orange juice in the plastic cup, or there is soda in the glass cup. 
There is water in the metal cup, there is not orange juice in the plastic cup, or there is cider in the mug. 
If there is cider in the mug, then there is water in the metal cup if there is soda in the glass cup. 
There is cider in the mug, or there is orange juice in the plastic cup.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B), Or(C, Not(A), D), Implies(D, Implies(C, B)), Or(D, A))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 41
    statement = """
It is not true that the sky is yellow and the sun is green. 
It is not true that the roses are blue and the violets are red. 
If the sky is yellow then the violets are red. 
It is not true that if the violets are red and the sky is yellow then the sun is green.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Not(And(A, B)), Not(And(C, D)), Implies(A, D), Not(Implies(And(D, A), C)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 42
    statement = """
The dentist went to school for 8 years, the doctor went to school for 12 years, or the lawyer went to school for 16 years. 
The teacher went to school for 6 years, the doctor did not go to school for 12 years, or the dentist went to school for 8 years. 
If the lawyer went to school for 16 years and the teacher went to school for 6 years, then the dentist did not go to school for 8 years. 
The teacher went to school for 6 years if the lawyer did not go to school for 16 years.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B, C), Or(D, Not(B), A), Implies(And(C, D), Not(A)), Implies(Not(C), D))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 43
    statement = """
The journey is complete if the treasure is found and the map is examined. 
The map is not examined if the map is lost. 
The journey is not complete, the treasure is not found, or the map is lost. 
If the map is lost, the treasure is not found.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Implies(And(A, B), C), Implies(D, Not(B)), Or(Not(C), Not(A), D), Implies(D, Not(A)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 44
    statement = """
The glasses belong to Sue, or the sunglasses belong to Sue. 
The glasses do not belong to Sue if the glasses belong to Bob and the sunglasses belong to Bob. 
The sunglasses do not belong to Bob, or the glasses and sunglasses belong to Sue.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B), Implies(And(C, D), Not(A)), Or(Not(D), And(A, B)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 45
    statement = """
The mouse finds the cheese if the homeowner setup a mousetrap. 
The homeowner setup a mousetrap if the homeowner saw a rodent. 
The homeowner setup a mousetrap if the homeowner heard squeaking. 
The homeowner did not hear squeaking, the homeowner did not see a rodent, or the homewner setup a mousetrap. 
The mouse did not find the cheese, or the homeowner saw a rodent.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Implies(B, A), Implies(C, B), Implies(D, B), Or(Not(D), Not(C), B), Or(Not(A), C))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 46
    statement = """
Plane A at 32000 feet, Plane B is at 35000 feet, Plane C is at 38000 feet, or Plane D is at 41000 feet. 
Plane A is at 32000 feet and Plane B is at 35000 feet if and only if Plane D is at 41000 feet.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B, C, D), Equivalent(And(A, B), D))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 47
    statement = """
The Olympics are in Tokyo, the World Cup is in Qatar, or the Super Bowl is in Los Angeles. 
The NBA Finals are in Los Angeles if and only if the Super Bowl is in Los Angeles. 
The NBA Finals are not in Los Angeles if the World Cup is in Qatar.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B, C), Equivalent(D, C), Implies(B, Not(D)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 48
    statement = """
Fishing is in the morning, hiking is at noon, or swimming is in the afternoon. 
The bonfire is at night, swimming is not in the afternoon, or hiking is not at noon. 
Hiking is at noon, or the bonfire is at night, or fishing is not in the morning. 
Fishing is in the morning if and only if the bonfire is not at night.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B, C), Or(D, Not(C), Not(B)), Or(B, D, Not(A)), Equivalent(A, Not(D)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 49
    statement = """
There was a message on the answering machine, or there was a note on the fridge. 
If there was not a note on the fridge, there was a conversation. 
If there was a note on the fridge, there was a text message and not a message on the answering machine. 
There was a text message, or there was not a message on the answering machine.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Or(A, B), Implies(Not(B), C), Implies(B, And(D, Not(A))), Or(D, Not(A)))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # 50
    statement = """
The bread was freshly baked if the baker was here this morning. 
The door was unlocked this morning, or the baker was not here this morning. 
The door was not unlocked this morning, or the door was locked last night. 
If the door was unlocked this morning, the baker was here this morning or the door was not locked last night.
"""
    statement = ''.join(statement.split('\n'))
    logical_form = "And(Implies(B, A), Or(C, Not(B)), Or(Not(C), D), Implies(C, Or(B, Not(D))))"
    cnf_expr, parsed_expr = text_to_cnf(logical_form)
    disp(statement, logical_form, parsed_expr, cnf_expr)
    add_sample(data, statement, logical_form, parsed_expr, cnf_expr)

    # Save data as json
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)