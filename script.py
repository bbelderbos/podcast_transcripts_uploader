from pathlib import Path
import requests
import feedparser
from decouple import config

BUZZSPROUT_API_KEY = config("BUZZSPROUT_API_KEY")
PODCAST_ID = config("PODCAST_ID")
FEED = f"https://feeds.buzzsprout.com/{PODCAST_ID}.rss"
TRANSCRIPT_ENDPOINT = (
    f"https://www.buzzsprout.com/api/{PODCAST_ID}/" + "episodes/{episode_id}/transcript"
)
TRANSCTIPT_DIR = config("TRANSCTIPT_DIR")
HEADERS = {
    "Authorization": f"Token token={BUZZSPROUT_API_KEY}",
    "User-Agent": config("USER_AGENT"),
}

PUBLIC_EPISODE_URL = (
    f"https://www.buzzsprout.com/{PODCAST_ID}/" + "{episode_id}/transcript"
)


def get_transcripts(transcript_dir=TRANSCTIPT_DIR) -> dict[str, str]:
    return {
        file.stem.split("-")[0]: str(file.resolve())
        for file in Path(transcript_dir).glob("*.srt")
    }


def get_episode_ids(feed=FEED) -> list[str]:
    entries = feedparser.parse(feed).entries
    ids = []
    for entry in entries:
        episode_id = entry.id.replace("Buzzsprout-", "")
        ids.append(episode_id)
    return ids


def upload_transcripts(episode_ids: list[str], transcripts: dict[str, str]) -> None:
    for episode_id in episode_ids:
        if episode_id not in transcripts:
            print("ERROR: no transcript found for", episode_id)
            continue

        transcript_url = PUBLIC_EPISODE_URL.format(episode_id=episode_id)
        response = requests.head(transcript_url, headers=HEADERS)
        if response.status_code == 200:
            print("already processed", episode_id)
            continue

        file_path = transcripts[episode_id]

        with open(file_path, "rb") as f:
            url = TRANSCRIPT_ENDPOINT.format(episode_id=episode_id)
            print("processing", url, file_path)
            files = {"transcript_file": f}
            data = {"transcript_format": "srt"}

            response = requests.post(url, headers=HEADERS, files=files, data=data)

            if response.status_code == 204:
                print("uploaded", episode_id)
            else:
                print("ERROR uploading", episode_id)
                print("Status Code:", response.status_code)
                print("Response Text:", response.text)
                try:
                    print("Response JSON:", response.json())
                except ValueError:
                    print("Response is not JSON")


if __name__ == "__main__":
    episodes_ids = get_episode_ids()
    transcripts = get_transcripts()
    upload_transcripts(episodes_ids, transcripts)
