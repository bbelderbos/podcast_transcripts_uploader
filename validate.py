from pprint import pprint as pp

import feedparser

from script import FEED


def all_episodes_have_transcripts(feed=FEED) -> bool:
    entries = feedparser.parse(feed).entries
    for entry in entries:
        try:
            if not entry.podcast_transcript["url"]:
                return False
        except (AttributeError, KeyError):
            print(f"Transcript missing for {entry.title}")
            return False
    return True


if __name__ == "__main__":
    result = all_episodes_have_transcripts()
    if result:
        print("All episodes have transcripts.")
    else:
        print("Some episodes are missing transcripts.")
