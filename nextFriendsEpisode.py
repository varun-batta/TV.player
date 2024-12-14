import random
import os
import subprocess
import vlc
import re
import json
from time import sleep

def get_episode():
    # Opening up episodeCount JSON to make sure no repetitions happen
    episodeInfo = {}
    with open('episodeCount.json') as f:
        episodeInfo = json.load(f)
        f.close()
    while True:
        # Generating a random season and episode
        season = random.randint(1, 10)
        seasonPath = "C:\\Users\\varun\\Videos\\F.R.I.E.N.D.S\\Season {}".format(season)
        episodeChoices = ["\\".join((seasonPath, f)) for f in os.listdir(seasonPath) if os.path.isfile("\\".join((seasonPath, f)))]
        episode = episodeChoices[random.randint(0, len(episodeChoices)-1)]
        # Making sure it's not repeating by using the JSON
        episodeCount = episodeInfo['F.R.I.E.N.D.S.']['episodeCount']
        totalEpisodeCount = episodeInfo['F.R.I.E.N.D.S.']['totalEpisodeCount']
        expectedCount = episodeCount // totalEpisodeCount
        episodeNameRegex = re.compile(r".*Season \d+\\(\d+[.]\d+(?:-\d+[.]\d+)?)")
        print(episode)
        episodeNumber = episodeNameRegex.match(episode)[1]
        if episodeInfo['F.R.I.E.N.D.S.']['episodes'][episodeNumber] == expectedCount:
            episodeInfo['F.R.I.E.N.D.S.']['episodeCount'] += 1
            episodeInfo['F.R.I.E.N.D.S.']['episodes'][episodeNumber] += 1
            break
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
    
while True:
    episode = get_episode()
    fileLength = get_length(episode)
    vlcPath = "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe"
    p = subprocess.Popen([vlcPath, episode, "--fullscreen", "--sub-track", "10"])
    sleep(fileLength+5)
    p.kill()