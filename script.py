from pathlib import Path
import requests
import feedparser
from decouple import config

from log import has_processed_episode, log_episode

BUZZSPROUT_API_KEY = config("BUZZSPROUT_API_KEY")
PODCAST_ID = 1501156
FEED = f"https://feeds.buzzsprout.com/{PODCAST_ID}.rss"
PUT_URL = f'https://www.buzzsprout.com/api/{PODCAST_ID}/' + 'episodes/{episode_id}/transcript'
TRANSCTIPT_DIR = config("TRANSCTIPT_DIR", default='/Users/bbelderbos/code/pybites-ai/scripts/outputs/podcast')
HEADERS = {
    'Authorization': f'Token token={BUZZSPROUT_API_KEY}',
    'Content-Type': 'application/json'
}

episode_dict = {file.stem.split('-')[0]: str(file.resolve()) for file in
                Path(TRANSCTIPT_DIR).glob('*.srt')}
print(episode_dict)

entries = feedparser.parse(FEED).entries
for entry in entries[::-1]:
    episode_id = entry.id.replace('Buzzsprout-', '')
    print("processing", episode_id)

    if episode_id not in episode_dict:
        print("ERROR: no transcript found for", episode_id)
        break

    if has_processed_episode(episode_id):
        print("already processed", episode_id)
        continue

    file_path = episode_dict[episode_id]

    with open(file_path, 'rb') as f:
        url = PUT_URL.format(episode_id=episode_id)
        files = {'transcript-file': f}
        data = {'transcript-format': 'srt'}
        response = requests.post(url, headers=HEADERS, files=files, data=data)

        print(response.status_code)
        print(response.json())
        if response.status_code == 200:
            log_episode(episode_id)

        break
