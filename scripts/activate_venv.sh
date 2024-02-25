#!/bin/sh

pwd=$(pwd)
PYTHON_VERSION=$(python -V 2>&1)

if [ -z "${VIRTUAL_ENV}" ]; then  # check for venv env var

  if [ -d "${pwd}/.venv" ]; then  # check for .venv folder
    echo "${PYTHON_VERSION} virtual environment already exists at ${pwd}/.venv"
  else
    echo "Setting up a new ${PYTHON_VERSION} virtual environment at ${pwd}/.venv..."
    python -m venv .venv
  fi
  echo "Run \`source .venv/bin/activate\` before continuing" && exit 1
else
  echo "${PYTHON_VERSION} virtual environment is already activated in ${pwd}"
fi