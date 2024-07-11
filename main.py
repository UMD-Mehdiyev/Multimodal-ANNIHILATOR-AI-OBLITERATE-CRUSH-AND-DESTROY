from flask import Flask, render_template, request, redirect, url_for
from firebase_admin import credentials, initialize_app, firestore, storage
import uuid
import datetime
import requests
import os

cred = credentials.Certificate("serviceAccountKey.json")
default_app = initialize_app(cred, {'storageBucket': 'multimodal-annihilator-ai.appspot.com'}) 
db = firestore.client()


app = Flask(__name__)

def download_file(url):
  # Common extensions to search for (adjust as needed)
  common_extensions = [".pdf", ".png", ".jpg", ".jpeg", ".wav", ".doc", ".txt"]

  # Split the URL path based on delimiters (adjust based on URL structure)
  url_parts = url.split("/")[-1].split("?")

  # Extract the filename part (assuming query string is separate)
  filename = url_parts[0]

  # Search for common extensions in the filename
  for extension in common_extensions:
    if extension in filename:
      final_filename = filename
      break  # Stop searching after finding the first match
  else:
      # No matching extension found, use the original filename
      final_filename = filename

  # Download the file using requests
  try:
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for unsuccessful downloads

    with open(final_filename, 'wb') as f:
      for chunk in response.iter_content(1024):
        if chunk:  # Filter out keep-alive new chunks
          f.write(chunk)

    return True, final_filename
  except requests.exceptions.RequestException as e:
    print(f"Error downloading file: {e}")
    return False, None
  

def generate_signed_url(bucket_name, file_path, expires_in=3600):  # Expires in 1 hour
  bucket = storage.bucket(bucket_name)
  blob = bucket.blob(file_path)
  expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expires_in)
  url = blob.generate_signed_url(expiration=expiration, method="GET")
  return url

def process(content):
    return f"Processing: {content}"

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
            print("AHHHHHHHHHHHHHHHHHHHHHH CONTENTTTTTTTTTTTTTTTTTTTTTTTT")
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
            print("FILEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEe")
            uploaded_file = request.files['file']
            content_id = uuid.uuid4().hex
            try:
                print("AHHHHH")
                bucket_name = 'multimodal-annihilator-ai.appspot.com'
                # Create a reference to the file in Cloud Storage
                bucket = storage.bucket(bucket_name)  # Get a reference to your storage bucket
                blob = bucket.blob(f"uploads/{uploaded_file.filename}")  # Customize file path as needed

                # Upload the file content
                blob.upload_from_string(uploaded_file.read(), content_type=uploaded_file.content_type)

                signed_url = generate_signed_url(bucket_name, f"uploads/{uploaded_file.filename}")

                print("made it here")
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
            print('ye')
            data = doc.to_dict()
            if 'content' in data: # Check for text content
                content = data['content']
                doc_ref.delete()
                processed_content = process(content)
                return render_template('response.html', response=processed_content)
            elif 'download_url' in data: # Check for download URL
                download_url = data['download_url']
                doc_ref.delete()
                _, downloaded_file = download_file(download_url)
                
                processed_content = process(downloaded_file)
                os.remove(downloaded_file)
                return render_template('response.html', response=processed_content)               
            else:
                return "No content found for this ID!"
        else:
            return render_template('index.html')
    except Exception as e:
        print(f"Error retrieving content from Firebase: {e}")
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
