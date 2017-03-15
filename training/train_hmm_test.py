from train_hmm import get_transition_matrix
from StringIO import StringIO
from rock_corpus_parser import parse_harmony

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
    harmony = parse_harmony(StringIO(TEST_HARMONY_CLT))
    print harmony
