import random
import os
import subprocess
import re
import json
import sys
from time import sleep

def get_episode(random_mode=False):
    # Opening up episodeCount JSON to make sure no repetitions happen
    with open('episodeCount.json') as f:
        episodeInfo = json.load(f)
        f.close()

    episodes_dict = episodeInfo['F.R.I.E.N.D.S.']['episodes']
    episode_keys = list(episodes_dict.keys())

    # Ensure lastPlayed exists
    if 'lastPlayed' not in episodeInfo['F.R.I.E.N.D.S.']:
        episodeInfo['F.R.I.E.N.D.S.']['lastPlayed'] = None

    if random_mode:
        # --- RANDOM MODE (existing logic) ---
        while True:
            season = random.randint(1, 10)
            seasonPath = f"C:\\Users\\varun\\Videos\\F.R.I.E.N.D.S\\Season {season}"
            episodeChoices = ["\\".join((seasonPath, f)) for f in os.listdir(seasonPath) if os.path.isfile("\\".join((seasonPath, f)))]
            episode = episodeChoices[random.randint(0, len(episodeChoices)-1)]
            episodeNameRegex = re.compile(r".*Season \d+\\(\d+[.]\d+(?:-\d+[.]\d+)?)")
            match = episodeNameRegex.match(episode)
            if not match:
                continue
            episodeNumber = match[1]
            episodeCount = episodeInfo['F.R.I.E.N.D.S.']['episodeCount']
            totalEpisodeCount = episodeInfo['F.R.I.E.N.D.S.']['totalEpisodeCount']
            expectedCount = episodeCount // totalEpisodeCount
            if episodes_dict[episodeNumber] == expectedCount:
                episodeInfo['F.R.I.E.N.D.S.']['episodeCount'] += 1
                episodes_dict[episodeNumber] += 1
                episodeInfo['F.R.I.E.N.D.S.']['lastPlayed'] = episodeNumber
                break
    else:
        # --- IN ORDER MODE ---
        last_played = episodeInfo['F.R.I.E.N.D.S.']['lastPlayed']
        try:
            idx = episode_keys.index(last_played) if last_played else -1
        except ValueError:
            idx = -1
        next_idx = idx + 1
        if next_idx >= len(episode_keys):
            print("All episodes played!")
            sys.exit(0)
        next_episode_number = episode_keys[next_idx]
        # Find the file for this episode
        season_num = next_episode_number.split('.')[0]
        seasonPath = f"C:\\Users\\varun\\Videos\\F.R.I.E.N.D.S\\Season {season_num}"
        # Find file that starts with the episode number
        episode_file = None
        for f in os.listdir(seasonPath):
            if f.startswith(next_episode_number):
                episode_file = "\\".join((seasonPath, f))
                break
        if not episode_file:
            print(f"Episode file for {next_episode_number} not found in {seasonPath}")
            sys.exit(1)
        episode = episode_file
        episodeInfo['F.R.I.E.N.D.S.']['lastPlayed'] = next_episode_number

    # Updating episodeCount JSON
    updatedEpisodeCountJSON = json.dumps(episodeInfo, indent=4)
    with open('episodeCount.json', 'w') as f:
        f.write(updatedEpisodeCountJSON)
        f.close()
    return episode

def get_length(filename):
    print(filename)
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename], shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)

if __name__ == "__main__":
    random_mode = "--random" in sys.argv or "-r" in sys.argv

    # Default to infinite loop if -n not provided
    num_episodes = None
    for i, arg in enumerate(sys.argv):
        if arg == "-n" and i + 1 < len(sys.argv):
            try:
                num_episodes = int(sys.argv[i + 1])
            except ValueError:
                print("Invalid value for -n. Please provide an integer.")
                sys.exit(1)

    count = 0
    while num_episodes is None or count < num_episodes:
        episode = get_episode(random_mode=random_mode)
        fileLength = get_length(episode)
        vlcPath = "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe"
        p = subprocess.Popen([vlcPath, episode, "--fullscreen", "--sub-track", "10"])
        sleep(fileLength + 5)
        p.kill()
        count += 1