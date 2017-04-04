import argparse
import json
import os
import pickle
from keras.models import load_model

from model_server import generate_hmm_sequence
from profiling.profile_model import (get_training_set_distribution, get_lstm_result_distribution,
                                     get_hmm_result_distribution)
from transformation.rock_corpus_parser import HARMONY_EXT, MELODY_EXT, MELODY_REL_PITCH
from transformation.resample_harmony_melody import get_harmony_melody_pairs, resample_song
from training.train_lstm import prepare_samples
from training.train_hmm import get_emission_matrix

num_notes = 12

parser = argparse.ArgumentParser()
parser.add_argument("--model", help="Model path.", required=True)
parser.add_argument("--harmony", help="Harmony files directory", required=True)
parser.add_argument("--melody", help="Melody files directory", required=True)
parser.add_argument('--timesteps', help="Number of timesteps (LSTM)", type=int, required=True)
parser.add_argument('--test_set', help="Test set songs for model", required=True)
parser.add_argument('--distribution', help="Get the musical note distributions",
                    action="store_true")
parser.add_argument('--emission', help="Get the emission matrices", action="store_true")
args = parser.parse_args()

harmony_root = os.path.abspath(args.harmony)
melody_root = os.path.abspath(args.melody)
harmony_filenames = os.listdir(harmony_root)
melody_filenames = os.listdir(melody_root)
pairs = get_harmony_melody_pairs(harmony_filenames, melody_filenames)

with open(args.test_set) as data_file:
    test_set = json.load(data_file)

training_pairs = [x for x in pairs if x not in test_set]
training_resamples = []
for pair in training_pairs:
    try:
        resample = resample_song(os.path.join(harmony_root, pair['harmony']),
                                 os.path.join(melody_root, pair['melody']))
        training_resamples.append(resample)
    except Exception as e:
        print "Encountered error on training song", pair['song'], ": Skipping."

if args.distribution:
    print "Input distribution:", get_training_set_distribution(training_resamples)

if args.emission:
    print "Input emission matrix:", get_emission_matrix(training_resamples)
    raise Exception('kdslafj')

test_resamples = []
for song in test_set:
    try:
        resample = resample_song(os.path.join(harmony_root, song + HARMONY_EXT),
                                 os.path.join(melody_root, song + MELODY_EXT))
        test_resamples.append(resample)
    except Exception as e:
        print "Encountered error on", pair['song'], ": Skipping."

if args.model.endswith('.h5'):
    model = load_model(args.model)
    testX, testY = prepare_samples(test_resamples, False, args.timesteps)
    generated_harmonies = model.predict(testX, batch_size=32, verbose=1)

    if args.distribution:
        print "LSTM distribution:", get_lstm_result_distribution(generated_harmonies)

elif args.model.endswith('.pkl'):
    f = open(args.model, 'r')
    model = pickle.load(f)
    outputs = []
    for resample in test_resamples:
        sequence = resample[MELODY_REL_PITCH].tolist()
        output = generate_hmm_sequence(sequence, model, False)
        outputs.append(output['sequence'])

    if args.distribution:
        print "HMM distribution:", get_hmm_result_distribution(outputs)
else:
    print "Unsupported model type:", model
