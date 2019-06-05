setup:
	-pyenv virtualenv 3.6.7 async-http
	pyenv local async-http
	pip install -r requirements-tests.txt

test:
	python -m pytest -s tests
