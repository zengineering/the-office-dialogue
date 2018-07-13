import sys
from pathlib import Path

test_path = Path(__file__).resolve().parent

sys.path.insert(0, str(test_path.parent/'officequotes'))

import parse
import dataclasses
import download
