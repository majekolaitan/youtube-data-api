import re
import csv
import pandas as pd
from googleapiclient.discovery import build

# Function to convert ISO 8601 duration format to seconds
def iso_duration_to_seconds(duration):
    match = re.match(
        r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',
        duration
    )
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds

# Set up the YouTube API client
api_key = 'AIzaSyBwYPwFRztcO0oDskxuNCJxc4sKQ5diYto'
youtube = build('youtube', 'v3', developerKey=api_key)

# Get video ID from URL
def get_video_id(url):
    regex = r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)'
    match = re.match(regex, url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube URL")

# Get video details
def get_video_details(video_url):
    video_id = get_video_id(video_url)
    response = youtube.videos().list(
        part='snippet,contentDetails,statistics',
        id=video_id
    ).execute()

    items = response.get('items')
    if not items:
        raise ValueError("No video found for the provided URL")

    video_title = items[0]['snippet']['title']
    duration = items[0]['contentDetails']['duration']
    duration_seconds = iso_duration_to_seconds(duration)
    view_count = items[0]['statistics']['viewCount']
    upload_date = items[0]['snippet']['publishedAt']
    
    return video_title, duration_seconds, view_count, upload_date

# Read URLs from file
input_file = 'urls.txt'
output_file = 'video_details.csv'

with open(input_file, 'r') as file:
    urls = file.read().splitlines()

# Get video details and write to CSV
video_details = []
for url in urls:
    try:
        title, duration, view_count, upload_date = get_video_details(url)
        video_details.append([url, title, duration, view_count, upload_date])
    except Exception as e:
        print(f"Error processing URL {url}: {e}")

# Convert to DataFrame and save to CSV
df = pd.DataFrame(video_details, columns=['URL', 'Title', 'Duration (seconds)', 'View Count', 'Upload Date'])
df.to_csv(output_file, index=False)

print(f"Video details exported to {output_file}")
