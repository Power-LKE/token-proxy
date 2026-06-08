"""Data models - OpenAI compatible request/response formats"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union


class ChatMessage(BaseModel):
    role: str
    content: Union[str, List[Dict[str, Any]]]


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    user: Optional[str] = None


class UsageInfo(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: UsageInfo


class UserInfo(BaseModel):
    api_key: str
    name: str
    balance: float
    is_active: bool = True
    created_at: str = ""
    email: str = ""
    transactions: List[dict] = []
    role: str = "user"
    parent_key: str = ""


class RegistrationRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    email: str = Field(default="", max_length=200)
