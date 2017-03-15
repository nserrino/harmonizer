# from train_hmm import get_transition_matrix
import numpy
from StringIO import StringIO
from ..transformation import rock_corpus_parser
from train_hmm import get_transition_matrix


TEST_HARMONY_CLT = """0.214   0.00    I   0   1   9   9
                      4.239   2.00    I   9   6   9   6
                      8.220   4.00    x   5   4   9   2
                      10.226  5.00    V   7   5   9   4
                      12.200  6.00    I   0   1   9   9
                      20.202  10.00   I   9   6   9   6"""

TEST_CHORD_LIST = [
    "I", "II", "III", "IV", "V"
]


def test_get_transition_matrix():
    expected = numpy.zeros(shape=(len(TEST_CHORD_LIST), len(TEST_CHORD_LIST)))
    expected[0][0] = 2
    expected[4][0] = 1

    harmony = rock_corpus_parser.parse_harmony(StringIO(TEST_HARMONY_CLT))
    transition_matrix = get_transition_matrix([harmony], TEST_CHORD_LIST)

    assert(numpy.array_equal(expected, transition_matrix))
