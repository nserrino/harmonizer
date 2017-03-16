import argparse
import json
import numpy
import os
from hmmlearn import hmm
from transformation.rock_corpus_parser import HARMONY_EXT, parse_harmony
from transformation.resample_harmony_melody import get_harmony_melody_pairs, resample_song
from training.train_hmm import get_transition_matrix, get_start_probability, get_emission_matrix
from training.train_hmm import NUM_MELODY_NOTES, MELODY_STATES

parser = argparse.ArgumentParser()
parser.add_argument("--chords_list", help="Supported chords list (json)", required=True)
parser.add_argument("--harmony", help="Harmony files directory", required=True)
parser.add_argument("--melody", help="Melody files directory", required=True)
args = parser.parse_args()

harmony_root = os.path.abspath(args.harmony)
melody_root = os.path.abspath(args.melody)

harmony_paths = [os.path.join(harmony_root, f) for f in os.listdir(harmony_root)
                 if f.endswith(HARMONY_EXT)]

harmonies = []
for harmony_path in harmony_paths:
    try:
        parsed_harmony = parse_harmony(harmony_path)
        harmonies.append(parsed_harmony)
    except Exception as e:
        print "Failed to parse harmony at path:", harmony_path

with open(args.chords_list) as f:
    chord_list = json.loads(f.read())

# Compute transition matrix
transition_matrix = get_transition_matrix(harmonies, chord_list)
# Compute start probabilities
start_probs = get_start_probability(harmonies, chord_list)

harmony_filenames = os.listdir(harmony_root)
melody_filenames = os.listdir(melody_root)
pairs = get_harmony_melody_pairs(harmony_filenames, melody_filenames)
resamples = []

for pair in pairs:
    try:
        resample = resample_song(os.path.join(harmony_root, pair['harmony']),
                                 os.path.join(melody_root, pair['melody']))
        resamples.append(resample)
    except Exception as e:
        print "Encountered error on", pair['song'], ": Skipping."

# Compute emission matrix
emission_matrix = get_emission_matrix(resamples, chord_list)

n_observations = NUM_MELODY_NOTES
observations = MELODY_STATES
n_states = len(chord_list)
states = chord_list

model = hmm.MultinomialHMM(n_components=n_states, init_params="ste")
model.startprob_ = start_probs
model.transmat_ = transition_matrix
model.emissionprob_ = emission_matrix

numpy.savetxt("foo2.csv", transition_matrix, delimiter=",", fmt='%1.3f')

test = numpy.array([[4, 5, 5, 4, 4, 5, 10, 10, 10, 9, 9, 7]]).T
# model = model.fit(test)
logprob, output = model.decode(test, algorithm="viterbi")
print test
# print("Melody says:", ", ".join(map(lambda x: observations[x], test)))
print("Harmony says:", ", ".join(map(lambda x: states[x], output)))
