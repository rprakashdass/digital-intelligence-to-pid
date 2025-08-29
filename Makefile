# Makefile for P&ID to Digital MVP

.PHONY: help setup run-backend format test clean

help:
	@echo "Available commands:"
	@echo "  setup         - Creates a virtual environment and installs dependencies"
	@echo "  run-backend   - Starts the FastAPI backend server"
	@echo "  format        - Formats the code (requires black and isort)"
	@echo "  test          - Runs tests (not implemented in MVP)"
	@echo "  clean         - Removes temporary files and caches"

setup:
	@echo "Creating virtual environment in .venv..."
	python -m venv .venv
	@echo "Virtual environment created. Activate it and then run: pip install -r backend/requirements.txt"
	@echo "On Windows: .venv\\Scripts\\activate.bat"
	@echo "On macOS/Linux: source .venv/bin/activate"

run-backend:
	@echo "Starting FastAPI server on http://localhost:8000"
	uvicorn backend.main:app --reload --port 8000

# These are placeholders as the tools are not dependencies yet
format:
	@echo "Formatting code with black and isort..."
	# pip install black isort
	# black backend/
	# isort backend/

test:
	@echo "Testing not implemented for MVP."
	# pip install pytest
	# pytest

clean:
	@echo "Cleaning up..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@rm -rf .venv
	@rm -rf temp_images
