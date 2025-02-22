import os
import openai
import json
import csv
import datetime
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def generateLlmResponse(
    data_requirements: str,
    conversation_history: List[Dict[str, str]],
    next_question: str
) -> str:
    """
    1) data_requirements: a JSON or string describing what data we want to collect 
       (e.g., enumerations, fields like mood, wake_time, activity, etc.).

    2) conversation_history: the messages so far, each item is {'role': 'user'|'assistant', 'content': ...}.

    3) next_question: the new text from user (like "I feel fine" or "I woke up at 9 am").

    Returns a string: the AI's response.
    """

    # Example system prompt referencing the data requirements
    system_prompt = f"""
You are a compassionate clinical-trial AI assistant. 
The trial requires collecting the following data: {data_requirements}

Ask clarifying questions if the user's answer is vague. 
Once you believe you have all necessary data, say the exact phrase:
"I have all the information I need. We can finalize now."

After that, do not ask further questions—just wait for finalization.
Be empathetic, but thorough.
"""

    # Combine system prompt + conversation + new user message
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": next_question})

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        ai_reply = completion.choices[0].message.content
        return ai_reply
    except Exception as e:
        return f"Error calling OpenAI: {str(e)}"


def parse_final_conversation_to_csv(
    conversation_history: List[Dict[str, str]],
    schema_instructions: str,
    output_csv_path: str = "diary_data.csv",
    schema_fields_json: str = "daily_schema_fields.json"
) -> None:
    """
    1) Takes the entire conversation (where the AI presumably said "we can finalize now").
    2) 'schema_instructions': Additional instructions telling GPT how to parse the conversation 
       into structured JSON (like your daily_schema.txt).
    3) 'output_csv_path': Where to save the final CSV row.
    4) 'schema_fields_json': A JSON file listing the columns we want in CSV.

    Steps:
    - We call GPT again with the conversation + schema_instructions to produce a JSON of final data.
    - We parse that JSON in Python.
    - We append (or create) a CSV row with those fields.
    """
    # Build the parse prompt
    parse_messages = conversation_history + [
        {"role": "system", "content": schema_instructions}
    ]

    # Call OpenAI to parse
    try:
        parse_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=parse_messages,
            temperature=0,
            max_tokens=300
        )
        json_reply = parse_completion.choices[0].message.content.strip()
    except Exception as e:
        print("Error calling OpenAI for parsing:", str(e))
        return

    print("DEBUG: GPT parse result:", json_reply)

    # Attempt to load JSON
    try:
        parsed_data = json.loads(json_reply)
    except json.JSONDecodeError:
        print("Could not parse JSON. GPT reply:", json_reply)
        return

    # Load the field definitions from your schema_fields JSON
    try:
        with open(schema_fields_json, "r", encoding="utf-8") as ff:
            fieldnames = json.load(ff)  # e.g. ["date","mood","wake_time",...]
    except Exception as e:
        print("Error reading schema fields JSON:", str(e))
        return

    # Write to CSV
    file_exists = os.path.isfile(output_csv_path)
    with open(output_csv_path, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        row = {}
        for fn in fieldnames:
            # fill with empty if not present
            row[fn] = parsed_data.get(fn, "")

        # if there's a 'date' field missing, fill with today:
        if not row.get("date"):
            row["date"] = str(datetime.date.today())

        writer.writerow(row)

    print(f"Parsed data appended to {output_csv_path}")

if __name__ == "__main__":
    # Suppose 'data_requirements' describes enumerations, e.g.:
    data_reqs = """
    The user must provide: 
    - mood (choice: 'Terrible','Fine','Great'), 
    - wake_time, 
    - sleep_time, 
    - hours_slept, 
    - notes
    ...
    """

    conversation = []
    while True:
        user_input = input("User: ")
        # call generateLlmResponse
        ai_response = generateLlmResponse(data_reqs, conversation, user_input)
        print("AI:", ai_response)

        # add to conversation
        conversation.append({"role": "user", "content": user_input})
        conversation.append({"role": "assistant", "content": ai_response})

        # check if AI says "we can finalize now"
        if "I have all the information I need. We can finalize now." in ai_response:
            print("\nAI indicated it's satisfied. Let's parse final conversation.")
            # we load 'schema_instructions' from a file or define inline
            parse_instructions = """
            You are now a data parser. Please output JSON with:
            {
              "date": "",
              "mood": "",
              "wake_time": "",
              "sleep_time": "",
              "hours_slept": 0,
              "notes": ""
              ... etc
            }
            Fill blanks if user didn't provide them. 
            Return valid JSON only, no extra text.
            """
            parse_final_conversation_to_csv(
                conversation, 
                parse_instructions,
                output_csv_path="diary_data.csv",
                schema_fields_json="daily_schema_fields.json"
            )
            print("Diary data saved to CSV. Exiting.")
            break
