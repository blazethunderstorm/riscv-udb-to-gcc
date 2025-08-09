VENV_DIR := venv
PYTHON := $(VENV_DIR)/bin/python3
PIP := $(VENV_DIR)/bin/pip
UDB_PATH ?= udb/orn.yaml
OUTPUT_DIR ?= output

.PHONY: setup run test clean

setup:
	python3 -m venv $(VENV_DIR)
	. $(VENV_DIR)/bin/activate && $(PIP) install -r requirements.txt

run:
	$(PYTHON) generate_gcc_md.py --udb_path $(UDB_PATH) --output_dir $(OUTPUT_DIR)

test:
	$(PYTHON) -m pytest tests/

clean:
	rm -rf $(VENV_DIR) $(OUTPUT_DIR) __pycache__ .pytest_cache
	find . -type d -name '__pycache__' -exec rm -r {} +
