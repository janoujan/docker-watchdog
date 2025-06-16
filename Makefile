test:
	 PYTHONPATH=. pytest --cov=src tests/

setup:
	 python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt pytest-cov

clean:
	 find . -type f -name '*.pyc' -delete
	 find . -type d -name '__pycache__' -exec rm -r {} +
	 rm -rf .pytest_cache .coverage htmlcov

cov:
	 PYTHONPATH=. pytest --cov=src --cov-report=html tests/
	 @echo "Le rapport HTML est disponible dans htmlcov/index.html"

open-cov:
ifeq ($(shell uname), Linux)
	 @xdg-open htmlcov/index.html
else ifeq ($(shell uname), Darwin)
	 @open htmlcov/index.html
else
	 @wslview htmlcov/index.html
endif
