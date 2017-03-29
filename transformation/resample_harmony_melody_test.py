import os
from resample_harmony_melody import resample_song
from rock_corpus_parser import (HARMONY_EXT, MELODY_EXT, BEATS, ROMAN_NUMERAL, HARMONY_REL_ROOT,
                                HARMONY_KEY_TONIC, HARMONY_DIATONIC_ROOT, HARMONY_ABS_ROOT,
                                MELODY_ABS_PITCH, MELODY_REL_PITCH)

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
TEST_SONG = 'a_hard_days_night_tdc'
TEST_HARMONY = os.path.join(ROOT, 'rock-corpus/rs200_harmony_clt', TEST_SONG + HARMONY_EXT)
TEST_MELODY = os.path.join(ROOT, 'rock-corpus/rs200_melody_nlt', TEST_SONG + MELODY_EXT)


def test_resample_song():
    song = resample_song(TEST_HARMONY, TEST_MELODY)
    columns = song.columns.tolist()
    expected = [BEATS, HARMONY_ABS_ROOT, HARMONY_DIATONIC_ROOT, HARMONY_KEY_TONIC,
                HARMONY_REL_ROOT, MELODY_ABS_PITCH, MELODY_REL_PITCH, ROMAN_NUMERAL]
    assert(columns == expected)
    assert(len(song) == 400)
