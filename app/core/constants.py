from enum import StrEnum


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# Top-level aliases for backwards compatibility
# Define aliases after the class is created to avoid referencing the
# class name inside its own body which would cause a NameError.


class ChatTitle:
    DEFAULT = "New Chat"


class VectorCollection:
    DOCUMENTS = "enterprise_documents"


class SupportedFileType(StrEnum):
    PDF = ".pdf"
    DOCX = ".docx"
    TXT = ".txt"


# Backwards-compatible aliases
USER_ROLE = MessageRole.USER
ASSISTANT_ROLE = MessageRole.ASSISTANT
SYSTEM_ROLE = MessageRole.SYSTEM

# Memory Management
SUMMARY_TRIGGER_MESSAGES = 20
RECENT_MESSAGES_LIMIT = 8

# Token Budget
MAX_CONTEXT_TOKENS = 6000

RESERVED_CONTEXT_TOKENS = 2000

MAX_MEMORY_TOKENS = MAX_CONTEXT_TOKENS - RESERVED_CONTEXT_TOKENS

EVALUATION_STATUS_QUEUED = "queued"
EVALUATION_STATUS_RUNNING = "running"
EVALUATION_STATUS_COMPLETED = "completed"
EVALUATION_STATUS_FAILED = "failed"
EVALUATION_STATUS_CANCELLED = "cancelled"
