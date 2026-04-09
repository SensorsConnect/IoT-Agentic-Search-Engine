import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vector_database import vector_db_push_batch

if __name__ == "__main__":
    force = "--force" in sys.argv
    vector_db_push_batch(force_rebuild=force)
