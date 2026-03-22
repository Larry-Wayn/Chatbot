import logging
import ollama
from .rag import Config, TextEmbedding

logger = logging.getLogger(__name__)


class ChatService:
    """
    Stateless-friendly chat service.

    conversation_history is kept on the instance; for multi-user scenarios
    each request should pass its own session history in (see views.py).
    """

    def __init__(self):
        self.text_embedding = TextEmbedding()
        self.client = ollama.Client(host="http://localhost:11434")
        self.model_name = "qwen-role-new-8b:latest"  # Q5_K_M ~6 GB VRAM
        self.conversation_history = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _format_messages(self, query: str, context: list) -> list:
        """Build the message list sent to the model."""
        history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.conversation_history[-Config.max_history :]
        ]
        context_str = "\n".join(
            [f"[角色资料 {i + 1}] {text}" for i, text in enumerate(context)]
        )
        return [
            *history,
            {
                "role": "user",
                "content": (
                    f"用户询问：{query}\n"
                    f" 请适当参考你的经历：{context_str}\n"
                    f"回复用户的聊天对话：{query}"
                ),
            },
        ]

    @staticmethod
    def _ensure_utf8(text) -> str:
        if isinstance(text, bytes):
            return text.decode("utf-8", errors="replace")
        return text

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chat(self, user_message: str) -> str:
        """
        Process one user message and return the assistant reply.
        Also appends both turns to self.conversation_history.
        """
        context = self.text_embedding._retrieve_context(user_message)
        messages = self._format_messages(user_message, context)

        response = self.client.chat(
            model=self.model_name,
            messages=messages,
        )

        reply: str = response["message"]["content"].lstrip("\n")

        self.conversation_history.extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": reply},
        ])

        logger.info("Query: %s", self._ensure_utf8(user_message))
        logger.info("Reply: %s", self._ensure_utf8(reply))

        return reply

    def reset_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []