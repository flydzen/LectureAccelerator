import pytube
import numpy as np
from moviepy.editor import *


class Editor:
    def __init__(self, title, path):
        self.data = VideoFileClip(path).subclip(100, 200)
        self.audio = self.data.audio
        self.title = title

    def calc_volume(self, gate=0.000048, separation=2):  # cube: gate=0.000047, separation = 1,2,4
        last = 0
        clips = []

        def cut(data, i):
            return data.subclip(i/separation, i/separation + 1/separation)

        def volume(i):
            return np.power(cut(self.audio, i).to_soundarray(fps=22000), 2).mean()

        def add(i):
            nonlocal last, clips
            if volume(i) < gate:
                clips.append(self.data.subclip(last, i/separation))
                clips.append(self.data.subclip(i/separation, i/separation + 1/separation).fx(vfx.speedx, 5))
                last = i/separation + 1/separation

        print("accelerating")
        n = int(self.data.duration)
        for j in range(n*separation - 1):
            add(j)
        final = concatenate_videoclips(clips)
        print("rendering")
        final.write_videofile('{}.mp4'.format(self.title))
        final.close()
        print("finished")


def gen_ev_listener(title):
    def event_listener(stream, path):
        editor = Editor(title, path)
        editor.calc_volume()

    return event_listener


def download(url):
    youtube = pytube.YouTube(url)
    print("downloading {}".format(youtube.title))
    youtube.register_on_complete_callback(gen_ev_listener(youtube.title))
    video = youtube.streams.filter(subtype='mp4').get_highest_resolution()
    video.download('./temp')


if __name__ == '__main__':
    download(input("url to video: "))
    # https://www.youtube.com/watch?v=HVnL7bAZgrE