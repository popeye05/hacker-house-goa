# RAG in GOA - Backend Deployment Guide

## Render Deployment (Free Tier)

### Prerequisites
1. Qdrant Cloud account with collection uploaded (already done: 997 passages)
2. Sarvam AI API key
3. GitHub repository

### Steps

1. **Push to GitHub** (if not already done)
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository: `hacker-house-goa`
   - Configure:
     - **Name**: `ragingoa-backend`
     - **Root Directory**: `task2-ragingoa/backend`
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - **Plan**: Free

3. **Set Environment Variables** in Render Dashboard:
   - `SARVAM_API_KEY`: Your Sarvam AI key
   - `QDRANT_URL`: Your Qdrant cloud URL
   - `QDRANT_API_KEY`: Your Qdrant API key
   - `QDRANT_COLLECTION`: `msmarco_xi`
   - `QDRANT_EMBEDDING_MODEL`: `intfloat/multilingual-e5-small`

4. **Deploy**
   - Click "Create Web Service"
   - Wait for build to complete (~5-10 minutes)
   - Your API will be live at: `https://ragingoa-backend.onrender.com`

### Test Deployment

```bash
# Health check
curl https://ragingoa-backend.onrender.com/health

# Test retrieval
curl -X POST https://ragingoa-backend.onrender.com/api/v1/rag/debug-retrieval \
  -H "Content-Type: application/json" \
  -d '{"query": "what is a corporation?", "language": "en", "top_k": 5}'
```

### Update Frontend

In `frontend/src/components/VoiceRecorder.tsx` or wherever you call the API, update:

```typescript
const response = await fetch("https://ragingoa-backend.onrender.com/api/query", {
  method: "POST",
  body: formData,
});
```

## Vercel/Netlify Frontend Deployment

### Vercel (Recommended)

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Deploy from frontend directory**
   ```bash
   cd frontend
   vercel
   ```

3. **Environment Variables** (if needed)
   - Set `VITE_API_URL` to your Render backend URL

### Netlify

1. **Deploy**
   ```bash
   cd frontend
   npm run build
   netlify deploy --prod --dir=dist
   ```

2. **Configure**
   - Build command: `npm run build`
   - Publish directory: `dist`

---

## Notes

- **Free tier limitations**: Render free tier spins down after 15 mins of inactivity (cold starts ~30s)
- **CORS**: Already configured in backend to allow all origins
- **Qdrant**: Using cloud-hosted vector DB, no local index needed
- **BGE-M3**: Not used on Render (too large for free tier), using Qdrant's cloud embeddings instead
