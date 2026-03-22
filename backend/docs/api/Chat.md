# Chat API

Base path: `/api/chat`

---

## POST `/api/chat/message`

Send a user message and receive the model's reply.

### Request

```json
{
  "message": "你好，哪吒"
}
```

| Field     | Type   | Required | Description        |
|-----------|--------|----------|--------------------|
| `message` | string | ✅        | The user's message |

### Response — 200 OK

```json
{
  "reply": "哈，你也好！有什么想聊的？"
}
```

### Error responses

| Status | Body                                       | Cause                        |
|--------|--------------------------------------------|------------------------------|
| 400    | `{ "error": "Empty message." }`            | Blank `message` field        |
| 400    | `{ "error": "Invalid JSON body." }`        | Malformed request body       |
| 500    | `{ "error": "ChatService is not initialized." }` | Service failed to start |
| 500    | `{ "error": "An error occurred: ..." }`    | Model / RAG runtime error    |

---

## POST `/api/chat/reset`

Clear the in-memory conversation history for the current session.

### Request

No body required.

### Response — 200 OK

```json
{
  "status": "success",
  "message": "Conversation history reset."
}
```

### Error responses

| Status | Body                                             | Cause                        |
|--------|--------------------------------------------------|------------------------------|
| 500    | `{ "error": "ChatService is not initialized." }` | Service failed to start      |
| 500    | `{ "error": "An error occurred: ..." }`          | Unexpected runtime error     |

---

## Notes

- Conversation history is stored **in-memory** on the server singleton. A server restart clears all history.
- The RAG knowledge base is loaded from `resource/database/NeZha.json` at startup. If the file changes, the vector store is automatically rebuilt on next startup.
- The Ollama model used is `qwen-role-new-8b:latest`. Change `model_name` in `chat/services/chat/ChatService.py` to swap models.