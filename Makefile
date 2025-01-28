VENV = .venv
UV = uv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

setup:
	@echo "Installing dependencies..."
	$(UV) venv $(VENV)
	$(VENV)/bin/activate && $(UV) pip install -r requirements.txt
	@echo "Installation complete!"

clean:
	@echo "Removing virtual environment..."
	@rm -rf $(VENV)
	@echo "Virtual environment removed!"

run:
	@echo "Starting FastAPI server..."
	$(PYTHON) -m uvicorn app.main:app --reload

format:
	@echo "🎨 Formatting code with Black..."
	$(VENV)/bin/black .

lint:
	@echo "🔍 Running Ruff lint..."
	$(VENV)/bin/ruff check .

test:
	@echo "Running tests with pytest..."
	$(VENV)/bin/pytest --maxfail=1 --disable-warnings --cov=app --cov-report=term-missing

check: format lint test
	@echo "✅ Code is ready to commit!"

help:
	@echo "Available commands:"
	@echo "  make install      -> Install dependencies in a virtualenv"
	@echo "  make clean        -> Remove the virtualenv"
	@echo "  make run          -> Start the FastAPI server"
	@echo "  make format       -> Format the code with Black"
	@echo "  make lint         -> Lint the code with Ruff"
	@echo "  make test         -> Run tests with pytest"
	@echo "  make check        -> Run all checks (format, lint, type-check, test, security, bandit)"

.PHONY: install clean run format lint type-check test security bandit check help
