
# turns requirements.in into the lockfile requirements.txt
# requires a venv to be active in order to use `pip-compile`
# this should only be used by a developer updating the lockfile
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

run-claude:
	python src/gpt-cli/main.py -m "claude-3-haiku-20240307"

format:
	python -m black -t py312 .