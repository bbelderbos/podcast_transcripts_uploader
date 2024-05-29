from decouple import config

LOG_FILE = config("LOG_FILE", default="log.txt")


def has_processed_episode(episode_id: str) -> bool:
    """
    Check if we already processed this episode.
    """
    try:
        with open(LOG_FILE, "r") as f:
            episode_ids = f.read().splitlines()
            return str(episode_id) in episode_ids
    except FileNotFoundError:
        return False


def log_episode(episode_id: str) -> None:
    """
    Log the episode as processed.
    """
    if has_processed_episode(episode_id):
        raise ValueError(f"Episode {episode_id} already processed")

    with open(LOG_FILE, "a") as f:
        f.write(str(episode_id) + "\n")
