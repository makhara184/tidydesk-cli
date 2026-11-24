# TidyDesk CLI

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Zero Dependencies](https://img.shields.io/badge/Dependencies-Stdlib%20Only-22c55e?style=flat-square)

A lightweight Python CLI utility that organizes cluttered directories (such as `Downloads` or `Desktop`), detects exact duplicate files via SHA-256 hashing, and supports full one-command undo.

## Usage

```bash
# Preview changes safely
python3 tidydesk.py ~/Downloads --dry-run

# Organize files into categorized folders
python3 tidydesk.py ~/Downloads

# Undo the last organization run
python3 tidydesk.py ~/Downloads --undo

# Find duplicate files by SHA-256 hash
python3 tidydesk.py ~/Downloads --duplicates
```

## Run Tests
```bash
python3 -m unittest discover -s tests
```

## License
MIT License — see [LICENSE](LICENSE).
