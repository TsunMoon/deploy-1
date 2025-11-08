#!/usr/bin/env python3
"""
Script to run and test the Netflix dataset loader
"""
import sys
import os
import importlib.util
import json

# Load the netflix_dataset module directly without importing the services package
module_path = os.path.join(os.path.dirname(__file__), 'netflix_dataset.py')
spec = importlib.util.spec_from_file_location("netflix_dataset", module_path)
netflix_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(netflix_module)

NetflixDatasetLoader = netflix_module.NetflixDatasetLoader


def main():
    """Load and display Netflix data"""
    print("Loading Netflix dataset...")
    
    # Load Netflix data
    loader = NetflixDatasetLoader()
    movies = loader.load_netflix_dataset()
    
    print(f"\nSuccessfully loaded {len(movies)} Netflix titles\n")

    print(movies)

    # Optionally save to JSON file
    save_to_file = input("\n\nSave all data to JSON file? (y/n): ").strip().lower()
    if save_to_file == 'y':
        with open('netflix_data.json', 'w') as f:
            json.dump(movies, f, indent=2)
        print(f"Data saved to netflix_data.json")


if __name__ == "__main__":
    main()
