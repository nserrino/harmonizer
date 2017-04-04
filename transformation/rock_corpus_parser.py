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
    harmony.columns = [SECONDS, BEATS, ROMAN_NUMERAL, HARMONY_REL_ROOT, HARMONY_DIATONIC_ROOT,
                       HARMONY_KEY_TONIC, HARMONY_ABS_ROOT]
    # Remove data we don't need
    del harmony[SECONDS]
    harmony = harmony.dropna()
    harmony[HARMONY_DIATONIC_ROOT] = harmony[HARMONY_DIATONIC_ROOT].astype(int)
    harmony[HARMONY_KEY_TONIC] = harmony[HARMONY_KEY_TONIC].astype(int)
    harmony[HARMONY_REL_ROOT] = harmony[HARMONY_REL_ROOT].astype(int)
    return harmony


def parse_melody(melody_path):
    melody = pandas.read_csv(melody_path, header=None, delimiter=r"\s+")
    melody.columns = [SECONDS, BEATS, MELODY_ABS_PITCH, MELODY_REL_PITCH]
    # Remove data we don't need
    del melody[SECONDS]
    melody = melody.dropna()
    melody[MELODY_ABS_PITCH] = melody[MELODY_ABS_PITCH].astype(int)
    melody[MELODY_REL_PITCH] = melody[MELODY_REL_PITCH].astype(int)
    return melody
