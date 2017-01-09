from guitar import Fingering

from collections import namedtuple
import logging

# Logger used for outputting tabs - avoids ugliness/interleaved lines when using print
log = logging.getLogger("Tab")

def print_melody_tab(melody, durations=None, fname=None):
    """
    Prints a guitar tab, either to stdout or a file.

    Args:
        melody: list of Fingering structs.
        durations: list of floats, representing the duration of each note. It can be in beats, seconds, whatever. It will be scaled so the tab looks decent.
        fname: If included, method will write tab to file. Otherwise, tab goes to stdout.
    """

    if durations and len(durations) != len(melody):
        raise ValueError("Length of durations must match length of melody: %d != %d" % (len(durations), len(melody)))

    # scale durations to a reasonable integer for printing
    if durations:
        durations = map(lambda d: int(d * 64), durations)
        min_dur = min(durations)
        durations = map(lambda d: int(d / min_dur), durations)

    n = len(melody)

    lines = ["|--"] * 6

    # 2 characters per note, and 2 characters of spacing (unless durations is defined)
    for i in range(n):
        f = melody[i]
        if type(f) is Fingering:
            f = [f]
        for j in range(6):
            is_note_played = False
            for note in f:
                if note.string == j:
                    # Write the fret number
                    is_note_played = True
                    if note.fret >= 10:
                        lines[j] += str(note.fret)
                    else:
                        lines[j] += str(note.fret) + "-"
                    break
            if not is_note_played:
                lines[j] += "--"
        # Add spacing
        if durations:
            lines = map(lambda line: line + "-" * durations[i], lines)
        else:
            # Default (if durations aren't provided) is to just add two hyphens.
            lines = map(lambda line: line + "--", lines)

    # Finish each line cleanly
    for i in range(5, -1, -1):
        lines[i] += "----|\n"

    # Output in reverse order (because string order is high to low in printed tabs.
    if fname:
        with open(fname, "w") as outfile:
            for line in reversed(lines):
                outfile.write(line)
    else:
        # One print call, because lines can be grossly interspersed if debug logs aren't flushed.
        output = '\n' + ''.join(reversed(lines))
        log.info(output)

