from flask import Flask, render_template, request, redirect, url_for
from firebase_admin import credentials, initialize_app, firestore
import uuid

cred = credentials.Certificate("serviceAccountKey.json")
default_app = initialize_app(cred) 
db = firestore.client()

app = Flask(__name__)

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
            print(f"Error saving content to Firebase: {e}")
            return redirect(url_for('index'))
    else:
        return render_template('index.html')

@app.route('/response/<content_id>')
def response(content_id):
    try:
        # Retrieve content from Firebase based on content_id
        doc_ref = db.collection('content').document(content_id)
        doc = doc_ref.get()
        if doc.exists:
            content = doc.to_dict()['content']
            # Delete content after display (comment out if you want to keep it)
            doc_ref.delete()

            processed_content = process(content)
            return render_template('response.html', response=processed_content)
        else:
            return redirect(url_for('index'))
    except Exception as e:
        print(f"Error retrieving content from Firebase: {e}")

if __name__ == "__main__":
    app.run(debug=True)
