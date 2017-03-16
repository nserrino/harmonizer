import argparse
import json
import os
from transformation.rock_corpus_parser import HARMONY_EXT, parse_harmony
from transformation.resample_harmony_melody import get_harmony_melody_pairs, resample_song
from training.train_hmm import get_transition_matrix, get_start_probability, get_emission_matrix

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

transition_matrix = get_transition_matrix(harmonies, chord_list)
# numpy.savetxt("foo2.csv", transition_matrix, delimiter=",", fmt='%1.3f')

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

emission = get_emission_matrix(resamples, chord_list)
print emission
