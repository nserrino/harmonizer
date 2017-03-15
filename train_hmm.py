import argparse
import os
import pandas
from resample_harmony_melody import resample_song

# Train a HMM, assuming input data in the rock corpus format


def get_start_probability():
    # Probability of each chord, in a vacuum
    return


def get_transition_matrix():
    # Probability of changing from one chord to another
    return


def get_emission_matrix():
    # For each melody note, the probability of each chord
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--harmony", help="Harmony files directory")#, required=True)
    parser.add_argument("--melody", help="Mlody files directory")#, required=True)
    parser.add_argument("--chords_list", help="Supported chords list (json)")#, required=True)
