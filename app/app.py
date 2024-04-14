from flask import Flask, render_template, request, redirect, url_for
from google.cloud import storage

app = Flask(__name__)

# Configure this environment variable or directly in your code
app.config['GCS_CREDENTIALS'] = 'gcp_credentials.json'
app.config['GCS_BUCKET'] = 'your-bucket-name'

# Initialize Google Cloud Storage
#storage_client = storage.Client.from_service_account_json(app.config['GCS_CREDENTIALS'])
#bucket = storage_client.get_bucket(app.config['GCS_BUCKET'])

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
