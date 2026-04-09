# Vector DB — Milvus Lite + BGE-small-en-v1.5

Semantic search layer that maps natural language queries to service type names (used as MongoDB collection names by the IoT engine).

**Model:** `BAAI/bge-small-en-v1.5` — 33M params, 384-dim, ~130 MB  
**Storage:** Milvus Lite (local `.db` file, no server required)  
**Index:** 500 service types from `assets/Services_description_V2.txt`

---

## Installation

From the `backend/` directory:

```bash
pip install "pymilvus[milvus_lite]>=2.4.0" "sentence-transformers>=2.7.0"
```

Or install everything at once:

```bash
pip install -r requirements_pip.txt
```

---

## Build the Index

Run from this directory (`backend/src/vector_db/`):

```bash
# First time — builds the index
python create_vectordb.py

# Force a full rebuild (drops and recreates the collection)
python create_vectordb.py --force
```

This will:
1. Download `BAAI/bge-small-en-v1.5` from HuggingFace (~130 MB, cached after first run)
2. Parse 500 service descriptions from `assets/Services_description_V2.txt`
3. Encode them in batches of 64 and insert into Milvus Lite
4. Save the index to `milvus_lite.db` in this directory

Expected output:
```
Indexing services: 100%|██████████| 8/8
INFO Indexed 500 services into 'services'.
```

Running again without `--force` is a no-op:
```
INFO Collection 'services' already has 500 entities. Skipping index build.
```

---

## Test It

Open a Python shell from `backend/src/vector_db/`:

```python
from vector_database import vector_search, vector_db_push_batch

# Verify the index exists (skip rebuild if already done)
vector_db_push_batch()

# Run a search — returns top 3 matching service type names
results = vector_search("I need a coffee shop", limit=3)
print(results)
# ['coffee shop', 'convenience store', 'deli shop']

results = vector_search("looking for a pharmacy", limit=3)
print(results)
# ['pharmacy', 'convenience store', 'gourmet grocery store']

results = vector_search("I want pizza", limit=3)
print(results)
# ['pizza restaurant', 'delivery chinese restaurant', 'deli shop']

results = vector_search("I need a doctor", limit=3)
print(results)
# ['medical clinic', 'medical center', 'optometrist']

results = vector_search("gym to work out", limit=3)
print(results)
# ['gym', 'fitness center', 'rock climbing gym']
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `MILVUS_URI` | `./milvus_lite.db` (next to this file) | Path for local Milvus Lite DB, or `http://milvus:19530` for full Milvus |

To use a custom path:

```bash
MILVUS_URI=/data/milvus.db python create_vectordb.py
```

---

## Files

```
vector_db/
├── vector_database.py          # Core logic: indexing + search
├── create_vectordb.py          # Standalone script to build the index
├── milvus_lite.db              # Generated — Milvus Lite database file (gitignored)
├── assets/
│   └── Services_description_V2.txt   # 500 service type descriptions
└── vectorDB_files_v2/          # Old HNSW index files (no longer used)
```

---

## Notes

- The `embeddings.position_ids UNEXPECTED` warning on model load is harmless — it's a known quirk of how sentence-transformers loads BGE models.
- The `milvus_lite.db` file is generated locally and should not be committed to git.
- In Docker, the DB file is persisted via a named volume (`milvus_data`) and the path is set via `MILVUS_URI`.
