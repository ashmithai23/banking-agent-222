# Server-Sent Events (SSE) Streaming Protocol

## Motivation
Financial analyses and multi-agent consensus checks can take 3-8 seconds to fully complete. SSE allows VectraBank to stream tokens progressively, maintaining perceived latency under 400ms.

## Protocol Specification
- **Endpoint**: `POST /api/chat/stream`
- **Content-Type**: `text/event-stream`
- **Cache-Control**: `no-cache`
- **Connection**: `keep-alive`

### Stream Frame Formats
1. **Token Frame**:
   ```
   data: {"role": "assistant", "token": "Your", "status": "streaming"}
   ```
2. **Agent Handshake Frame**:
   ```
   data: {"role": "supervisor", "active_agent": "Loan Advisor", "status": "routing"}
   ```
3. **Completion Frame**:
   ```
   data: {"status": "completed", "full_response": "...", "metadata": {}}
   ```
