import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash
from atproto import Client, models
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'dev-secret-key')

# Initialize Bluesky client
client = Client()

def authenticate():
    """Authenticate with Bluesky using env variables"""
    handle = os.getenv('BLUESKY_HANDLE')
    password = os.getenv('BLUESKY_PASSWORD')
    
    if not handle or not password:
        raise ValueError("Missing Bluesky credentials")
    
    if not handle.endswith(".bsky.social"):
        handle += ".bsky.social"
    
    client.login(handle, password)
    print(f"Authenticated as {handle}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        post_text = request.form.get('text', '')
        
        if len(post_text) > 300:
            flash('Post too long (max 300 characters)', 'danger')
            return redirect(url_for('index'))
        
        try:
            record = client.send_post(text=post_text)
            flash('Post published successfully! 🚀', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error posting: {str(e)}', 'danger')
    
    return render_template('index.html')

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    authenticate()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
