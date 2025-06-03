# General Guidelines for est-lawyer

## Key Features of the solution
### Data retrieval from Estonian law repository
- Search for legal acts using the Riigi Teataja API
- Store legal document metadata in a SQLite database
- Retrieve full document text

## Documentation (Docstrings/Comments)
* **README.md** when adding new functionality, new option or use case. Update user guide accordingly.
* **requirements.txt** when importing new module that requires pip install, add this to requirements.txt
* **.env.example** when introducing new environment variable, add the variable to .env.example
* **Python Docstrings:** Add clear, concise PEP 257 compliant docstrings to all new Python functions, classes, and methods, explaining their purpose, arguments (`Args:`), and return values (`Returns:`). Use English.
* **Comments:**
   * **Evaluate all existing comments.** Remove comments that are unnecessary, state the obvious, or simply restate what the code does, regardless of their original language.
   * Add **new, concise English comments** only where necessary to explain complex or non-obvious logic, assumptions, or important decisions.

## Configuration

* **No Hardcoding:** Avoid hardcoding URLs, file paths, or sensitive values directly in functions or modules. Use environment variables for that.

## Dependencies & Imports

* **Python Imports:** Group imports standardly: 1. Standard library, 2. Third-party libraries, 3. Local application modules. Use absolute imports from the project root where clear, or relative imports (`from . import utils`) within blueprints/modules.
* **New Python Dependencies:** If adding a new Python dependency is required, add it to `requirements.txt`.

## Error Handling & Logging

## Code Style & Formatting
* **Python:** Strictly follow the PEP 8 style guide. Use `snake_case` for variable and function names.

## Context Management & Interaction
* **Refactor suggestion:** If single file becomes too large, notify user about need to refactor`