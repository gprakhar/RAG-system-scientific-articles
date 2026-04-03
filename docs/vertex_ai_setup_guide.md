# Vertex AI Setup Guide for Local Development (macOS)

## Prerequisites
- Active GCP project
- Python 3.8+ installed on Mac
- This project uses `uv` for package management

## Step 1: Install Google Cloud CLI

```bash
# Install gcloud CLI if not already installed
brew install --cask google-cloud-sdk

# Or update existing installation
gcloud components update
```

## Step 2: Authenticate with GCP

```bash
# Login to your Google account
gcloud auth login

# Set your active project
gcloud config set project YOUR_PROJECT_ID

# Create application default credentials (used by Python client libraries)
gcloud auth application-default login
```

## Step 3: Enable Required APIs

```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Enable other commonly needed APIs
gcloud services enable storage-api.googleapis.com
gcloud services enable compute.googleapis.com
```

## Step 4: Install Python Dependencies

```bash
# Add Vertex AI SDK to your project
uv add google-cloud-aiplatform

# If you need additional Google Cloud libraries
uv add google-cloud-storage  # For GCS access
```

## Step 5: Basic Python Script Example

Create a file `test_vertex_ai.py`:

```python
from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel

# Initialize Vertex AI
PROJECT_ID = "your-project-id"  # Replace with your project ID
REGION = "us-central1"  # Choose your region

vertexai.init(project=PROJECT_ID, location=REGION)

# Example 1: Using Gemini models
def test_gemini():
    model = GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Explain quantum computing in simple terms")
    print(response.text)

# Example 2: Using embeddings (for your RAG system)
def test_embeddings():
    from vertexai.language_models import TextEmbeddingModel

    model = TextEmbeddingModel.from_pretrained("text-embedding-004")
    texts = ["Sample scientific text", "Another document chunk"]
    embeddings = model.get_embeddings(texts)

    for idx, embedding in enumerate(embeddings):
        print(f"Text {idx}: {len(embedding.values)} dimensions")
        print(f"First 5 values: {embedding.values[:5]}")

if __name__ == "__main__":
    test_gemini()
    # test_embeddings()
```

## Step 6: Run Your Script

```bash
# Run with uv
uv run python test_vertex_ai.py

# Or activate the environment and run directly
uv sync
source .venv/bin/activate
python test_vertex_ai.py
```

## Configuration Options

### Option 1: Environment Variables (Recommended)
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_REGION="us-central1"
```

Then in Python:
```python
import os
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
REGION = os.getenv("GOOGLE_CLOUD_REGION")
```

### Option 2: Service Account Key (Alternative)
If you need a service account instead of user credentials:

```bash
# Create service account
gcloud iam service-accounts create vertex-ai-local \
    --display-name="Vertex AI Local Development"

# Grant necessary roles
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:vertex-ai-local@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Create and download key
gcloud iam service-accounts keys create ~/vertex-ai-key.json \
    --iam-account=vertex-ai-local@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/vertex-ai-key.json"
```

## For Your RAG System

Based on your `claude_code_plan.md`, here's how to use Vertex AI for embeddings:

```python
from vertexai.language_models import TextEmbeddingModel
import vertexai

# Initialize
vertexai.init(project=PROJECT_ID, location=REGION)

# Load embedding model
model = TextEmbeddingModel.from_pretrained("text-embedding-004")

# Process chunks (matches your 512-token strategy)
def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """
    Embed text chunks using Vertex AI.

    Args:
        chunks: List of text chunks (512 tokens each per your plan)

    Returns:
        List of embedding vectors
    """
    embeddings = model.get_embeddings(chunks)
    return [emb.values for emb in embeddings]

# Batch processing for efficiency
BATCH_SIZE = 250  # Vertex AI supports up to 250 inputs per request

def embed_large_dataset(chunks: list[str]) -> list[list[float]]:
    all_embeddings = []
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        batch_embeddings = embed_chunks(batch)
        all_embeddings.extend(batch_embeddings)
    return all_embeddings
```

## Available Models on Vertex AI

### Generative Models (LLMs)
- `gemini-1.5-pro` - Best quality, multimodal
- `gemini-1.5-flash` - Fast, cost-effective
- `gemini-2.0-flash-exp` - Latest experimental

### Embedding Models
- `text-embedding-004` - Latest, 768 dimensions (recommended for your RAG)
- `textembedding-gecko@003` - Legacy, 768 dimensions
- `text-multilingual-embedding-002` - Multilingual support

### Vision Models (for figure extraction)
- `gemini-1.5-pro-vision` - For analyzing scientific figures per your plan

## Troubleshooting

### Error: "Could not find application default credentials"
Run: `gcloud auth application-default login`

### Error: "Permission denied"
Ensure your account has the role `roles/aiplatform.user`:
```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="user:YOUR_EMAIL@gmail.com" \
    --role="roles/aiplatform.user"
```

### Error: "API not enabled"
```bash
gcloud services enable aiplatform.googleapis.com
```

## Cost Considerations

- **Embeddings**: ~$0.025 per 1K text records (text-embedding-004)
- **Gemini Pro**: ~$0.00025 per 1K characters input
- **Gemini Flash**: ~$0.0000625 per 1K characters input

For a dataset of 1M scientific paper chunks:
- Embedding cost: ~$25 (one-time)
- Query cost: Minimal (retrieval doesn't use the API)

## Next Steps

1. Get your project ID: `gcloud config get-value project`
2. Choose your region: `us-central1`, `us-east1`, `europe-west1`, etc.
3. Update the example script with your values
4. Test with the simple Gemini example first
5. Then test embeddings for your RAG pipeline
