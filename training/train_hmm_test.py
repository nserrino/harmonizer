import numpy
from StringIO import StringIO
from transformation import rock_corpus_parser, resample_harmony_melody
from train_hmm import get_transition_matrix, get_start_probability, get_emission_matrix
from train_hmm import NUM_NOTES

TEST_HARMONY_CLT = """0.214   0.00    I     0   6   7   8
                      4.239   2.00    I     0   6   7   8
                      8.220   4.00    ?i    1   6   7   8
                      10.226  5.00    V     1   6   7   8
                      12.200  6.00    II    2   6   7   8
                      20.202  10.00   II    2   6   7   8"""

TEST_MELODY_NLT = """15.437  0.00    57  4
                     15.689  1.00    57  4
                     15.940  5.00    61  5
                     16.500  7.00    61  5
                     17.699  9.00    57  6"""

TEST_CHORD_LIST = [
    "I", "II", "III", "IV", "V"
]


def test_get_transition_matrix_chords():
    expected = numpy.zeros(shape=(len(TEST_CHORD_LIST), len(TEST_CHORD_LIST)))
    expected[0][0] = 1.0
    expected[4][1] = 1.0
    expected[1][1] = 1.0

    harmony = rock_corpus_parser.parse_harmony(StringIO(TEST_HARMONY_CLT))
    transition_matrix = get_transition_matrix([harmony], TEST_CHORD_LIST)
    assert(numpy.array_equal(expected, transition_matrix))


def test_get_transition_matrix_numeric():
    expected = numpy.zeros(shape=(NUM_NOTES, NUM_NOTES))
    expected[0][0] = 0.5
    expected[0][1] = 0.5
    expected[1][1] = 0.5
    expected[1][2] = 0.5
    expected[2][2] = 1.0

    harmony = rock_corpus_parser.parse_harmony(StringIO(TEST_HARMONY_CLT))
    transition_matrix = get_transition_matrix([harmony], None)
    assert(numpy.array_equal(expected, transition_matrix))


def test_get_start_probability_chords():
    expected = numpy.zeros(len(TEST_CHORD_LIST))
    expected[0] = 2.0 / 5
    expected[1] = 2.0 / 5
    expected[4] = 1.0 / 5

    harmony = rock_corpus_parser.parse_harmony(StringIO(TEST_HARMONY_CLT))
    start_prob = get_start_probability([harmony], TEST_CHORD_LIST)
    assert(numpy.array_equal(expected, start_prob))


def test_get_start_probability_numeric():
    expected = numpy.zeros(NUM_NOTES)
    expected[0] = 2.0 / 6
    expected[1] = 2.0 / 6
    expected[2] = 2.0 / 6

    harmony = rock_corpus_parser.parse_harmony(StringIO(TEST_HARMONY_CLT))
    start_prob = get_start_probability([harmony], None)
    assert(numpy.array_equal(expected, start_prob))


def test_get_emission_matrix_chords():
    expected = numpy.zeros(shape=(len(TEST_CHORD_LIST), NUM_NOTES))
    # I always maps to 4 in the above example
    expected[0][4] = 1.0
    # V maps to 4,5
    expected[4][4] = 1.0 / 2
    expected[4][5] = 1.0 / 2
    # II maps to 5, 6
    expected[1][5] = 1.0 / 2
    expected[1][6] = 1.0 / 2

    resampled = resample_harmony_melody.resample_song(StringIO(TEST_HARMONY_CLT),
                                                      StringIO(TEST_MELODY_NLT))
    emission = get_emission_matrix([resampled], TEST_CHORD_LIST)
    assert(numpy.array_equal(expected, emission))


def test_get_emission_matrix_numeric():
    expected = numpy.zeros(shape=(NUM_NOTES, NUM_NOTES))
    # I always maps to 4
    expected[0][4] = 1.0
    expected[1][4] = 2.0 / 3
    expected[1][5] = 1.0 / 3
    expected[2][5] = 2.0 / 4
    expected[2][6] = 2.0 / 4

    resampled = resample_harmony_melody.resample_song(StringIO(TEST_HARMONY_CLT),
                                                      StringIO(TEST_MELODY_NLT))
    emission = get_emission_matrix([resampled], None)
    assert(numpy.array_equal(expected, emission))
