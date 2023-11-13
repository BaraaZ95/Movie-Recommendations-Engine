import sys
from pathlib import Path # if you haven't already done so
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[0]
sys.path.append(str(root))
# Project directories 
PACKAGE_ROOT = root


with open(PACKAGE_ROOT / "VERSION") as version_file:
    __version__ = version_file.read().strip()

    
