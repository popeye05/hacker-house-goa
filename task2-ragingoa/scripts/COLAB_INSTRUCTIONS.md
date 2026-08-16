# Google Colab MS MARCO Indexing Instructions

## Quick Start

1. **Open Google Colab**
   - Go to https://colab.research.google.com/
   - Click "File" → "New notebook"

2. **Upload the script**
   - Copy the contents of `colab_index_msmarco.py`
   - Or run each step below as separate cells

3. **Set Runtime to GPU** (optional but faster)
   - Click "Runtime" → "Change runtime type"
   - Select "T4 GPU" (free tier)
   - Click "Save"

---

## Step-by-Step Cells

### Cell 1: Install Dependencies
```python
!pip install -q qdrant-client datasets sentence-transformers tqdm
```

### Cell 2: Import and Configure (SECURE METHOD)
```python
from datasets import load_dataset
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from tqdm.auto import tqdm
import time
from google.colab import userdata

# 🔐 SECURE: Get credentials from Colab Secrets
QDRANT_URL = userdata.get('QDRANT_URL')
QDRANT_API_KEY = userdata.get('QDRANT_API_KEY')

QDRANT_COLLECTION = "msmarco_xi_english"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Fast English model
VECTOR_SIZE = 384
BATCH_SIZE = 128

# Full English subset from MS MARCO-XI (~8.8M passages)
MAX_DOCUMENTS = None  # Process entire English collection
LANGUAGE_FILTER = "en"

print("✅ Configuration loaded")
print("📊 Will index FULL English MS MARCO-XI collection")
print("⏱️  Estimated time: 6-10 hours (may need multiple Colab sessions)")
```

**How to add secrets in Colab:**
1. Click the 🔑 (key) icon in the left sidebar
2. Click "Add new secret"
3. Add these two secrets:
   - Name: `QDRANT_URL`, Value: `your_qdrant_url`
   - Name: `QDRANT_API_KEY`, Value: `your_qdrant_api_key` (must have Read+Write permissions)
4. Enable access for this notebook

### Cell 3: Initialize Clients
```python
print("🔧 Initializing Qdrant client...")
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=120
)

print("🤖 Loading embedding model...")
model = SentenceTransformer(EMBEDDING_MODEL)
print("✅ Ready!")
```

### Cell 4: Create Collection
```python
print(f"📦 Creating collection: {QDRANT_COLLECTION}")
if client.collection_exists(QDRANT_COLLECTION):
    print(f"⚠️  Collection already exists. Recreating...")
    client.delete_collection(QDRANT_COLLECTION)

client.create_collection(
    collection_name=QDRANT_COLLECTION,
    vectors_config=models.VectorParams(
        size=VECTOR_SIZE,
        distance=models.Distance.COSINE,
    )
)
print("✅ Collection created")
```

### Cell 5: Load Dataset
```python
print("📚 Loading MS MARCO-XI English dataset...")
dataset = load_dataset(
    "unicamp-dl/mmarco",  # MS MARCO-XI multilingual
    "english",            # English subset only
    split="collection",   # Full passage collection
    streaming=True        # Memory efficient
)
print("✅ Dataset loaded (streaming mode)")
print("📊 Dataset: MS MARCO-XI English (~8.8M passages)")
```

### Cell 6: Index Data (Main Processing)
```python
print("🚀 Starting indexing...")
batch_texts = []
batch_ids = []
batch_payloads = []
total_indexed = 0
point_id = 0
start_time = time.time()

for item in tqdm(dataset):
    # Extract text from MS MARCO-XI format
    passage_text = item.get("text", "")
    if not passage_text or len(passage_text.strip()) == 0:
        continue
    
    batch_texts.append(passage_text)
    batch_ids.append(point_id)
    batch_payloads.append({
        "text": passage_text,
        "source": "msmarco_xi_english",
        "doc_id": item.get("docid", "")
    })
    point_id += 1
    
    if len(batch_texts) >= BATCH_SIZE:
        embeddings = model.encode(
            batch_texts,
            batch_size=BATCH_SIZE,
            show_progress_bar=False,
            normalize_embeddings=True
        )
        
        client.upload_points(
            collection_name=QDRANT_COLLECTION,
            points=[
                models.PointStruct(
                    id=batch_ids[i],
                    vector=embeddings[i].tolist(),
                    payload=batch_payloads[i]
                )
                for i in range(len(batch_ids))
            ],
            wait=False
        )
        
        total_indexed += len(batch_texts)
        batch_texts = []
        batch_ids = []
        batch_payloads = []
        
        if total_indexed % 1000 == 0:
            elapsed = time.time() - start_time
            print(f"   📊 Indexed: {total_indexed:,} | Rate: {total_indexed/elapsed:.1f} docs/sec")
    
    if MAX_DOCUMENTS and total_indexed >= MAX_DOCUMENTS:
        break

# Upload remaining
if batch_texts:
    embeddings = model.encode(batch_texts, batch_size=BATCH_SIZE, normalize_embeddings=True)
    client.upload_points(
        collection_name=QDRANT_COLLECTION,
        points=[models.PointStruct(id=batch_ids[i], vector=embeddings[i].tolist(), payload=batch_payloads[i])
                for i in range(len(batch_ids))],
        wait=True
    )
    total_indexed += len(batch_texts)

print(f"\n✅ DONE! Indexed {total_indexed:,} passages in {(time.time()-start_time)/60:.1f} minutes")
```

### Cell 7: Test Retrieval
```python
print("🧪 Testing retrieval...")
test_query = "what is a corporation?"
query_embedding = model.encode(test_query, normalize_embeddings=True)

results = client.search(
    collection_name=QDRANT_COLLECTION,
    query_vector=query_embedding.tolist(),
    limit=3
)

print(f"\nQuery: '{test_query}'")
for i, result in enumerate(results, 1):
    print(f"\n{i}. Score: {result.score:.4f}")
    print(f"   {result.payload['text'][:200]}...")
```

---

## Important Notes

1. **Dataset Size**
   - Full English MS MARCO-XI: ~8.8 million passages
   - Expected indexing time: 6-10 hours on Colab free tier
   - May require multiple Colab sessions (12-hour limit)

2. **For Long Indexing (>12 hours)**
   - Colab Pro recommended (24-hour sessions, faster GPUs)
   - Or run in chunks with checkpointing (see below)

3. **Checkpointing Strategy (if needed)**
   ```python
   # Before the loop, check existing count
   try:
       collection_info = client.get_collection(QDRANT_COLLECTION)
       point_id = collection_info.points_count
       print(f"✅ Resuming from document {point_id:,}")
   except:
       point_id = 0
       print("🆕 Starting fresh")
   ```

4. **After Indexing**
   - Update backend `.env`:
     ```
     QDRANT_COLLECTION=msmarco_xi_english
     ```
   - Redeploy backend on Render

5. **Expected Time**
   - 1M docs: ~1 hour
   - 5M docs: ~5 hours
   - 8.8M docs (full): ~8-10 hours

---

## Troubleshooting

**Out of Memory?**
- Reduce `BATCH_SIZE` to 32 or 16

**Connection Timeout?**
- Increase `timeout=300` in QdrantClient

**Colab Disconnects?**
- Save checkpoint every 100K documents
- Resume from last checkpoint

**Need to Resume?**
Add this before the loop:
```python
# Get current count
collection_info = client.get_collection(QDRANT_COLLECTION)
point_id = collection_info.points_count
print(f"Resuming from document {point_id}")
```
