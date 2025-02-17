import os
import time
from atproto import Client, models
from datetime import datetime

# Initialize Bluesky client
client = Client()

def authenticate():
    """Authenticate with Bluesky using env variables"""
    handle = os.getenv('BLUESKY_HANDLE')
    password = os.getenv('BLUESKY_PASSWORD')
    
    if not handle or not password:
        raise ValueError("Missing Bluesky credentials in environment variables")
    
    client.login(handle, password)
    print(f"Authenticated as {handle} at {datetime.now().isoformat()}")

def post_message(text):
    """Create a new post"""
    try:
        client.send_post(text=text)
        print(f"Posted: {text}")
    except Exception as e:
        print(f"Post failed: {str(e)}")

def reply_to_mentions():
    """Check and reply to mentions"""
    try:
        notifications = client.get_notifications()
        for notification in notifications.notifications:
            if notification.reason == 'mention' and not notification.is_read:
                post_uri = notification.uri
                reply_text = "🤖 Beep boop! Thanks for mentioning me!"
                
                parent_ref = models.create_strong_ref(notification.record)
                client.send_post(
                    text=reply_text,
                    reply_to=models.AppBskyFeedPost.ReplyRef(parent=parent_ref, root=parent_ref)
                )
                print(f"Replied to {post_uri}")
    except Exception as e:
        print(f"Reply error: {str(e)}")

def main_loop():
    """Main execution loop with intervals"""
    while True:
        try:
            # Example scheduled action
            current_time = datetime.now().strftime("%H:%M")
            post_message(f"🕒 Automated post at {current_time} UTC")
            
            # Check for mentions every run
            reply_to_mentions()
            
            # Sleep for 15 minutes (900 seconds)
            print("Sleeping for 15 minutes...")
            time.sleep(900)
            
        except Exception as e:
            print(f"Main loop error: {str(e)}")
            time.sleep(60)  # Wait before retrying

if __name__ == "__main__":
    authenticate()
    main_loop()
