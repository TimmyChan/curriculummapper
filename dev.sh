#!/usr/bin/bash

source .venv/bin/activate
pytest > pytest.log
cat pytest.log
flake8 $PWD --statistics --output-file flake8.log
cat flake8.log