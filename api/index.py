import sys
import os

# Tambahkan direktori root ke path agar modul services dan app dapat diimpor dengan sempurna
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
