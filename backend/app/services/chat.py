from app.utils.llm import chat_completion


async def send_chat(prompt: str) -> str:
    messages = [
        {
            "role": "user",
            "content": prompt,
        }
    ]
    try:
        response = chat_completion(messages=messages)
        return response
    except Exception as e:
        print(f"Error during chat completion: {e}")
        return "An error occurred while processing your request."
