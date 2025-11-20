import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# OAuth setup
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
creds = None

if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            'client_secret.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

youtube = googleapiclient.discovery.build(
    'youtube', 'v3', credentials=creds)

# Your channel ID
CHANNEL_ID = 'UCcZLpkXsqshrXveN2uTTWaQ'

# Find active live stream
print("Finding live stream...")
search = youtube.search().list(
    part='id',
    channelId=CHANNEL_ID,
    eventType='live',
    type='video',
    maxResults=1
).execute()

video_id = None
if not search['items']:
    print("No live stream found on the default channel!")
    video_id = input(
        "Please enter the YouTube Video ID of the live stream you want to monitor: ").strip()
    if not video_id:
        print("No video ID provided. Exiting.")
        exit()
else:
    video_id = search['items'][0]['id']['videoId']
    print(f"Live stream found: {video_id}")

# Get live chat ID
try:
    video = youtube.videos().list(
        part='liveStreamingDetails',
        id=video_id
    ).execute()

    if not video['items']:
        print("Video not found or invalid ID.")
        exit()

    live_details = video['items'][0].get('liveStreamingDetails')
    if not live_details:
        print(
            "This video does not seem to be a live stream or has no live streaming details.")
        exit()

    live_chat_id = live_details.get('activeLiveChatId')
    if not live_chat_id:
        print("No active live chat found for this stream (chat might be disabled).")
        exit()

    print(f"Live chat ID: {live_chat_id}\n")
    print("Listening for comments...")

    # Stream comments
    next_page = None
    while True:
        try:
            response = youtube.liveChatMessages().list(
                liveChatId=live_chat_id,
                part='snippet,authorDetails',
                pageToken=next_page
            ).execute()

            for item in response['items']:
                if item['snippet']['type'] == 'textMessageEvent':
                    author = item['authorDetails']['displayName']
                    message = item['snippet']['textMessageDetails']['messageText']
                    print(f"{author}: {message}")

            next_page = response.get('nextPageToken')
            # Wait for the polling interval specified by the API
            time.sleep(response.get('pollingIntervalMillis', 5000) / 1000)

        except KeyboardInterrupt:
            print("\nStopped")
            break
        except Exception as e:
            print(f"Error fetching messages: {e}")
            time.sleep(5)

except Exception as e:
    print(f"An error occurred: {e}")
