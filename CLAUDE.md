# Testing
- Use pytest

# Python
- We use python 3.13
- Run python from a venv. This can be loaded with the following commands:
  - `python3 -m venv /Users/caleb/python/venv`
  - `source /Users/caleb/python/venv/bin/activate`

# Workflow
- Most changes should be accompanied by test changes or improved test coverage
- Run tests when making changes to make sure nothing breaks
- If asked to commit changes with git, split commits up into smaller, incremental changes when possible to aid later debugging/bisecting

# IMPORTANT
This repository contains data visualization and mapping scripts and the accompanying data needed for these scripts. These data files can be MASSIVE so be very careful when reading files so we don't use up all of our LLM API tokens and incur a large financial cost. 

The files in `census/` contain mapping shapefiles, and should almost never be read.

The files in `noaa/` contain weather data, and can be very large. Before reading these files, YOU MUST check the file size first, and if it's larger than a couple hundred lines, ONLY read the start of the file using `head`. This is VERY IMPORTANT to remember. Some files in this directory are small and fine to read. But others, including but not limited to `dly-tmax-normal.txt` and `zipcodes-normals-stations.txt` are very long and it would be VERY BAD to read these files completely.