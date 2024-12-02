#!/bin/bash

# Read the requirements file and install each package
while IFS= read -r package; do
    pip install "$package" || echo "Failed to install $package"
done < requirements.txt

pip install geopy;

python -m spacy download en_core_web_lg 
python -m spacy download en_core_web_sm 
python -m spacy download en
cd src/vector_db; python create_cectordb.py;