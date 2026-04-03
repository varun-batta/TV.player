import random
import os
import subprocess
import re
import json
import sys
from time import sleep
import time
import argparse

# Add these imports
import keyboard
import pygetwindow as gw

def get_episode(show='F.R.I.E.N.D.S.', random_mode=False):
    # Opening up episodeCount JSON to make sure no repetitions happen
    with open('episodeCount.json') as f:
        episodeInfo = json.load(f)
        f.close()

    episodes_dict = episodeInfo[show]['episodes']
    episode_keys = list(episodes_dict.keys())

    # Ensure lastPlayed exists
    if 'lastPlayed' not in episodeInfo[show]:
        episodeInfo[show]['lastPlayed'] = None

    if random_mode:
        # --- RANDOM MODE (existing logic) ---
        while True:
            season = random.randint(1, 10)
            seasonPath = f"C:\\Users\\varun\\Videos\\{show}\\Season {season}"
            episodeChoices = ["\\".join((seasonPath, f)) for f in os.listdir(seasonPath) if os.path.isfile("\\".join((seasonPath, f)))]
            episode = episodeChoices[random.randint(0, len(episodeChoices)-1)]
            episodeNameRegex = re.compile(r".*Season \d+\\(\d+[.]\d+(?:-\d+[.]\d+)?)")
            match = episodeNameRegex.match(episode)
            if not match:
                continue
            episodeNumber = match[1]
            episodeCount = episodeInfo[show]['episodeCount']
            totalEpisodeCount = episodeInfo[show]['totalEpisodeCount']
            expectedCount = episodeCount // totalEpisodeCount
            if episodes_dict[episodeNumber] == expectedCount:
                episodeInfo[show]['episodeCount'] += 1
                episodes_dict[episodeNumber] += 1
                episodeInfo[show]['lastPlayed'] = episodeNumber
                break
    else:
        # --- IN ORDER MODE ---
        last_played = episodeInfo[show]['lastPlayed']
        try:
            idx = episode_keys.index(last_played) if last_played else -1
        except ValueError:
            idx = -1
        next_idx = idx + 1
        if next_idx >= len(episode_keys):
            print("All episodes played!")
            print("Restarting from the beginning...")
            next_idx = 0
        next_episode_number = episode_keys[next_idx]
        # Find the file for this episode
        season_num = next_episode_number.split('.')[0]
        seasonPath = f"C:\\Users\\varun\\Videos\\{show}\\Season {season_num}"
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
        episodeInfo[show]['lastPlayed'] = next_episode_number

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

def is_vlc_foreground():
    try:
        win = gw.getActiveWindow()
        return win and "vlc" in win.title.lower()
    except Exception:
        return False

def is_vlc_playing():
    """
    Returns True if VLC is playing a file (window title contains ' - VLC media player'),
    False if just 'VLC media player' (idle or paused at no file).
    """
    try:
        win_list = gw.getWindowsWithTitle("VLC media player")
        if not win_list:
            return False
        # Use regex to check if any window title matches '.* - VLC media player'
        pattern = re.compile(r".+ - VLC media player")
        for w in win_list:
            if pattern.match(w.title):
                return True
        return False
    except Exception:
        return False

def parse_args():
    parser = argparse.ArgumentParser(description='TV Show Player')
    parser.add_argument('-r', '--random', action='store_true',
                      help='Play episodes in random order')
    parser.add_argument('-n', '--num-episodes', type=int,
                      help='Number of episodes to play (default: infinite)')
    parser.add_argument('-s', '--show', type=str, default='F.R.I.E.N.D.S.',
                      help='TV show to play (default: F.R.I.E.N.D.S.)')
    return parser.parse_args()

if __name__ == "__main__":
    print("Starting TV player...")
    args = parse_args()
    print(f"Random mode: {args.random}, Show: {args.show}")

    count = 0
    quit_flag = False
    print(f"Episodes to play: {'infinite' if args.num_episodes is None else args.num_episodes}")
    while (args.num_episodes is None or count < args.num_episodes) and not quit_flag:
        print(f"Playing episode {count + 1}...")
        episode = get_episode(show=args.show, random_mode=args.random)
        vlcPath = "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe"
        p = subprocess.Popen([vlcPath, episode, "--fullscreen", "--sub-track", "10"])

        sleep(2)
        # Wait until VLC is no longer playing a file
        while is_vlc_playing():
            if is_vlc_foreground() and keyboard.is_pressed('q'):
                print("Q pressed, quitting...")
                quit_flag = True

        p.kill()
        if quit_flag:
            print("Quitting after current episode.")
            break
        count += 1