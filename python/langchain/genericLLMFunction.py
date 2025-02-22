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
    conversation_history: List[Dict[str, str]]
) -> str:
    """
    1) data_requirements: a string or JSON describing what data we want to collect 
       (e.g. enumerations, fields like mood, wake_time, activity, etc.).

    2) conversation_history: the messages so far, each item is {'role': 'user'|'assistant', 'content': ...}.

    Returns a string: the AI's next response.

    The AI is instructed to keep asking for missing data until it says:
    'I have all the information I need. We can finalize now.'
    """

    # Enhanced system prompt emphasizing empathy, clarifications, and best guesses
    system_prompt = f"""
You are a compassionate clinical-trial AI assistant, showing empathy and reassurance.
Your goal is to thoroughly gather the following data from the user: {data_requirements}

- If the user's answer is incomplete or unclear, politely ask for clarification.
- If the user is reluctant or unable to provide specifics, offer examples or suggestions.
- If the user still cannot or will not specify, make a best guess or note it as an estimate.
- Always remain empathetic, encouraging, and respectful.

Once you believe you have all necessary data, say the exact phrase:
"I have all the information I need. We can finalize now."

After that, do not ask further questions—just wait for finalization.
Be empathetic, but thorough.
"""

    # Build the entire prompt: system + conversation so far
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)

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
    fieldnames: Dict
) -> str:
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
        raise e

    print("\nDEBUG: GPT parse result:", json_reply)

    # Attempt to load JSON
    try:
        parsed_data = json.loads(json_reply)
    except json.JSONDecodeError as e:
        print("Could not parse JSON. GPT reply:", json_reply)
        raise e

    out = {}
    for fn in fieldnames:
        # fill with empty if not present
        out[fn] = parsed_data.get(fn, "")

    return json.dumps(out)


if __name__ == "__main__":
    # Example 'data_requirements' describing enumerations / fields:
    data_requirements = """
    We want to collect:
    - mood (choices: 'Terrible','Fine','Great'),
    - wake_time,
    - sleep_time,
    - hours_slept,
    - notes
    ...
    """

    conversation = []
    while True:
        user_input = input("User: ")
        # Add the user's message to conversation
        conversation.append({"role": "user", "content": user_input})

        # Call generateLlmResponse with the updated conversation
        ai_response = generateLlmResponse(data_requirements, conversation)
        print("AI:", ai_response)

        # Add AI's reply to conversation
        conversation.append({"role": "assistant", "content": ai_response})

        # Check if AI says "I have all the information I need. We can finalize now."
        if "I have all the information I need. We can finalize now." in ai_response:
            print("\nAI indicated it's satisfied. Let's parse final conversation.")

            # You can define or load parse instructions:
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

            with open('daily_schema_fields.json', 'r') as f:
                schema_fields = json.load(f)

            parse_final_conversation_to_csv(
                conversation, 
                parse_instructions,
                schema_fields
            )
            print("Diary data saved to CSV. Exiting.")
            break
