import os
import time
import openai
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from atproto import Client, models
from datetime import datetime

# Initialize Flask and Bluesky client
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET')
client = Client()
openai.api_key = os.getenv('OPENAI_API_KEY')

def authenticate():
    """Authenticate with Bluesky"""
    handle = os.getenv('BLUESKY_HANDLE')
    password = os.getenv('BLUESKY_PASSWORD')
    
    if not handle or not password:
        raise ValueError("Missing Bluesky credentials")
    
    if not handle.endswith(".bsky.social"):
        handle += ".bsky.social"
    
    client.login(handle, password)
    print(f"Authenticated as {handle}")

def generate_ai_post():
    """Generate post using GPT-4"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": """Create 3 Bluesky posts with:
- Current trends
- 1-2 hashtags
- Humorous tone
- Under 250 characters"""
            }],
            temperature=0.7,
            max_tokens=150
        )
        return [line for line in response.choices[0].message.content.split("\n") if line.strip()]
    except Exception as e:
        print(f"AI Error: {str(e)}")
        return []

@app.route('/generate', methods=['POST'])
def generate_post():
    """Generate AI post options"""
    try:
        options = generate_ai_post()
        return jsonify({"options": options})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        post_text = request.form.get('text', '')
        
        if len(post_text) > 300:
            flash('Post too long (max 300 characters)', 'danger')
            return redirect(url_for('index'))
        
        try:
            client.send_post(text=post_text)
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
