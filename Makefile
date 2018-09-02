.PHONY
install: requirements.txt
	pip install -r requirements.txt
	pip install officequotes/

.PHONY
test:
	python -m pytest

.PHONY
download: install
	python -m officequotes download


.PHONY
corrections: officequotes.sqlite
	python -m officequotes download $<

