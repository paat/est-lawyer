import sys
import os
import json
from src.rt_api_client import fetch_acts_list, get_all_acts_for_query

def main():
    print("Testing fetch_acts_list function:")
    # Test parameters for single page fetch
    api_params = {
        'leht': 1,
        'limiit': 10,
        'dokument': 'seadus'
    }

    # Fetch acts list
    result = fetch_acts_list(api_params)

    # Print result
    if result:
        print("API Response received successfully!")
        print("Raw response structure:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # Try to determine the correct key for the results
        possible_keys = ['results', 'data', 'hits', 'items', 'documents', 'oigusaktid']
        found_key = None
        for key in possible_keys:
            if key in result and isinstance(result[key], list):
                found_key = key
                break

        if found_key:
            print(f"\nFound results under key '{found_key}': {len(result[found_key])}")
        else:
            print("\nCould not determine the key for the results list. Available keys:")
            print(list(result.keys()))
    else:
        print("Failed to retrieve data from API.")

    print("\nTesting get_all_acts_for_query function:")
    # Test parameters for fetching all pages
    initial_params = {
        'limiit': 10,
        'dokument': 'seadus'
    }

    # Fetch all acts for the query
    all_acts = get_all_acts_for_query(initial_params)

    # Print result
    if all_acts:
        print("Successfully retrieved all acts for the query!")
        print(f"Total number of acts retrieved: {len(all_acts)}")
        # Print first act as a sample
        if all_acts:
            print("\nSample act:")
            print(json.dumps(all_acts[0], indent=2, ensure_ascii=False))
    else:
        print("Failed to retrieve any acts for the query.")

if __name__ == "__main__":
    main()