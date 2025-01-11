# Define variables
ENV_NAME = lang2cnf
REQ_FILE = requirements.txt
API_KEY_ENV_VAR = OPENAI_API_KEY
PYTHON_SCRIPT = lang2cnf.py

# Default target
.PHONY: all
all: setup run

# Create and activate the virtual environment using Micromamba
.PHONY: create-env
create-env:
	micromamba create -n $(ENV_NAME) python=3.9 -y
	@echo "Environment $(ENV_NAME) created successfully."

# Install dependencies
.PHONY: install
install:
	micromamba activate $(ENV_NAME) && micromamba install -n $(ENV_NAME) --file $(REQ_FILE) -y
	@echo "Dependencies installed successfully in $(ENV_NAME)."

# Export ChatGPT API key
.PHONY: set-api-key
set-api-key:
	@if [ -z "$$$(echo $$$(grep $(API_KEY_ENV_VAR) ~/.zshrc || true))" ]; then \
		echo 'export $(API_KEY_ENV_VAR)="$$(read -p "Enter your ChatGPT API Key: " key && echo $$key)"' >> ~/.zshrc; \
		source ~/.zshrc; \
		echo "API key added to environment."; \
	else \
		echo "API key already exists in your environment."; \
	fi

# Run the Python script
.PHONY: run
run:
	micromamba run -n $(ENV_NAME) python $(PYTHON_SCRIPT)

# Clean the environment
.PHONY: clean
clean:
	micromamba remove -n $(ENV_NAME) --all -y
	@echo "Environment $(ENV_NAME) removed successfully."

# Setup all (create-env + install + set-api-key)
.PHONY: setup
setup: create-env install set-api-key
	@echo "Setup complete. Ready to run."
