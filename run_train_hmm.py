import argparse
import json
import os
import pickle

from hmmlearn import hmm
from transformation.rock_corpus_parser import HARMONY_EXT, parse_harmony
from transformation.resample_harmony_melody import get_harmony_melody_pairs, resample_song
from training.train_hmm import get_transition_matrix, get_start_probability, get_emission_matrix
from training.train_hmm import NUM_NOTES, NOTE_STATES

parser = argparse.ArgumentParser()
parser.add_argument("--chords", help="Supported chords list (json). If not provided, the "
                                     "generated model will output notes from [0-11]")
parser.add_argument("--harmony", help="Harmony files directory", required=True)
parser.add_argument("--melody", help="Melody files directory", required=True)
parser.add_argument('--output', help="Destination to store pkl file", required=True)
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
        print "Failed to parse harmony at path:", harmony_path, e
        raise e


if args.chords is not None:
    with open(args.chords) as f:
        chords = json.loads(f.read())
else:
    chords = None

# Compute transition matrix
transition_matrix = get_transition_matrix(harmonies, chords)

# Compute start probabilities
start_probs = get_start_probability(harmonies, chords)

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
emission_matrix = get_emission_matrix(resamples, chords)

n_observations = NUM_NOTES
observations = NOTE_STATES
n_states = NUM_NOTES if chords is None else len(chords)
states = NOTE_STATES if chords is None else chords

model = hmm.MultinomialHMM(n_components=n_states, init_params="ste")
model.startprob_ = start_probs
model.transmat_ = transition_matrix
model.emissionprob_ = emission_matrix

out = open(args.output, 'w')
pickle.dump(model, out)
out.close()
