install: requirements.txt
	pip install -r requirements.txt
	pip install officequotes/

test: install
	python -m pytest

download: install
	python -m officequotes download
