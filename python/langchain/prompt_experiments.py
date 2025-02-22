# python/langchain/prompt_experiments.py

import os
import openai
from dotenv import load_dotenv

load_dotenv()  # Load OPENAI_API_KEY from .env
openai.api_key = os.getenv("OPENAI_API_KEY")  # The same key used in main.py

def multi_turn_chat():
    """
    Runs a loop in the terminal, storing the entire conversation 
    so GPT can refer back to previous messages (like the SvelteKit front end).
    """

    # Start with a system message, as in main.py
    messages = [
        {"role": "system", "content": "You are a helpful clinical-trial AI assistant."}
    ]

    print("Type your question (or 'exit'):")
    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            break

        # Add the user's latest message to the conversation
        messages.append({"role": "user", "content": user_input})

        try:
            # Create a completion with the entire conversation so far
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=200
            )
            ai_reply = completion.choices[0].message.content

            print(f"Assistant: {ai_reply}")
            # Remember to add the assistant's reply back into messages for context
            messages.append({"role": "assistant", "content": ai_reply})

        except Exception as e:
            print("Error:", str(e))

if __name__ == "__main__":
    multi_turn_chat()
