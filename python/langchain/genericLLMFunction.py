import os
import openai
import json
import datetime
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def generateLlmResponse(
    data_requirements: str,
    userName: str,
    conversation_history: List[Dict[str, str]]
) -> tuple[str, bool]:
    """
    data_requirements: a JSON string describing the form inputs (e.g. choice, number, string).
    conversation_history: the messages so far (user/assistant roles).

    The AI asks for all missing data until it says:
    "I have all the information I need. We can finalize now."
    """

    system_prompt = f"""
You are a compassionate clinical-trial AI assistant, speaking directly to the patient.
Below is the form structure we want to collect data for (in JSON):

{data_requirements}

- If the user's answer is incomplete or unclear, politely ask for clarification.
- If the user is reluctant or cannot provide specifics, give examples or suggestions.
- If the user is unsure, ask for their best guess.
- Make sure to ask for all the necessary data.
- Remain empathetic, encouraging, and respectful.
- Ensure you are adding a fair share of emojis for better context

Once you believe you have all necessary data, say the exact phrase:
"I have all the information I need. We can finalize now."

After that, do not ask further questions—just wait for finalization.
Be empathetic, but thorough.

Make sure to refer to the user personally, (preferably by their first name) instead of referring to them as a "patient" or "user".

User's name: {userName}

#IMPORTANT: DONT IGNORE THIS
NEVER EVER EVER EVER reference the user as "the patient" or "the user". Always use their name.
NUMBER FIELDS MUST CONTAIN A NUMERICAL VALUE, NOT A STRING.
CHOICE FIELDS **MUST** CONTAIN ONE OF THE PROVIDED VALUES IN THE ORIGINAL REQUEST.
IF A PATIENT REFUSES CONTINUOUSLY, WRITE "REFUSED" INSTEAD OF A VALUE AS A **LAST RESORT**.

Also: Make sure to only ask one question at a time, as to not overwhelm the user! :)
"""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.2,
            max_tokens=300
        )
        done = False
        for message in completion.choices: #type: ignore
            if "I have all the information I need. We can finalize now." in message.message.content:
                done = True
                break
        return completion.choices[0].message.content, done #type: ignore
    except Exception as e:
        return f"Error calling OpenAI: {str(e)}", False


def parse_final_conversation_to_json(
    conversation_history: List[Dict[str, str]],
    fields: List[Dict[str, object]]
) -> Dict:
    """
    1) Takes the entire conversation (AI said "I have all the information I need. We can finalize now.").
    2) parse_instructions: Tells GPT how to produce final JSON with keys = fieldnames.
    3) fieldnames: The keys we expect in the final JSON.

    Returns a JSON string with those keys, or empty if not provided.
    """

    parse_instructions = f"""
    You are now a data parser. Please output valid JSON with the following fields, PAYING ATTENTION to the original instructions:
    {'{'}
    {
        ''',
        '''.join([
            f'"{field["label"]}": ""' for field in fields
        ])
    }
    {'}'}
    If the user did not provide them, fill them with blank or 0.
    "number" type fields must contain a numerical value, not a string.
    "choice" type fields must contain one of the provided values in the origin request.
    "string" type fields must contain a summary of the original result.

    REMEMBER!!!! CHOICE FIELDS **MUST** CONTAIN ONE OF THE PROVIDED VALUES IN THE ORIGINAL REQUEST.
    THERE WILL BE CRITICAL ERRORS IF THIS IS NOT FOLLOWED.
    YOU MUST FIND THE VALUE PASSED THAT MOST CLOSELY MATCHES THE USER'S RESPONSE.

    Return only valid JSON, no extra commentary.
    """

    # Combine conversation + system instructions
    parse_messages = conversation_history + [
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
        print("Error calling OpenAI for parsing:", str(e))
        raise e

    try:
        parsed_data = json.loads(json_reply)
    except json.JSONDecodeError as e:
        print("Could not parse JSON. GPT reply:", json_reply)
        raise e

    # Fill missing fields with ""
    fieldnames = [field['label'] for field in fields]
    output = {}
    for fn in fieldnames:
        output[fn] = parsed_data.get(fn, "")

    return output


if __name__ == "__main__":
    # 1) form_inputs describing each field. 
    #    The 'description' will become the final JSON key (no hard-coding).
    form_inputs = [
        {
            "label": "Mood",
            "description": "The mood of the patient today (pick one):",
            "data": {
                "values": ["Terrible", "Poor", "Fair", "Good", "Great", "Excellent"],
                "type": "choice"
            }
        },
        {
            "label": "Sleep Duration",
            "description": "How many hours did the patient sleep last night? (0-12+)",
            "data": {
                "type": "number"
            }
        },
        {
            "label": "Additional Notes",
            "description": "Any additional notes about how the patient is feeling or other details:",
            "data": {
                "type": "string"
            }
        }
    ]

    # Convert form_inputs to JSON so the AI knows the structure
    data_requirements = json.dumps(form_inputs, indent=2)

    # 2) We'll store conversation in a list
    conversation = []

    while True:
        user_input = input("User: ")
        conversation.append({"role": "user", "content": user_input})

        # Generate next AI message
        ai_response = generateLlmResponse(data_requirements, conversation)
        print("AI:", ai_response)

        conversation.append({"role": "assistant", "content": ai_response})

        # 3) If the AI says "I have all the information I need. We can finalize now."
        if "I have all the information I need. We can finalize now." in ai_response:
            print("\nAI indicated it's satisfied. Let's parse final conversation.")

            # 4) Build parse instructions + dynamic keys from form_inputs
            #    We'll use the 'description' as the final JSON key for each item
            #    So if we have N items, we produce N keys in our final JSON.

            # Build a minimal JSON object template from each 'description'
            # e.g. { "Your mood today (pick one):": "", "How many hours did you sleep last night? (0-12+)": "", ... }
            parse_instructions = "You are now a data parser. Please output valid JSON with these keys:\n{\n"
            for item in form_inputs:
                key = item["label"]
                parse_instructions += f'  "{key}": "",\n'
            parse_instructions += """}
If the user did not provide them, fill them with blank or 0. Return only valid JSON, no extra commentary.
"""

            # Our final 'fieldnames' is just the list of descriptions from form_inputs
            schema_fields = [item["label"] for item in form_inputs]

            final_data = parse_final_conversation_to_json(
                conversation_history=conversation,
                parse_instructions=parse_instructions,
                fieldnames=schema_fields
            )

            print("Parsed as dict:", final_data)

            print("Exiting.")
            break
