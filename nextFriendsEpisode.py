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

def load_episode_info():
    with open('episodeCount.json') as f:
        return json.load(f)

def save_episode_info(episode_info):
    with open('episodeCount.json', 'w') as f:
        f.write(json.dumps(episode_info, indent=4))

def get_show_names(episode_info):
    return [
        key for key, value in episode_info.items()
        if isinstance(value, dict) and 'episodes' in value
    ]

def choose_show_interactively(show_names):
    print("Choose a show:")
    for i, show_name in enumerate(show_names, start=1):
        print(f"  {i}. {show_name}")

    while True:
        choice = input(f"Enter number (1-{len(show_names)}): ").strip()
        if not choice.isdigit():
            print("Please enter a number.")
            continue

        idx = int(choice)
        if 1 <= idx <= len(show_names):
            return show_names[idx - 1]

        print("Invalid choice. Try again.")

def resolve_show(change_show, explicit_show=None):
    episode_info = load_episode_info()
    show_names = get_show_names(episode_info)

    if not show_names:
        print("No shows found in episodeCount.json")
        sys.exit(1)

    if change_show:
        selected_show = choose_show_interactively(show_names)
    else:
        last_played_show = episode_info.get('lastPlayedShow')
        if last_played_show in show_names:
            selected_show = last_played_show
        elif explicit_show in show_names:
            selected_show = explicit_show
        else:
            selected_show = show_names[0]

    episode_info['lastPlayedShow'] = selected_show
    save_episode_info(episode_info)
    return selected_show

def get_available_seasons(show):
    episodeInfo = load_episode_info()

    if show not in episodeInfo:
        return []

    episode_keys = list(episodeInfo[show]['episodes'].keys())
    seasons = sorted({int(k.split('.')[0]) for k in episode_keys})
    return seasons

def get_episode(show='F.R.I.E.N.D.S.', random_mode=False):
    # Opening up episodeCount JSON to make sure no repetitions happen
    episodeInfo = load_episode_info()

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
    save_episode_info(episodeInfo)
    return episode

def set_start_from_season(show, start_season, num_episodes=None):
    """
    Seed lastPlayed so the next in-order episode starts from a random episode
    in the selected season (never the season's last episode).
    """
    episodeInfo = load_episode_info()

    if show not in episodeInfo:
        print(f"Show '{show}' not found in episodeCount.json")
        sys.exit(1)

    episodes_dict = episodeInfo[show]['episodes']
    episode_keys = list(episodes_dict.keys())
    season_prefix = f"{start_season}."
    season_episode_keys = [k for k in episode_keys if k.startswith(season_prefix)]

    if not season_episode_keys:
        print(f"Season {start_season} not found for show '{show}'")
        sys.exit(1)

    # Keep the full requested run inside the chosen season and never start on season finale.
    requested_count = 1 if num_episodes is None else num_episodes
    max_start_by_count = len(season_episode_keys) - requested_count
    max_start_by_not_last = len(season_episode_keys) - 2
    max_start_idx = min(max_start_by_count, max_start_by_not_last)

    if max_start_idx < 0:
        print(
            f"Cannot start in Season {start_season} with --num-episodes={num_episodes}. "
            f"Season has {len(season_episode_keys)} episodes and start cannot be the last one."
        )
        sys.exit(1)

    chosen_idx = random.randint(0, max_start_idx)
    chosen_episode = season_episode_keys[chosen_idx]
    global_idx = episode_keys.index(chosen_episode)
    episodeInfo[show]['lastPlayed'] = episode_keys[global_idx - 1] if global_idx > 0 else None

    save_episode_info(episodeInfo)

    print(
        f"Start season set to {start_season}. "
        f"Starting episode will be {chosen_episode}."
    )

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
    parser.add_argument('-c', '--change-show', action='store_true',
                      help='Choose a show interactively and set it as last played')
    parser.add_argument('-r', '--random', action='store_true',
                      help='Play random order (or random first episode only when --num-episodes > 1)')
    parser.add_argument('-n', '--num-episodes', type=int,
                      help='Number of episodes to play (default: infinite)')
    parser.add_argument('-s', '--show', type=str, default='F.R.I.E.N.D.S.',
                      help='Fallback show if no last played show is stored')
    parser.add_argument('-S', '--start-season', type=int,
                      help='Start from a random episode in this season, then continue in order')
    return parser.parse_args()

if __name__ == "__main__":
    print("Starting TV player...")
    args = parse_args()
    selected_show = resolve_show(args.change_show, args.show)
    print(f"Random mode: {args.random}, Show: {selected_show}")

    if args.num_episodes is not None and args.num_episodes <= 0:
        print("--num-episodes must be greater than 0")
        sys.exit(1)

    if args.start_season is not None:
        available_seasons = get_available_seasons(selected_show)
        if not available_seasons:
            print(f"Show '{selected_show}' not found in episodeCount.json")
            sys.exit(1)
        if args.start_season not in available_seasons:
            seasons_str = ", ".join(str(s) for s in available_seasons)
            print(
                f"Invalid --start-season {args.start_season} for show '{selected_show}'. "
                f"Valid seasons: {seasons_str}"
            )
            sys.exit(1)
        set_start_from_season(selected_show, args.start_season, args.num_episodes)

    count = 0
    quit_flag = False
    print(f"Episodes to play: {'infinite' if args.num_episodes is None else args.num_episodes}")
    while (args.num_episodes is None or count < args.num_episodes) and not quit_flag:
        print(f"Playing episode {count + 1}...")
        # Hybrid behavior: with -r and -n > 1, first episode is random, then continue in order.
        use_random_mode = args.random
        if args.start_season is not None:
            use_random_mode = False
        elif args.random and args.num_episodes is not None and args.num_episodes > 1:
            use_random_mode = count == 0

        episode = get_episode(show=selected_show, random_mode=use_random_mode)
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