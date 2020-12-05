import pytube
import numpy as np
from moviepy.editor import *
import time

class Editor:
    def __init__(self, title, path):
        self.data = VideoFileClip(path).subclip(0, 120)
        self.audio = self.data.audio
        self.title = title

    def process(self, gate=0.000048, separation=2):  # cube: gate=0.000047, separation = 1,2,4
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


def process(url, title):
    global starttime
    starttime = time.time()
    youtube = pytube.YouTube(url)
    print("downloading {}".format(youtube.title))
    video = youtube.streams.get_highest_resolution()  # get_lowest_resolution()
    path = video.download('./temp', title)
    editor = Editor(title, path)
    editor.process()


if __name__ == '__main__':
    starttime = 0
    process(input("url to video: "), input("file name: "))
    print("time {}".format(time.time()-starttime))
    # https://www.youtube.com/watch?v=HVnL7bAZgrE