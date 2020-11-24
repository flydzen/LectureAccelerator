import pytube
import numpy as np
from moviepy.editor import *


class Editor:
    def __init__(self, title, path):
        self.data = VideoFileClip(path).subclip(100, 800)
        self.audio = self.data.audio
        self.title = title

    def calc_volume(self, gate=0.009):
        def add(ind, i: VideoClip):
            if volumes[ind] < gate:
                return i.fx(vfx.speedx, 5)
            else:
                return i

        n = int(self.data.duration)
        print("cutting")
        clips = [self.data.subclip(i, i + 1) for i in range(n - 1)]
        volume = lambda arr: np.sqrt(((1.0 * arr) ** 2).mean())
        print("calc volumes")
        volumes = [volume(clips[i].audio.to_soundarray(fps=22000)) for i in range(n - 1)]
        print(volumes)
        print("accelerating")
        clips = [add(ind, i) for ind, i in enumerate(clips)]
        print("rendering")
        final = concatenate_videoclips(clips)
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
    # url_ = "https://www.youtube.com/watch?v=BL58YWapQFM"
    download(input("url to video: "))
    # download(url_)
