

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


 
  
