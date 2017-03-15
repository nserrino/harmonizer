import argparse
import json
import os
import numpy
# import pandas
from ..transformation import rock_corpus_parser
# from resample_harmony_melody import resample_song

# Train a HMM, assuming input data in the rock corpus format


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
    num_transitions = 0

    for harmony in harmonies:
        last_chord = None
        for chord in harmony[rock_corpus_parser.ROMAN_NUMERAL]:
            if chord in chord_list:
                if last_chord is not None:
                    last_index = chord_list.index(last_chord)
                    this_index = chord_list.index(chord)
                    transitions[last_index][this_index] += 1
                    num_transitions += 1

                last_chord = chord
            else:
                # If not a valid chord, don't count this transition or the next one.
                last_chord = None

    return transitions / num_transitions


def get_emission_matrix():
    # For each melody note, the probability of each chord
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--harmony", help="Harmony files directory", required=True)
    parser.add_argument("--chords_list", help="Supported chords list (json)", required=True)
    # parser.add_argument("--melody", help="Melody files directory", required=True)
    args = parser.parse_args()

    harmony_paths = [os.path.join(args.harmony, f) for f in os.listdir(args.harmony)
                     if f.endswith(rock_corpus_parser.HARMONY_EXT)]

    harmonies = []
    for harmony_path in harmony_paths:
        try:
            parsed_harmony = rock_corpus_parser.parse_harmony(harmony_path)
            harmonies.append(parsed_harmony)
        except Exception as e:
            print e
            print "Failed to parse harmony at path:", harmony_path
            raise Exception("alkjfsd")

    with open(args.chords_list) as f:
        chord_list = json.loads(f.read())

    transition_matrix = get_transition_matrix(harmonies, chord_list)
    with transition_matrix.option_context('display.max_rows', None):
        print transition_matrix
