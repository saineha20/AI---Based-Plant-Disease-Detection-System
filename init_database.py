# scripts/init_database.py
"""
Script to initialize and seed the SQLite database for Kisan Mitra.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from backend.database import init_database, query_all_diseases

def main():
    print("=" * 60)
    print("KISAN MITRA - SQLite Database Initialization")
    print("=" * 60)
    init_database()
    diseases = query_all_diseases(lang="en")
    print(f"Database successfully initialized with {len(diseases)} conditions.")
    for d in diseases[:5]:
        print(f"  - {d['crop']} : {d['disease_name']} ({d['pathogen_type']})")
    print("  ... and 33 more conditions.")
    print("Database path: data/kisan_mitra.db")

if __name__ == "__main__":
    main()

