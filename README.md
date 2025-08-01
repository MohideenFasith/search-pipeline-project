# Search Engineer Take-Home Project

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Load Data to Vector Store
```bash
python init.py
```

## Retrieve Candidates for a Query
```bash
python retrieve.py
```

## Evaluate a Query
```bash
python evaluate.py
```

## Submit Final Graded Set
```bash
python grade_submit.py
```

## Notes
- Uses TurboPuffer with `voyage-3` embeddings
- `retrieve.py` includes hard filtering from `.yml` config
- Ready for submission via `/grade` API
- GPT-4.1 reranking logic can be added as a post-processing filter
