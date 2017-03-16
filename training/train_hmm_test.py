import numpy
from StringIO import StringIO
from transformation import rock_corpus_parser, resample_harmony_melody
from train_hmm import get_transition_matrix, get_start_probability, get_emission_matrix
from train_hmm import NUM_MELODY_NOTES


TEST_HARMONY_CLT = """0.214   0.00    I   0   1   9   9
                      4.239   2.00    I   9   6   9   6
                      8.220   4.00    ?   5   4   9   2
                      10.226  5.00    V   7   5   9   4
                      12.200  6.00    I   0   1   9   9
                      20.202  10.00   I   9   6   9   6"""

TEST_MELODY_NLT = """15.437  0.00    57  0
                     15.689  1.00    57  0
                     15.940  5.00    61  4
                     16.500  7.00    61  4
                     17.699  9.00    57  0"""

TEST_CHORD_LIST = [
    "I", "II", "III", "IV", "V"
]


def test_get_transition_matrix():
    expected = numpy.zeros(shape=(len(TEST_CHORD_LIST), len(TEST_CHORD_LIST)))
    expected[0][0] = 1
    expected[4][0] = 1

    harmony = rock_corpus_parser.parse_harmony(StringIO(TEST_HARMONY_CLT))
    transition_matrix = get_transition_matrix([harmony], TEST_CHORD_LIST)
    assert(numpy.array_equal(expected, transition_matrix))


def test_get_start_probability():
    expected = numpy.zeros(len(TEST_CHORD_LIST))
    expected[0] = 4.0 / 5
    expected[4] = 1.0 / 5

    harmony = rock_corpus_parser.parse_harmony(StringIO(TEST_HARMONY_CLT))
    start_prob = get_start_probability([harmony], TEST_CHORD_LIST)
    assert(numpy.array_equal(expected, start_prob))


def test_get_emission_matrix():
    expected = numpy.zeros(shape=(len(TEST_CHORD_LIST), NUM_MELODY_NOTES))
    expected[0][0] = 5.0 / 7
    expected[0][4] = 2.0 / 7
    expected[4][0] = 1.0 / 2
    expected[4][4] = 1.0 / 2

    resampled = resample_harmony_melody.resample_song(StringIO(TEST_HARMONY_CLT),
                                                      StringIO(TEST_MELODY_NLT))
    emission = get_emission_matrix([resampled], TEST_CHORD_LIST)
    assert(numpy.array_equal(expected, emission))
