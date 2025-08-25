from app.utils.llm import generate_response


async def send_chat(prompt: str) -> str:
    messages = [
        {
            "role": "user",
            "content": prompt,
        }
    ]
    try:
        response = generate_response(messages=messages)
        return response
    except Exception as e:
        print(f"Error during response generation: {e}")
        return "An error occurred while processing your request."
