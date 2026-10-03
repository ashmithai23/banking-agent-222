# Environment Configuration Reference

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LLM_MODE` | `string` | `gemini` | Model provider: `gemini` or `openai` |
| `GEMINI_API_KEY` | `string` | (Required for Gemini) | Google Gemini API credential |
| `OPENAI_API_KEY` | `string` | None | OpenAI or NVIDIA API credential |
| `OPENAI_BASE_URL` | `string` | None | Custom base URL for OpenAI-compatible APIs |
| `OPENAI_MODEL` | `string` | `moonshotai/kimi-k3` | Model name when running in OpenAI mode |
| `LLM_MAX_TOKENS` | `integer` | `16384` | Max tokens generated per completion |
| `LLM_TEMPERATURE`| `float` | `0.7` | Sampling temperature for creative tasks |
| `VECTOR_STORE_PATH` | `string` | `./chroma_db` | Storage path for Chroma vector indices |
