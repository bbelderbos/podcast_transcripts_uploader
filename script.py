from pathlib import Path
import requests
import feedparser
from decouple import config

from log import has_processed_episode, log_episode

BUZZSPROUT_API_KEY = config("BUZZSPROUT_API_KEY")
PODCAST_ID = config("PODCAST_ID")
FEED = f"https://feeds.buzzsprout.com/{PODCAST_ID}.rss"
PUT_URL = (
    f"https://www.buzzsprout.com/api/{PODCAST_ID}/" + "episodes/{episode_id}/transcript"
)
TRANSCTIPT_DIR = config("TRANSCTIPT_DIR")
HEADERS = {
    "Authorization": f"Token token={BUZZSPROUT_API_KEY}",
    "Content-Type": "application/json",
}


def get_transcripts(transcript_dir=TRANSCTIPT_DIR) -> dict[str, str]:
    return {
        file.stem.split("-")[0]: str(file.resolve())
        for file in Path(TRANSCTIPT_DIR).glob("*.srt")
    }


def get_episode_ids(feed=FEED) -> list[str]:
    entries = feedparser.parse(feed).entries
    ids = []
    for entry in entries:
        episode_id = entry.id.replace("Buzzsprout-", "")
        ids.append(episode_id)
    return ids


def upload_transcripts(episode_ids: list[str], transcripts: dict[str, str]) -> None:
    # TODO: remove slicing
    for episode_id in episode_ids[:10]:
        if episode_id not in transcripts:
            print("ERROR: no transcript found for", episode_id)
            continue

        # cannot get this from API episode endpoint
        if has_processed_episode(episode_id):
            print("already processed", episode_id)
            continue

        file_path = transcripts[episode_id]

        with open(file_path, "rb") as f:
            url = PUT_URL.format(episode_id=episode_id)
            files = {"transcript-file": f}
            data = {"transcript-format": "srt"}

            response = requests.post(url, headers=HEADERS, files=files, data=data)

            if response.status_code == 200:
                print("uploaded", episode_id)
                log_episode(episode_id)
            else:
                print("ERROR uploading", episode_id, response.text)


if __name__ == "__main__":
    episodes_ids = get_episode_ids()
    transcripts = get_transcripts()
    upload_transcripts(episodes_ids, transcripts)
