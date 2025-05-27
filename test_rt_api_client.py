import sys
import os
from src.rt_api_client import fetch_acts_list

def main():
    # Test parameters
    api_params = {
        'leht': 1,
        'limiit': 10,
        'dokument': 'seadus',
        'kehtiv': '2024-05-01'
    }

    # Fetch acts list
    result = fetch_acts_list(api_params)

    # Print result
    if result:
        print("API Response received successfully!")
        print(f"Number of results: {len(result)}")
    else:
        print("Failed to retrieve data from API.")

if __name__ == "__main__":
    main()