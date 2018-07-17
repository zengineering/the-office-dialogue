import sys
from pathlib import Path

'''
Hackery to make sure pytest can find the module under test
'''

# Import package modules.
# Assumes project structure:
#
# top/
#   officequotes/
#       parse.py
#       database.py
#       ...
#   tests/
#       test_parse.py
#       test_database.py
#       ...

test_path = Path(__file__).resolve().parent
sys.path.insert(0, str(test_path.parent/'officequotes'))

import download
import database
