
# turns requirements.in into the lockfile requirements.txt
# requires a venv to be active in order to use `pip-compile`
lock:
	chmod +x ./scripts/activate_venv.sh; ./scripts/activate_venv.sh && \
	python -m pip install -U pip pip-tools && \
	pip-compile --generate-hashes --output-file requirements.txt requirements.in


# install python packages from lockfile
.PHONY: install
install:
	python -m pip install -U pip && \
	python -m pip install --require-hashes -r requirements.txt


run:
	python src/gpt-cli/main.py

format:
	python -m black -t py312 .