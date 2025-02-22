from typing import Union
from fastapi import FastAPI, HTTPException
import firebase_admin
from firebase_admin import credentials, firestore
import sys
import os
import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from langchain.genericLLMFunction import generateLlmResponse

app = FastAPI()

# Initialize Firebase Admin with your service account key.
cred = credentials.Certificate("firestore_key.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore client.
db = firestore.client()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/get_form/{form_id}")
def get_form(form_id: str):
    """
    Retrieve a form and its fields from the Firestore database.
    
    Expected Firestore structure:
      forms (collection)
         └── form_id (document)
              └── ...fields
    """
    try:
        # Access the document in the "forms" collection with the given form_id.
        form_ref = db.collection('forms').document(form_id)
        form_doc = form_ref.get()
        if form_doc.exists:
            # Return the dictionary of fields stored in the document.
            return form_doc.to_dict()
        else:
            raise HTTPException(status_code=404, detail="Form not found")
    except Exception as e:
        # Log or handle the exception as needed.
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/start_session/{form_id}/{patient_id}")
def start_session(form_id: str, patient_id: str):
    """
    Start a new chat session for a given patient using a specified form.
    
    Process:
      1. Retrieve the form from Firestore.
      2. Create a conversation array with a placeholder for each input field.
      3. Generate the initial bot question using the imported LLM function.
      4. Save the session in a "sessions" subcollection under the patient.
      5. Return the session id and the first bot question.
    """
    # Retrieve form document from Firestore.
    form_ref = db.collection("forms").document(form_id)
    form_doc = form_ref.get()
    if not form_doc.exists:
        raise HTTPException(status_code=404, detail="Form not found")
    form_data = form_doc.to_dict()

    # Initialize conversation placeholders for each input field.
    conversation = []
    inputs = form_data.get("inputs", [])
    if not inputs:
        raise HTTPException(status_code=400, detail="Form does not have any input fields")
    for idx, _ in enumerate(inputs):
        conversation.append({
            "field_id": idx,
            "question": None,
            "response": None
        })

    # Generate the initial question for the first input field using the LLM function.
    initial_question = generateLlmResponse([], inputs[0])
    conversation[0]["question"] = initial_question

    # Prepare the session document data.
    session_data = {
        "form_id": form_id,
        "patient_id": patient_id,
        "created_at": datetime.datetime.utcnow(),
        "current_field_index": 0,  # waiting for response to the first question
        "inputs": inputs,
        "conversation": conversation
    }

    # Save the session document in a subcollection under the patient.
    session_ref = db.collection("patient").document(patient_id).collection("sessions").document()
    session_ref.set(session_data)
    session_id = session_ref.id

    return {"session_id": session_id, "bot_question": initial_question}

@app.post("/send_message/{patient_id}/{session_id}/{message_text}")
def send_message(patient_id: str, session_id: str, message_text: str):
    """
    Process a patient's message in an existing session.
    
    Process:
      1. Retrieve the session document.
      2. Save the patient's response for the current conversation step.
      3. If there is another input field, generate the next bot question using the LLM function.
      4. Update the session document and return the new bot question.
      5. If no further fields remain, mark the session as complete.
    """
    session_ref = db.collection("patient").document(patient_id).collection("sessions").document(session_id)
    session_doc = session_ref.get()
    if not session_doc.exists:
        raise HTTPException(status_code=404, detail="Session not found")
    session_data = session_doc.to_dict()

    current_index = session_data.get("current_field_index", 0)
    conversation = session_data.get("conversation", [])
    inputs = session_data.get("inputs", [])

    # Check if the session is already complete.
    if current_index >= len(conversation):
        raise HTTPException(status_code=400, detail="Session already complete")

    # Save the user's response to the current conversation entry.
    conversation[current_index]["response"] = message_text

    # If there is another input field, generate the next question.
    if current_index + 1 < len(conversation):
        new_index = current_index + 1
        next_question = generateLlmResponse(conversation, inputs[new_index])
        conversation[new_index]["question"] = next_question

        # Update the session: set the new current index and update conversation history.
        session_ref.update({
            "current_field_index": new_index,
            "conversation": conversation
        })
        return {"bot_question": next_question}
    else:
        # No more input fields; the session is complete.
        session_ref.update({
            "current_field_index": current_index + 1,
            "conversation": conversation
        })
        return {"message": "Session complete"}

@app.get("/receive_message/{patient_id}/{session_id}")
def get_messages(patient_id: str, session_id: str):
    """
    Retrieve the conversation history for a given session.
    """
    session_ref = db.collection("patient").document(patient_id).collection("sessions").document(session_id)
    session_doc = session_ref.get()
    if not session_doc.exists:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_doc.to_dict()
