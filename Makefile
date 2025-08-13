ASSETS_DIR := assets/
SRC_DIR := src/
OUTPUT_DIR := build/
TEMPLATES_DIR := templates/ 

install-deps:
	python3 -m venv .venv
	. .venv/bin/activate
	python3 -m pip install -r scripts/requirements.txt

.PHONY: build
build: src
	. .venv/bin/activate
	python3 scripts/builder.py --src-dir $(SRC_DIR) --assets-dir $(ASSETS_DIR) --templates-dir $(TEMPLATES_DIR) --output-dir $(OUTPUT_DIR)

serve:
	python3 -m http.server --dir build/

clean:
	rm -rf build/