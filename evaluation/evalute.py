import os
import string
import nltk
from nltk.tokenize import sent_tokenize
from sympy import symbols, And, Or, Not, Implies, Equivalent
from sympy.logic.boolalg import to_cnf
from openai import OpenAI
from lark import Lark, Transformer
import configparser
import json

nltk.download('punkt_tab')

# # Set environment variables if needed (adjust paths as needed)
# os.environ['NLTK_DATA'] = '/scratch/mfp5696/nltk_data'  # Adjust as needed
# nltk.data.path.append('/scratch/mfp5696/nltk_data')     # Adjust as needed

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

# Instantiate the transformer
transformer = LogicTransformer()

def sentence_to_logical_form(sentence):
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config['openai']['api_key']
    client = OpenAI(api_key=api_key)

    completion = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
          {"role": "system", "content": """
You are an AI assistant that converts English sentences into logical expressions in propositional logic. 
The sequence of sentences given are logically connected by AND, and it must be wrapped in And(<expr>). 
For variable names, use a single capitalized alphabetic variables (like A, B, C, D).
For logical connectives, use the following: And(P, Q), Or(P, Q), Not(P), Implies(P, Q), Equivalent(P, Q). 
Logical expressions can be nested within each other, if applicable to the statement. 
Provide only the logical expression without any additional text. 
Do not provide any comments.
"""},
          {
            "role": "user",
            "content": f"{sentence}"
          }
      ]
  )
    logical_form = completion.choices[0].message.content.strip()
    return logical_form

def text_to_cnf(text):
    logical_form = sentence_to_logical_form(text)
    print("Logical form from GPT-4o-mini: ", logical_form)
    print(f"Logical form for sentence '{text}': {logical_form}")
    try:
        # Parse the logical expression using Lark
        parse_tree = parser.parse(logical_form)
        # Transform the parse tree into a SymPy expression
        expr = transformer.transform(parse_tree)
        print(f"Parsed expression: {expr}")
        cnf_expr = to_cnf(expr, simplify=True, force=True)
        print(f"CNF expression: {cnf_expr}")
        return cnf_expr 
    except Exception as e:
        print(f"Error processing logical form '{logical_form}': {e}")

def evaluate(cnf_expr, expected):
    """
    This function evaluates whether the given cnf_expr is equivalent with the expected CNF expression, from a logical perspective.
    This function assumes both cnf_expr and expected have already been simplified to their most reduced form.

    Inputs:
        cnf_expr: a CNF encoding of a logical statement, output from the model
        expected: the expected CNF encoding
    Output:
        returns True if the given cnf_expr is equivalent to the expected CNF expression, False otherwise
    
    Equivalence is tested as follows:
    1. Replace all symbols in both CNFs with X_i, where each X_i corresponds to a variable.
    2. Transform the string encoding into a set. This is a set of sets, where each inner set represents a clause.
    3. Check for set equivalence.
    """
    cnf_expr = str(cnf_expr).strip()
    expected = str(expected).strip()

    got_symbols = {}
    got_cnt = 1
    expected_symbols = {}
    expected_cnt = 1

    # 1. Replace all symbols in both CNFs with X_i, where each X_i corresponds to a variable
    for c in cnf_expr:
        if c.isalpha() and c not in got_symbols:
            got_symbols[c] = f"X{got_cnt}"
            got_cnt += 1
    
    for c in expected:
        if c.isalpha() and c not in expected_symbols:
            expected_symbols[c] = f"X{expected_cnt}"
            expected_cnt += 1

    for k, v in got_symbols.items():
        cnf_expr = cnf_expr.replace(k, v)

    for k, v in expected_symbols.items():
        expected = expected.replace(k, v)

    # 2. Transform the string encoding into a set
    cnf_expr = [set(var.strip().strip('(').strip(')') for var in clause.strip().strip('(').strip(')').split('|')) for clause in cnf_expr.split('&')]
    expected = [set(var.strip().strip('(').strip(')') for var in clause.strip().strip('(').strip(')').split('|')) for clause in expected.split('&')]

    cnf_expr = set([frozenset(clause) for clause in cnf_expr])
    expected = set([frozenset(clause) for clause in expected])

    # 3. Check for set equivalence
    return cnf_expr == expected


# Example usage
if __name__ == "__main__":
    
    data = json.load(open('data.json'))
    n = len(data)
    correct = 0

    for i, sentence in enumerate(data):
        cnf_expr = text_to_cnf(sentence['statement'])

        if cnf_expr:
            print(f"\nFinal CNF Expression for sentence {i+1}:")
            print(f"Output: {cnf_expr}")
            print(f"Expected: {sentence['cnf_expr']}")

            if evaluate(cnf_expr, sentence['cnf_expr']):
                correct += 1
                print("Correct!")
            else:
                print("Incorrect!")

            print("\n")
    
    print(f"Accuracy: {correct}/{n}")