# API Operations

This microagent is triggered by keywords related to API operations in est-lawyer.

## Fetching Legal Acts

To fetch legal acts from the Riigi Teataja API, use the `data_retriever.py` script:
```bash
python src/data_retriever.py
```

## API Client Usage

You can use the API client programmatically:
```python
from src.rt_api_client import get_all_acts_for_query

params = {
    'dokument': 'seadus',
    'limiit': 100,
}

all_acts = get_all_acts_for_query(params)
print(f"Total acts retrieved: {len(all_acts)}")
```