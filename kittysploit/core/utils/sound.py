from nava import play, stop
import time
from kittysploit.core.utils.function_module import file_exists


def play_sound(filename=None):
    if file_exists(filename):
        play(filename)


def play_and_stop(filename, timeout=3):
    if file_exists(filename):
        sound_id = play(filename, async_mode=True)
        time.sleep(timeout)
        stop(sound_id)
