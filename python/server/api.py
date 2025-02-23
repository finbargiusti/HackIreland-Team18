import sys
import os
import datetime
import json
from typing import Union, List, Dict

from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel

import firebase_admin
from firebase_admin import credentials, firestore, auth

# Adjust sys.path so we can import modules from the parent directory.
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from langchain.genericLLMFunction import generateLlmResponse, parse_final_conversation_to_json

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase Admin with your service account key.
cred = credentials.Certificate("firestore_key.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore client.
db = firestore.client()

# ----------------------------
# Models
# ----------------------------
class StartSessionRequest(BaseModel):
    patient_id: str

class SendMessageRequest(BaseModel):
    session_id: str
    patient_id: str
    message: str

# ----------------------------
# Endpoints
# ----------------------------

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/get_form/{admin_id}/{form_id}")
def get_form(admin_id: str, form_id: str):
    """
    Retrieve a form from Firestore.
    
    Expected structure:
      admin (collection)
         └── {admin_id} (document)
             └── forms (subcollection)
                  └── {form_id} (document) with fields such as "title", "inputs", and "users".
    """
    try:
        form_ref = db.collection("admin").document(admin_id).collection("forms").document(form_id)
        form_doc = form_ref.get()
        if form_doc.exists:
            return form_doc.to_dict()
        else:
            raise HTTPException(status_code=404, detail="Form not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/start_session/{admin_id}/{form_id}")
def start_session(admin_id: str, form_id: str, start_req: StartSessionRequest):
    """
    Start a new chat session for a given patient using a specified form.
    
    Process:
      1. Retrieve the form from Firestore at admin/{admin_id}/forms/{form_id}.
      2. Check if the patient's email (retrieved via Firebase Auth) is approved in the form's "users" list.
      3. Initialize conversation history as an empty list.
      4. Generate the initial bot question by calling generateLlmResponse with the first input's description.
      5. Append the bot's response (with role "assistant") to the conversation.
      6. Save the session in a "sessions" subcollection under the form.
      7. Return the session id and the initial bot question.
    """
    patient_id = start_req.patient_id

    # Retrieve form document.
    form_ref = db.collection("admin").document(admin_id).collection("forms").document(form_id)
    form_doc = form_ref.get()
    if not form_doc.exists:
        raise HTTPException(status_code=404, detail="Form not found")
    form_data = form_doc.to_dict()
    
    # Check patient approval via Firebase Auth.
    try:
        user_record = auth.get_user(patient_id)
        patient_email = user_record.email
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid patient uid provided")
    
    approved_users = form_data.get("users", [])
    if patient_email not in approved_users:
        raise HTTPException(status_code=401, detail="Patient not authorized for this form")
    
    # Retrieve input definitions.
    inputs = form_data.get("inputs", [])
    if not inputs:
        raise HTTPException(status_code=400, detail="Form does not have any input fields")
    
    # Initialize conversation history as an empty list.
    conversation: List[Dict[str, str]] = []
    # Generate the initial question using the first input's description.
    initial_question, _ = generateLlmResponse(json.dumps(inputs), conversation)
    conversation.append({"role": "assistant", "content": initial_question})

    # Prepare the session document data.
    session_data = {
        "admin_id": admin_id,
        "form_id": form_id,
        "patient_id": patient_id,  # stored for reference if needed
        "created_at": datetime.datetime.utcnow(),
        "current_field_index": 0,  # indicates which input is currently being processed
        "inputs": inputs,
        "conversation": conversation
    }

    # Save the session document in a "sessions" subcollection under the form.
    session_ref = db.collection("admin").document(admin_id)\
                    .collection("forms").document(form_id)\
                    .collection("sessions").document()
    session_ref.set(session_data)
    session_id = session_ref.id

    # Optionally, store the session_id in the document.
    session_ref.update({"session_id": session_id})

    return {"session_id": session_id, "bot_question": initial_question}

@app.post("/send_message/{admin_id}/{form_id}")
def send_message(admin_id: str, form_id: str, send_req: SendMessageRequest):
    """
    Process a patient's message for an existing session.
    
    Process:
      1. Retrieve the session document from admin/{admin_id}/forms/{form_id}/sessions/{session_id} (session_id from body).
      2. Append the patient's message (with role "user") to the conversation history.
      3. If there is another input field pending, generate the next bot question using generateLlmResponse.
         - The LLM function is called with the new input field's description and the updated conversation history.
      4. Append the bot's response (with role "assistant") to the conversation.
      5. Update the session document accordingly.
      6. Return the new bot question or a completion message.
    """
    session_id = send_req.session_id
    patient_id = send_req.patient_id
    message = send_req.message

    form_ref =  db.collection("admin").document(admin_id)\
                    .collection("forms").document(form_id)

    # Retrieve the session document using the full path.
    session_ref = form_ref.collection("sessions").document(session_id)
    session_doc = session_ref.get()
    if not session_doc.exists:
        raise HTTPException(status_code=404, detail="Session not found")
    session_data = session_doc.to_dict()

    current_index = session_data.get("current_field_index", 0)
    inputs = session_data.get("inputs", [])
    conversation: List[Dict[str, str]] = session_data.get("conversation", [])

    # Check if the session is already complete.
    # if current_index >= len(inputs):
    #     raise HTTPException(status_code=400, detail="Session already complete")

    # Append the patient's message to the conversation history.
    conversation.append({"role": "user", "content": message})

    # If there is another input field pending, generate the next question.
    new_index = current_index + 1
    next_question, done = generateLlmResponse(json.dumps(inputs), conversation)
    if not done:
        conversation.append({"role": "assistant", "content": next_question})
        # Update the session: advance the current field index and save the updated conversation.
        session_ref.update({
            "current_field_index": new_index,
            "conversation": conversation
        })
        return {"bot_question": next_question}
    else:
        # No more input fields; mark the session as complete.
        session_ref.update({
            "current_field_index": current_index + 1,
            "conversation": conversation
        })

        form_data = form_ref.get().to_dict()

        result = parse_final_conversation_to_json(conversation, inputs)
        # add some additional data to the result:
        result["email"] = auth.get_user(patient_id).email
        result["form_id"] = form_id
        result["admin_id"] = admin_id
        result["session_id"] = session_id
        result["date"] = datetime.datetime.utcnow().isoformat()
        results = form_data.get("results", [])
        results.append(result)
        form_ref.update({"results": results})

        return {"message": "Session complete"}

def get_result_json(conversation, fields):
    """
    Parse the final conversation into a JSON object using the provided field descriptions.
    """
    return parse_final_conversation_to_json(conversation, fields)

@app.get("/receive_message/{admin_id}/{form_id}/{session_id}")
def get_messages(admin_id: str, form_id: str, session_id: str):
    """
    Retrieve the conversation history for a given session.
    The session is located at:
      admin/{admin_id}/forms/{form_id}/sessions/{session_id}
    """
    session_ref = db.collection("admin").document(admin_id)\
                    .collection("forms").document(form_id)\
                    .collection("sessions").document(session_id)
    session_doc = session_ref.get()
    if not session_doc.exists:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_doc.to_dict()

@app.get("/conversation/{admin_id}/{form_id}/{session_id}")
def get_conversation(admin_id: str, form_id: str, session_id: str):
    """
    Retrieve the entire conversation history for a given session.
    Only returns the conversation field from the session document.
    """
    session_ref = db.collection("admin").document(admin_id)\
                    .collection("forms").document(form_id)\
                    .collection("sessions").document(session_id)
    session_doc = session_ref.get()
    if not session_doc.exists:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = session_doc.to_dict()
    conversation = session_data.get("conversation", [])
    return {"conversation": conversation}
