import os
import sys

RUNTESTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(
    RUNTESTS_DIR, '..', 'src'))
sys.path.insert(0, os.path.join(BASE_DIR, 'argyle_task'))
