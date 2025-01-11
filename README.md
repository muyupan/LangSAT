LangSAT

Lang2CNF
Lang2CNF is the first part of the LangSAT project. It translates natural language statements into Conjunctive Normal Form (CNF), a crucial representation for solving logical and computational problems. This tool leverages APIs such as ChatGPT and other necessary libraries to process and transform inputs efficiently.
  
Prerequisites
Before you begin, it is recommended to you to have the following installed:
	•	Micromamba (a lightweight Conda alternative)
	•	Python 3.9 or higher
	•	A valid OpenAI API key for ChatGPT integration.

Installation

Step 1: Clone the Repository
Clone the Lang2CNF repository to your local machine:

        git clone git@github.com:muyupan/LangSAT.git
        cd LangSAT/lang2cnf

Step 2: Set Up the Environment
Use Micromamba to create and activate the virtual environment:

        micromamba create -n lang2cnf python=3.9 -y
        micromamba activate lang2cnf

Step 3: Install Dependencies
Install the necessary packages from the requirements.txt file:

        micromamba install -n lang2cnf --file requirements.txt -y

Step 4: Configure the ChatGPT API Key
Set up your OpenAI API key for the ChatGPT integration, add the API key to your shell configuration:

        export OPENAI_API_KEY="your-api-key-here"
        
Reload shell after

Usage

Run the Program

To translate natural language to CNF:
 
	make run

The lang2cnf.py script processes natural language statements and outputs their CNF representations.

Sample Usage

Running the Program, to translate a natural language statement into CNF:

	python lang2cnf.py "The circus has a ferris wheel or the circus has a rollercoaster. The circus does not have a carousel if and only if the circus has a ferris wheel and the circus has a rollercoaster. If the circus does not have a carousel, then the circus has a trapese. The circus does not have a trapese and the circus has a rollercoaster."

CNF Output: 

Sentence #1: The circus has a ferris wheel or the circus has a rollercoaster.
Model Output: Or(P, Q)
Parsed Expression: P | Q
CNF Expression: P | Q
-----
Sentence #2: The circus does not have a carousel if and only if the circus has a ferris wheel and the circus has a rollercoaster.
Model Output: Equivalent(Not(R), And(P, Q))
Parsed Expression: Equivalent(~R, P & Q)
CNF Expression: (P | R) & (Q | R) & (~P | ~Q | ~R)
-----
Sentence #3: If the circus does not have a carousel, then the circus has a trapese.
Model Output: Implies(Not(R), S)
Parsed Expression: Implies(~R, S)
CNF Expression: R | S
-----
Sentence #4: The circus does not have a trapese and the circus has a rollercoaster.
Model Output: And(Not(S), Q)
Parsed Expression: Q & ~S
CNF Expression: Q & ~S
-----

Final CNF Expression (Simplified):
Q & R & ~P & ~S
