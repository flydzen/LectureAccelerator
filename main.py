import pytube
import numpy as np
from moviepy.editor import *
import time

class Editor:
    def __init__(self, title, path):
        self.data = AudioFileClip(path).subclip(0, 120)
        self.title = title

    def calc_volume(self, gate=0.000048, separation=2):  # cube: gate=0.000047, separation = 1,2,4
        last = 0
        clips = []
        percent = -1

        def cut(data, i):
            return data.subclip(i/separation, i/separation + 1/separation)

        def volume(i):
            return np.power(cut(self.audio, i).to_soundarray(fps=4000), 2).mean()

        def add(i):
            nonlocal last, clips
            if volume(i) < gate:
                clips.append(self.data.subclip(last, i/separation))
                clips.append(self.data.subclip(i/separation, i/separation + 1/separation).fx(vfx.speedx, 5))
                last = i/separation + 1/separation

        print("accelerating")
        n = int(self.data.duration)
        for j in range(n*separation - 1):
            newp = 100*j//(n*separation-1)
            if newp > percent:
                print(newp)
                percent = newp
            add(j)
        clips.append(self.data.subclip(last, self.data.duration))
        final = concatenate_videoclips(clips)
        print("rendering")
        final.write_videofile('./video/{}.mp4'.format(self.title), fps=30, threads=4)
        final.close()
        print("finished")

    def test(self, gate=0.000048, separation=2):
        def cut(data, i):
            return data.subclip(i/separation, i/separation + 1/separation)

        def volume(i):
            return np.power(cut(self.data, i).to_soundarray(fps=4000), 2).mean()

        data = [volume(i) for i in range(int(self.data.duration)*separation-1)]
        return data


def gen_ev_listener(title):
    def event_listener(stream, path):
        editor = Editor(title, path)
        print(editor.test())

    return event_listener


def download(url):
    global starttime
    starttime = time.time()
    youtube = pytube.YouTube(url)
    print("downloading {}".format(youtube.title))
    youtube.register_on_complete_callback(gen_ev_listener(youtube.title))
    video = youtube.streams.filter(only_audio=True).all()
    video[0].download('./temp')


if __name__ == '__main__':
    starttime = 0
    download(input("url to video: "))
    print("time {}".format(time.time()-starttime))
    # https://www.youtube.com/watch?v=HVnL7bAZgrE