from typing import Union
from fastapi import FastAPI, HTTPException
import firebase_admin
from firebase_admin import credentials, firestore

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

@app.post("/send_message/{user_id}/{message_text}")
def sendMessage():
    # Your implementation here.
    pass

@app.post()
def 

@app.get("/receive_message/{user_id}/{message_text}")
def getMessage():
    # Your implementation here.
    pass
