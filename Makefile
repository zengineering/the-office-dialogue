DATA_DIR = data

.PHONY: install
install: requirements.txt
	pip install -r requirements.txt
	python -m textblob.download_corpora

.PHONY: test
test:
	python -m pytest

.PHONY: download
download:
	python -m officequotes download -o $(DATA_DIR)/json
	python -m officequotes corrections $(DATA_DIR)/json

.PHONY: database
database: 
	python -m officequotes create_db $(DATA_DIR)/json \
	-o $(DATA_DIR)/officequotes.sqlite

.PHONY: analysis
analysis:
	python -m officequotes analyze $(DATA_DIR)/officequotes.sqlite \
	-o $(DATA_DIR)/analysis.json

.PHONY: all
all: download database analysis
