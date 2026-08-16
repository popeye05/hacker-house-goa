"""
Google Colab script to index full MS MARCO dataset to Qdrant Cloud
Uses intfloat/multilingual-e5-small embedding model

Instructions:
1. Upload this file to Google Colab
2. Set your Qdrant credentials in the variables below
3. Run all cells
4. Wait for indexing to complete (~2-3 hours for full dataset)
"""

# ============================================
# STEP 1: Install dependencies
# ============================================
# !pip install -q qdrant-client datasets sentence-transformers tqdm

# ============================================
# STEP 2: Configuration (SECURE METHOD)
# ============================================
import os
from datasets import load_dataset
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from tqdm.auto import tqdm
import time

try:
    from google.colab import userdata
    # 🔐 SECURE: Get credentials from Colab Secrets
    # To add secrets: Click 🔑 icon in left sidebar → Add new secret
    QDRANT_URL = userdata.get('QDRANT_URL')
    QDRANT_API_KEY = userdata.get('QDRANT_API_KEY')
    print("✅ Using Colab Secrets (secure)")
except:
    # Fallback for non-Colab environments (e.g., local testing)
    QDRANT_URL = os.getenv("QDRANT_URL", "YOUR_QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "YOUR_QDRANT_API_KEY")
    print("⚠️  Using environment variables or hardcoded values")

QDRANT_COLLECTION = "msmarco_xi"  # Keep same as your demo collection
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"  # Multilingual for Hindi
VECTOR_SIZE = 384
BATCH_SIZE = 128

# 5M Hindi passages from MS MARCO-X
MAX_DOCUMENTS = 5000000  # 5 million passages
LANGUAGE_FILTER = "hi"  # Hindi passages

# ============================================
# STEP 3: Initialize clients
# ============================================
print("🔧 Initializing Qdrant client...")
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=120
)

print("🤖 Loading embedding model...")
model = SentenceTransformer(EMBEDDING_MODEL)

# ============================================
# STEP 4: Create collection
# ============================================
print(f"📦 Creating collection: {QDRANT_COLLECTION}")
if client.collection_exists(QDRANT_COLLECTION):
    print(f"⚠️  Collection '{QDRANT_COLLECTION}' already exists. Deleting...")
    client.delete_collection(QDRANT_COLLECTION)

client.create_collection(
    collection_name=QDRANT_COLLECTION,
    vectors_config=models.VectorParams(
        size=VECTOR_SIZE,
        distance=models.Distance.COSINE,
    ),
    optimizers_config=models.OptimizersConfigDiff(
        indexing_threshold=10000,
    )
)
print("✅ Collection created")

# ============================================
# STEP 5: Load MS MARCO-X dataset (Hindi)
# ============================================
print("📚 Loading MS MARCO-X dataset (Hindi)...")
dataset = load_dataset(
    "ai4bharat/MSMARCO-X",  # MS MARCO-X dataset
    "hindi",                # Hindi subset
    split="train",          # Training split
    streaming=True          # Memory efficient
)
print("✅ Dataset loaded (streaming mode)")

# ============================================
# STEP 6: Index passages
# ============================================
print("🚀 Starting indexing process...")
print(f"   Batch size: {BATCH_SIZE}")
print(f"   Embedding model: {EMBEDDING_MODEL}")
print(f"   Max documents: {MAX_DOCUMENTS if MAX_DOCUMENTS else 'ALL'}")

batch_texts = []
batch_ids = []
batch_payloads = []
total_indexed = 0
point_id = 0

start_time = time.time()

for item in tqdm(dataset):
    # Extract passage text from MS MARCO-X format
    passage_text = item.get("passage", "")
    
    if not passage_text or len(passage_text.strip()) == 0:
        continue
    
    # Prepare batch
    batch_texts.append(passage_text)
    batch_ids.append(point_id)
    batch_payloads.append({
        "text": passage_text,
        "source": "msmarco_x",
        "language": "hi",
        "query": item.get("query", "")
    })
    point_id += 1
    
    # Upload batch when full
    if len(batch_texts) >= BATCH_SIZE:
        # Generate embeddings
        embeddings = model.encode(
            batch_texts,
            batch_size=BATCH_SIZE,
            show_progress_bar=False,
            normalize_embeddings=True
        )
        
        # Upload to Qdrant
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
        
        # Clear batch
        batch_texts = []
        batch_ids = []
        batch_payloads = []
        
        # Progress update
        if total_indexed % 1000 == 0:
            elapsed = time.time() - start_time
            rate = total_indexed / elapsed
            print(f"   📊 Indexed: {total_indexed:,} passages | Rate: {rate:.1f} docs/sec")
    
    # Stop if max reached
    if MAX_DOCUMENTS and total_indexed >= MAX_DOCUMENTS:
        break

# Upload remaining batch
if batch_texts:
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
        wait=True
    )
    
    total_indexed += len(batch_texts)

# ============================================
# STEP 7: Final stats
# ============================================
elapsed = time.time() - start_time
print("\n" + "="*60)
print("✅ INDEXING COMPLETE!")
print("="*60)
print(f"📊 Total passages indexed: {total_indexed:,}")
print(f"⏱️  Total time: {elapsed/60:.1f} minutes")
print(f"🚀 Average rate: {total_indexed/elapsed:.1f} docs/sec")
print(f"📦 Collection: {QDRANT_COLLECTION}")
print(f"🔗 Qdrant URL: {QDRANT_URL}")
print("="*60)

# ============================================
# STEP 8: Test retrieval
# ============================================
print("\n🧪 Testing retrieval...")
test_query = "what is a corporation?"
query_embedding = model.encode(test_query, normalize_embeddings=True)

results = client.search(
    collection_name=QDRANT_COLLECTION,
    query_vector=query_embedding.tolist(),
    limit=3
)

print(f"\nQuery: '{test_query}'")
print(f"Top 3 results:")
for i, result in enumerate(results, 1):
    print(f"\n{i}. Score: {result.score:.4f}")
    print(f"   Text: {result.payload['text'][:200]}...")

print("\n✅ All done! Your Qdrant collection is ready for production.")
