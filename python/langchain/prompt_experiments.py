import os
import openai
from dotenv import load_dotenv
import csv
import datetime
import json
import time  # for streaming delays

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def daily_diary_chat():
    """
    A multi-turn diary chat where the AI decides when it has enough info.
    When the AI says 'I have all the information I need. We can finalize now.',
    we parse and save automatically, then exit.
    """

    # Modify the system prompt:
    # Instruct the AI to finalize on its own, no 'done' from user.
    system_prompt = (
        "You are a compassionate clinical-trial AI assistant. "
        "Your goal is to guide patients through a daily diary while showing empathy and reassurance. "
        "For each diary item (mood, wake time, sleep time, activities, etc.), ask clarifying questions if needed. "
        "Once you believe you have all necessary data, say the exact phrase:\n\n"
        "\"I have all the information I need. We can finalize now.\"\n\n"
        "After that, do not ask further questions—just wait for the system to finalize. "
        "Be empathetic, but thorough."
    )

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    print("Hi there.\n")
    while True:
        user_input = input("User: ")
        messages.append({"role": "user", "content": user_input})

        try:
            # Slow-stream the assistant's response
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=300,
                stream=True
            )

            print("Assistant: ", end="", flush=True)
            collected_chunks = []

            for chunk in completion:
                chunk_text = chunk["choices"][0]["delta"].get("content", "")
                # Slow down output, e.g., 50ms per character
                for char in chunk_text:
                    print(char, end="", flush=True)
                    time.sleep(0.05)
                collected_chunks.append(chunk_text)

            ai_reply = "".join(collected_chunks)
            print()  # finish the line

            # Add the assistant's response to the conversation
            messages.append({"role": "assistant", "content": ai_reply})

            # Check if AI used the finalizing phrase
            if "I have all the information I need. We can finalize now." in ai_reply:
                print("\nAI indicated it's satisfied. Saving diary and exiting...")
                parse_and_save_diary(messages)
                print("Diary saved. Exiting.")
                break

        except Exception as e:
            print("Error:", str(e))

def parse_and_save_diary(messages):
    """
    Calls GPT again, instructing it to parse the entire conversation into
    structured fields, then writes that to a CSV.
    """
    # Load the parse instructions from an external file
    with open("daily_schema.txt", "r", encoding="utf-8") as f:
        parse_instructions = f.read()

    parse_messages = messages + [
        {"role": "system", "content": parse_instructions}
    ]

    try:
        parse_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=parse_messages,
            temperature=0,
            max_tokens=300
        )
        json_reply = parse_completion.choices[0].message.content.strip()
    except Exception as e:
        print("Error in parse step:", e)
        return

    print("\nDEBUG: Raw GPT parse reply:", json_reply)

    try:
        diary_data = json.loads(json_reply)
    except json.JSONDecodeError:
        print("Could not parse JSON from GPT. Raw reply:")
        print(json_reply)
        return

    with open("daily_schema_fields.json", "r") as ff:
        fieldnames = json.load(ff)

    csv_filename = "diary_data.csv"
    file_exists = os.path.isfile(csv_filename)

    with open(csv_filename, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        row = {}
        for fn in fieldnames:
            row[fn] = diary_data.get(fn, "")

        if not row["date"]:
            row["date"] = str(datetime.date.today())

        writer.writerow(row)

if __name__ == "__main__":
    daily_diary_chat()
