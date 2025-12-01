import json
import glob
import sys

errors = False

for f in glob.glob('src/data/prompts/*.json'):
    try:
        json.load(open(f, encoding='utf-8'))
        print('OK:', f)
    except Exception as e:
        print('BAD JSON:', f, e)
        errors = True

for f in glob.glob('src/data/config/*.json'):
    try:
        json.load(open(f, encoding='utf-8'))
        print('OK:', f)
    except Exception as e:
        print('BAD JSON:', f, e)
        errors = True

if errors:
    sys.exit(1)
