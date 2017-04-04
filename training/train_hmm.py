import numpy
from transformation import rock_corpus_parser

# Train a HMM, assuming input data in the rock corpus format

NUM_NOTES = 12
NOTE_STATES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


# If 'chords' is defined, the start probability should be relative to that list.
# Otherwise, the output of the model will simply be the notes 0-11.
# Same for the methods get_transition_matrix and get_emission_matrix.
def get_start_probability(harmonies, chords):
    # Probability of each chord/note, in a vacuum
    if chords is not None:
        start = numpy.zeros(len(chords))
    else:
        start = numpy.zeros(NUM_NOTES)

    num_entries = 0

    for harmony in harmonies:
        if chords is not None:
            for chord in harmony[rock_corpus_parser.ROMAN_NUMERAL]:
                if chord in chords:
                    index = chords.index(chord)
                    start[index] += 1
                    num_entries += 1
        else:
            for chord_root in harmony[rock_corpus_parser.HARMONY_REL_ROOT]:
                start[chord_root] += 1
                num_entries += 1

    return start / num_entries


def get_transition_matrix(harmonies, chords):
    # Probability of changing from one chord to another
    if chords is not None:
        transitions = numpy.zeros(shape=(len(chords), len(chords)))
        num_transitions = numpy.zeros(len(chords))
    else:
        transitions = numpy.zeros(shape=(NUM_NOTES, NUM_NOTES))
        num_transitions = numpy.zeros(NUM_NOTES)

    for harmony in harmonies:
        last_chord = None
        if chords is not None:
            for chord in harmony[rock_corpus_parser.ROMAN_NUMERAL]:
                if chord in chords:
                    if last_chord is not None:
                        last_index = chords.index(last_chord)
                        this_index = chords.index(chord)
                        transitions[last_index][this_index] += 1
                        num_transitions[last_index] += 1

                    last_chord = chord
                else:
                    # If not a chord in the input list, don't count this transition or the next one.
                    last_chord = None
        else:
            for chord_root in harmony[rock_corpus_parser.HARMONY_REL_ROOT]:
                if last_chord is not None:
                    transitions[last_chord][chord_root] += 1
                    num_transitions[last_chord] += 1
                last_chord = chord_root

    # Make sure each one has at least 1 transition to avoid a divide by 0
    for i in xrange(len(num_transitions)):
        if num_transitions[i] == 0:
            num_transitions[i] += 1

    return transitions / num_transitions[:, None]


def get_emission_matrix(resamples, chords=None):
    # For each chord, the probability of matching each melody note
    if chords is not None:
        emission = numpy.zeros(shape=(len(chords), NUM_NOTES))
        num_pairs = numpy.zeros(len(chords))
    else:
        emission = numpy.zeros(shape=(NUM_NOTES, NUM_NOTES))
        num_pairs = numpy.zeros(NUM_NOTES)

    for i in xrange(len(resamples)):
        resample = resamples[i].dropna()
        for index, row in resample.iterrows():
            rel_melody = int(row[rock_corpus_parser.MELODY_REL_PITCH])

            if chords is not None:
                chord = row[rock_corpus_parser.ROMAN_NUMERAL]
                if chord in chords:
                    index = chords.index(chord)
                    emission[index][rel_melody] += 1
                    num_pairs[index] += 1
            else:
                chord_root = int(row[rock_corpus_parser.HARMONY_REL_ROOT])
                emission[chord_root][rel_melody] += 1
                num_pairs[chord_root] += 1

    # Make sure each chord has at least 1 pair to avoid a divide by 0
    for i in xrange(len(num_pairs)):
        if num_pairs[i] == 0:
            num_pairs[i] += 1

    return emission / num_pairs[:, None]
