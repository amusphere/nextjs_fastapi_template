from app.models.chat import ChatRequestModel, ChatResponseModel
from app.services.chat import chat_with_openai
from fastapi import APIRouter

router = APIRouter(prefix="/chat")


@router.post("", response_model=ChatResponseModel)
async def chat(data: ChatRequestModel):
    response = await chat_with_openai(data.prompt)
    return {"response": response}
