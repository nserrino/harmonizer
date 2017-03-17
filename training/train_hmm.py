import numpy
from transformation import rock_corpus_parser

# Train a HMM, assuming input data in the rock corpus format

NUM_MELODY_NOTES = 12
MELODY_STATES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


def get_start_probability(harmonies, chord_list):
    # Probability of each chord, in a vacuum
    start = numpy.zeros(len(chord_list))
    num_entries = 0

    for harmony in harmonies:
        for chord in harmony[rock_corpus_parser.ROMAN_NUMERAL]:
            if chord in chord_list:
                index = chord_list.index(chord)
                start[index] += 1
                num_entries += 1

    return start / num_entries


def get_transition_matrix(harmonies, chord_list):
    # Probability of changing from one chord to another
    transitions = numpy.zeros(shape=(len(chord_list), len(chord_list)))
    num_transitions = numpy.zeros(len(chord_list))

    for harmony in harmonies:
        last_chord = None
        for chord in harmony[rock_corpus_parser.ROMAN_NUMERAL]:
            if chord in chord_list:
                if last_chord is not None:
                    last_index = chord_list.index(last_chord)
                    this_index = chord_list.index(chord)
                    transitions[last_index][this_index] += 1
                    num_transitions[last_index] += 1

                last_chord = chord
            else:
                # If not a valid chord, don't count this transition or the next one.
                last_chord = None

    # Make sure each one has at least 1 transition to avoid a divide by 0
    for i in xrange(len(chord_list)):
        if num_transitions[i] == 0:
            num_transitions[i] += 1

    return transitions / num_transitions[:, None]


def get_emission_matrix(resamples, chord_list):
    # For each chord, the probability of matching each melody note
    emission = numpy.zeros(shape=(len(chord_list), NUM_MELODY_NOTES))
    num_pairs = numpy.zeros(len(chord_list))

    for resample in resamples:
        for index, row in resample.iterrows():
            chord = row[rock_corpus_parser.ROMAN_NUMERAL]
            rel_melody = row[rock_corpus_parser.MELODY_REL_PITCH]
            if chord in chord_list:
                index = chord_list.index(chord)
                emission[index][rel_melody] += 1
                num_pairs[index] += 1

    # Make sure each chord has at least 1 pair to avoid a divide by 0
    for i in xrange(len(chord_list)):
        if num_pairs[i] == 0:
            num_pairs[i] += 1

    print emission
    numpy.savetxt('emission_matrix.csv', emission, delimiter=',', fmt='%d')
    return emission / num_pairs[:, None]
