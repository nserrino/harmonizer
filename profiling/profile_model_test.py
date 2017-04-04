import numpy
import os
from profile_model import (get_training_set_distribution, get_lstm_result_distribution,
                           get_result_emission_matrix)
from transformation.resample_harmony_melody import resample_song

TEST_SONG = 'a_hard_days_night_tdc'
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
HARMONY_ROOT = os.path.join(ROOT, 'rock-corpus/rs200_harmony_clt')
MELODY_ROOT = os.path.join(ROOT, 'rock-corpus/rs200_melody_nlt')


def test_get_training_set_distribution():
    resample = resample_song(os.path.join(HARMONY_ROOT, TEST_SONG + '.clt'),
                             os.path.join(MELODY_ROOT, TEST_SONG + '.nlt'))
    num_notes, distribution = get_training_set_distribution([resample])
    assert(num_notes == 400)
    expected = [142, 0, 0, 0, 16, 103, 0, 60, 0, 29, 50, 0]
    assert(distribution == expected)
    return


def test_get_lstm_result_distribution():
    result_sequence = [
        numpy.array([0, 0.9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.1]),
        numpy.array([0, 0, 0, 0, 0, 0, 0.55, 0.45, 0, 0, 0, 0]),
        numpy.array([0, 0.4, 0.3, 0.2, 0.1, 0, 0, 0, 0, 0, 0, 0])
    ]
    expected = [0, 2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
    num_notes, distribution = get_lstm_result_distribution([result_sequence])
    assert(num_notes == 3)
    assert(distribution == expected)


def test_get_result_emission_matrix():
    resample = resample_song(os.path.join(HARMONY_ROOT, TEST_SONG + '.clt'),
                             os.path.join(MELODY_ROOT, TEST_SONG + '.nlt'))
    output_harmony = []
    for i in xrange(len(resample)):
        if i % 2:
            output_harmony.append(0)
        else:
            output_harmony.append(5)

    emission = get_result_emission_matrix([resample], [output_harmony])

    for i in xrange(len(emission)):
        expected_0 = numpy.array([0.055, 0., 0.025, 0.08, 0.1, 0.18, 0., 0.345, 0.03, 0.08, 0.04,
                                  0.065])
        expected_5 = numpy.array([0.08, 0., 0.02, 0.095, 0.1, 0.17, 0.005, 0.315, 0.03, 0.075,
                                  0.06, 0.05])
        expected_else = numpy.zeros(12)
        if i is 0:
            assert(numpy.array_equal(expected_0, emission[i]))
        elif i is 5:
            assert(numpy.array_equal(expected_5, emission[i]))
        else:
            assert(numpy.array_equal(expected_else, emission[i]))
