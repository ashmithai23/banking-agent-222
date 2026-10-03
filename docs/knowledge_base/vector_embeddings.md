# Vector Embeddings Reference

## Models Evaluated
1. **Google `text-embedding-004`**:
   - Dimension: 768
   - Latency: ~45ms per 10-chunk batch
   - Semantic financial term fidelity: High
2. **OpenAI `text-embedding-3-small`**:
   - Dimension: 1536
   - Latency: ~60ms
   - Compatibility: High

## Distance Metric
Cosine distance is preferred for normalized embedding vectors:
$$D_{\text{cosine}}(u, v) = 1 - \frac{u \cdot v}{\|u\|_2 \|v\|_2}$$
