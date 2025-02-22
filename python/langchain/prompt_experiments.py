# python/langchain/prompt_experiments.py

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
    A multi-turn diary chat. When user types 'done',
    we ask GPT to parse the entire conversation into structured data,
    then save it to a CSV file.
    """

    # Enhanced system prompt for better clarifications and follow-up
    system_prompt = (
        "You are a compassionate clinical-trial AI assistant. "
        "Your goal is to guide patients through a daily diary while showing empathy and reassurance. "
        "For each diary item (mood, wake time, sleep time, activities, exercise type, estimated calories burned, "
        "total food intake, medications/supplements, and any symptoms/notes), if the patient's response is vague "
        "or missing key information, politely ask for clarification or provide examples to help them estimate. "
        "Only move on once you have a reasonable answer or the user prefers not to say. "
        "Encourage the patient to share openly but gently, with examples if needed (e.g., 'Would you say that's "
        "mostly cardio or strength training? About how many calories do you think that might have burned?'). "
        "At the end, kindly invite the patient to type 'done' if they have nothing more to add. "
        "Once the user says 'done', do not continue the conversation; simply acknowledge that "
        "the diary is complete and thank them for their time."
    )

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    print("Daily Diary: type your response or 'done' to finish the session.")
    while True:
        user_input = input("User: ")
        if user_input.lower() == "done":
            parse_and_save_diary(messages)
            print("Diary saved. Exiting.")
            break

        messages.append({"role": "user", "content": user_input})

        try:
            # Slow-stream the assistant's response so it feels more natural
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
            messages.append({"role": "assistant", "content": ai_reply})

        except Exception as e:
            print("Error:", str(e))

def parse_and_save_diary(messages):
    """
    Calls GPT again, instructing it to parse the entire conversation into
    structured fields, then writes that to a CSV.
    """

    parse_instructions = (
        "You are now a data parser. Review the entire conversation above. "
        "Extract the key daily-diary info and produce a JSON with these fields:\n\n"
        "{\n"
        '  "date": "YYYY-MM-DD or blank",\n'
        '  "mood": 3,                  // numeric 1–10\n'
        '  "wake_time": "07:30",\n'
        '  "sleep_time": "23:30",\n'
        '  "hours_slept": 8,           // numeric hours or your best estimate\n'
        '  "activity_type": "cardio",  // one word (cardio, strength, yoga, mixed, etc.)\n'
        '  "estimated_calories_burned": 500,  // numeric\n'
        '  "food_intake": 3000,        // numeric estimate of total calories\n'
        '  "medications": "ibuprofen",\n'
        '  "notes": "feeling nauseous, any other remarks"\n'
        "}\n\n"
        "Guidelines:\n"
        "- If the user doesn't specify an activity type, try to infer or use 'mixed'.\n"
        "- If the user doesn't give times, do your best guess or leave them blank.\n"
        "- hours_slept is the difference between sleep_time and wake_time if known; else guess.\n"
        "- For 'notes', keep it concise.\n"
        "- Return ONLY valid JSON, no extra commentary.\n"
        "If the user didn’t provide certain fields, fill them with blanks or zero.\n"
    )

    parse_messages = messages + [
        {"role": "system", "content": parse_instructions}
    ]

    try:
        parse_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=parse_messages,
            temperature=0,  # minimal creativity => more direct JSON
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

    fieldnames = [
        "date",
        "mood",
        "wake_time",
        "sleep_time",
        "hours_slept",
        "activity_type",
        "estimated_calories_burned",
        "food_intake",
        "medications",
        "notes"
    ]

    csv_filename = "diary_data.csv"
    file_exists = os.path.isfile(csv_filename)

    with open(csv_filename, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        row = {}
        for fn in fieldnames:
            row[fn] = diary_data.get(fn, "")

        # If GPT left date blank, fill with today's date
        if not row["date"]:
            row["date"] = str(datetime.date.today())

        writer.writerow(row)

if __name__ == "__main__":
    daily_diary_chat()
