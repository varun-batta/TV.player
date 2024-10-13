import random
import os
import subprocess
import vlc
from time import sleep

def get_length(filename):
    print(filename)
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename], shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)
    
    
while True:
    season = random.randint(1, 10)
    seasonPath = "C:\\Users\\varun\\Videos\\F.R.I.E.N.D.S\\Season {}".format(season)
    episodeChoices = ["\\".join((seasonPath, f)) for f in os.listdir(seasonPath) if os.path.isfile("\\".join((seasonPath, f)))]
    episode = episodeChoices[random.randint(0, len(episodeChoices)-1)]

    fileLength = get_length(episode)
    vlcPath = "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe"
    os.execv(vlcPath, [" ", '"' + episode + '"'])
    # print(fileLength)
    sleep(fileLength+5)
    # media_player = vlc.MediaPlayer(episode)
    # media_player.play()
    # sleep(5)
    # while media_player.is_playing():
         # sleep(1)
    # media_player.release()