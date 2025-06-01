from app.models.chat import ChatRequestModel, ChatResponseModel
from app.services.chat import send_chat
from fastapi import APIRouter

router = APIRouter(prefix="/chat")


@router.post("", response_model=ChatResponseModel)
async def chat(data: ChatRequestModel):
    response = await send_chat(data.prompt)
    return {"response": response}
