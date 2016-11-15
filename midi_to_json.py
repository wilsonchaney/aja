import json
import os

from math import ceil
from music21 import *
from Queue import Queue
from threading import Thread
from time import time

# If true, this will convert all midi files in music/ directory to .json files.
# If false, it will convert FILE_LIMIT files.
PROCESS_ALL = False
FILE_LIMIT = 10

NUM_WORKER_THREADS = 4


def convert(path):
    fname, ext = os.path.splitext(path)

    midi_file = converter.parse(path)

    data = {
        "tracks": []
    }

    for part in midi_file.parts:

        track = []
        for n in part.notesAndRests:
            pitches = []
            if not isinstance(n, note.Rest):
                for p in n.pitches:
                    pitches.append(p.pitchClass + 12 * p.octave)

            n_ = {
                "pitches": pitches,
                "duration": float(n.duration.quarterLength)
            }
            track.append(n_)

        data["tracks"].append(track)

    # Add mega-rests so durations of all tracks match
    track_lengths = [sum(n["duration"] for n in t) for t in data["tracks"]]
    max_length = ceil(max(track_lengths))

    if __name__ == '__main__':
        for i in range(len(data["tracks"])):
            track_len = track_lengths[i]
            if track_len < max_length:
                big_rest = {
                    "pitches": [],
                    "duration": float(max_length - track_len)
                }
                data["tracks"][i].append(big_rest)

    json.dump(data, open(fname + ".json", "w"))


def should_process(path):
    fname, ext = os.path.splitext(path)
    output_path = fname + ".json"
    return (ext == ".mid" and not os.path.exists(output_path)) or PROCESS_ALL


def worker_thread():
    while True:
        path = q.get()
        fname = os.path.basename(path)

        success = False

        start = time()
        try:
            convert(path)
            success = True
        except Exception as e:
            print "Failed %s" % fname
        end = time()

        if success:
            proc_time = end - start
            print "Converted %s in %.2f seconds." \
                  % (fname, proc_time)

        q.task_done()

def run():
    global FILE_LIMIT
    folder_name = "music"
    files = os.listdir(folder_name)

    if not FILE_LIMIT:
        FILE_LIMIT = float('inf')

    for i in range(4):
        t = Thread(target=worker_thread)
        t.daemon = True
        t.start()

    num_queued = 0

    for f in files:
        path = os.path.join(folder_name, f)
        if should_process(path):
            q.put(path)
            num_queued += 1
            if num_queued == FILE_LIMIT:
                break
        else:
            print "Skipping", f

    q.join()  # block until all tasks are done

if __name__ == "__main__":
    q = Queue()
    run()
