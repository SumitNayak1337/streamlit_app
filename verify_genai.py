import sys
from google import genai
from google.genai import types

def main():
    client = genai.Client(api_key="TEST_KEY")
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction="You are a helpful assistant."
        )
    )
    print("history type:", type(chat.get_history()))
    print("has_history_attr:", hasattr(chat, 'history'))
    try:
        r = chat.send_message("Hello")
        print("role:", chat.get_history()[0].role)
        print("text:", chat.get_history()[0].parts[0].text)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
