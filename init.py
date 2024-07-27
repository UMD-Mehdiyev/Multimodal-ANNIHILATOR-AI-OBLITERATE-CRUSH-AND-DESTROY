from flask import Flask, render_template, request, redirect, url_for
from firebase_admin import credentials, initialize_app, firestore, storage
import util
import uuid
import os

import util.gemini

cred = credentials.Certificate("serviceAccountKey.json")
default_app = initialize_app(cred, {'storageBucket': 'multimodal-annihilator-ai.appspot.com'}) 
db = firestore.client()

app = Flask(__name__)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')
    
@app.route('/sign_in')
def sign_in():
    return render_template('sign_in.html')

@app.route('/', methods=['POST', 'GET'])
def submit_content():
    if request.method == 'POST':
        if request.files['file'].name == 'file' and len(request.form['content']) != 0:
            content = request.form['content']
            content_id = uuid.uuid4().hex
            try:
                # Save content to Firebase
                doc_ref = db.collection('content').document(content_id)
                doc_ref.set({
                    'content': content,
                })
                return redirect(url_for('response', content_id=content_id))
            except Exception as e:
                print(f"Error saving text content to Firebase: {e}")
                return render_template('index.html')
        else:
            uploaded_file = request.files['file']
            content_id = uuid.uuid4().hex
            try:
                bucket_name = 'multimodal-annihilator-ai.appspot.com'
                # Create a reference to the file in Cloud Storage
                bucket = storage.bucket(bucket_name)  # Get a reference to your storage bucket
                blob = bucket.blob(f"uploads/{uploaded_file.filename}")  # Customize file path as needed

                # Upload the file content
                blob.upload_from_string(uploaded_file.read(), content_type=uploaded_file.content_type)

                signed_url = util.util.generate_signed_url(bucket_name, f"uploads/{uploaded_file.filename}")

                # Save text content to Firebase (unchanged)
                doc_ref = db.collection('content').document(content_id)
                doc_ref.set({
                    'download_url': signed_url,
                })
                return redirect(url_for('response', content_id=content_id))
            except Exception as e:
                print(f"Error saving file content to Firebase: {e}")
                return render_template('index.html')

    else:
        return render_template('index.html')

@app.route('/response/<content_id>')
def response(content_id):
    try:
        # Retrieve content from Firebase based on content_id
        doc_ref = db.collection('content').document(content_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            if 'content' in data: # Check for text content
                content = data['content']
                doc_ref.delete()
                
                
                """
                apply ai stuff
                """
                
                #processed_content = util.util.process(content)
                processed_content = util.gemini.process_text(content)




                return render_template('response.html', response=processed_content)
            elif 'download_url' in data: # Check for download URL
                download_url = data['download_url']
                doc_ref.delete()
                _, downloaded_file = util.util.download_file(download_url)
                
                """
                apply ai stuff
                """
                processed_content = util.util.process(downloaded_file)




                os.remove(downloaded_file)
                return render_template('response.html', response=processed_content)               
            else:
                return "No content found for this ID!"
        else:
            return render_template('index.html')
    except Exception as e:
        print(f"Error retrieving content from Firebase: {e}")
        return render_template('index.html')

