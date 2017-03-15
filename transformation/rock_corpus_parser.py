import pandas

HARMONY_EXT = ".clt"
MELODY_EXT = ".nlt"

SECONDS = "Seconds"
BEATS = "Beats"
ROMAN_NUMERAL = "Roman numeral"
HARMONY_REL_ROOT = "Harmony key-relative root"
HARMONY_KEY_TONIC = "Harmony key tonic"
HARMONY_DIATONIC_ROOT = "Harmony diatonic root"
HARMONY_ABS_ROOT = "Harmony absolute root"
MELODY_ABS_PITCH = "Melody absolute pitch"
MELODY_REL_PITCH = "Melody key-relative pitch"


def parse_harmony(harmony_path):
    harmony = pandas.read_csv(harmony_path, header=None, delimiter=r"\s+")
    harmony.dropna()
    harmony.columns = [SECONDS, BEATS, ROMAN_NUMERAL, HARMONY_REL_ROOT, HARMONY_DIATONIC_ROOT,
                       HARMONY_KEY_TONIC, HARMONY_ABS_ROOT]
    # Remove data we don't need
    del harmony[SECONDS]
    del harmony[HARMONY_REL_ROOT]
    del harmony[HARMONY_DIATONIC_ROOT]
    del harmony[HARMONY_ABS_ROOT]
    return harmony


def parse_melody(melody_path):
    melody = pandas.read_csv(melody_path, header=None, delimiter=r"\s+")
    melody.dropna()
    melody.columns = [SECONDS, BEATS, MELODY_ABS_PITCH, MELODY_REL_PITCH]
    # Remove data we don't need
    del melody[SECONDS]
    return melody
