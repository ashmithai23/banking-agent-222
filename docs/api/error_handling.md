# API Error Handling Strategy

VectraBank uses standard RFC-7807 problem details for structured error reporting:

| HTTP Status | Error Scenario | Recovery Action |
|-------------|----------------|-----------------|
| `400 Bad Request` | Unsupported file extension on upload | Return allowed list: [.pdf, .txt, .md] |
| `422 Unprocessable` | Missing mandatory financial parameters | Clarification prompt back to customer |
| `429 Too Many Requests` | LLM Quota exhaustion | Fallback to secondary model or queued retry |
| `500 Server Error` | Unexpected parsing or vector exception | Detailed diagnostic log with fallback message |
| `503 Service Unavailable` | LLM API provider timeout | Fallback offline deterministic heuristics |
