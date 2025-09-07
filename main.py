"""
SDVX Asphyxia to Kamaitachi Converter

Designed for the plugin at https://github.com/22vv0/asphyxia_plugins

This script reads SDVX score data from an Asphyxia database file and converts it
to the JSON format expected by Kamaitachi.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# Meta information for the final output
META = {
    "game": "sdvx",
    "playtype": "Single",
    "service": "Asphyxia"
}

# Configuration constants
DATABASE_PATH = "sdvx@asphyxia.db"
ASPHYXIA_PROFILE_ID = "ACA11374C2D83E9A"
PRESERVE_FAILS = True
OUTPUT_FILE = "output.json"

# Mapping of plugin clear type to Kamaitachi clear type
CLEAR_TYPE_MAP = {
    1: "FAILED",
    2: "CLEAR",
    3: "EXCESSIVE CLEAR",
    4: "ULTIMATE CHAIN",
    5: "PERFECT ULTIMATE CHAIN",
    6: "MAXXIVE CLEAR"
}

# Mapping of plugin difficulty to Kamaitachi difficulty
DIFFICULTY_MAP = {
    0: "NOV",
    1: "ADV",
    2: "EXH",
    3: "ANY_INF",
    4: "MXM"
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_plays_database(db_path: Path) -> List[Dict]:
    """Load score database from file."""
    try:
        with db_path.open("r", encoding="utf-8") as db_file:
            data_points = [json.loads(line) for line in db_file]
            plays = [play for play in data_points if play.get("collection", None) == "music"]

        return plays
    except json.JSONDecodeError:
        logger.warning("Invalid JSON format in database file")
        raise
    except Exception as e:
        logger.error(f"Error loading database: {e}")
        raise


def filter_user_scores(scores: List[Dict[str, Any]], profile_id: str) -> List[Dict[str, Any]]:
    """Filter scores to find the specified user's scores."""
    scores = [
        point for point in scores
        if point.get("__refid") == profile_id and point.get("__s") == "plugins_profile"
    ]

    logger.info(f"Found {len(scores)} scores for user {profile_id}")
    return scores


def convert_play(play: Dict) -> Optional[Dict]:
    """Convert a play from the database to Kamaitachi format."""
    try:
        score = int(play["score"])
        exscore = int(play["exscore"]) if play.get("exscore", 0) > 0 else None
        song_id = str(play["mid"])
        time_achieved = int(play["createdAt"]["$$date"])

        # Clear type
        clear_type = play["clear"]
        if clear_type not in CLEAR_TYPE_MAP:
            logger.warning(f"Unknown clear type {play['clear']} for song {song_id}")
            return None
        lamp = CLEAR_TYPE_MAP[clear_type]

        # Chart difficulty
        difficulty_type = play["type"]
        if difficulty_type not in DIFFICULTY_MAP:
            logger.warning(f"Unknown difficulty type {play['difficulty']} for song {song_id}")
            return None
        difficulty = DIFFICULTY_MAP[difficulty_type]

        # Build output
        output = {
            "matchType": "sdvxInGameID",
            "identifier": song_id,
            "score": score,
            "lamp": lamp,
            "difficulty": difficulty,
            "timeAchieved": time_achieved
        }

        # EX SCORE might not be present depending on settings and version
        if exscore is not None and exscore > 0:
            output["optional"] = {}
            output["optional"]["exScore"] = int(exscore)

        return output
    except Exception as e:
        logger.error(f"Error converting play: {e}")
        return None


def save_results(results: Dict[str, Any], output_path: Path) -> None:
    """Save converted file to JSON."""
    try:
        with output_path.open("w", encoding="utf-8") as output_file:
            json.dump(results, output_file, indent=None)

        logger.info(f"File {output_path} saved")
    except Exception as e:
        logger.error(f"Error saving results: {e}")


def main():
    logger.info("Config:")
    logger.info(f"DATABASE_PATH: {DATABASE_PATH}")
    logger.info(f"OUTPUT_FILE: {OUTPUT_FILE}")
    logger.info(f"ASPHYXIA_PROFILE_ID: {ASPHYXIA_PROFILE_ID}")
    logger.info(f"PRESERVE_FAILS: {PRESERVE_FAILS}")

    logger.info("Starting scores conversion")
    data_points = load_plays_database(Path(DATABASE_PATH))

    # Filter selected user's scores
    plays_for_user = filter_user_scores(data_points, ASPHYXIA_PROFILE_ID)

    # Convert each score
    score_results = []
    for play in plays_for_user:
        score_info = convert_play(play)
        if score_info:
            # Filter out fails
            if PRESERVE_FAILS or score_info["lamp"] != "FAILED":
                score_results.append(score_info)

    logger.info(f"Conversion resulted in {len(score_results)} valid scores")

    # Final result
    result = {
        "meta": META,
        "scores": score_results
    }

    # Write output to file
    save_results(result, Path(OUTPUT_FILE))

    logger.info(f"Scores conversion complete")


if __name__ == "__main__":
    main()
