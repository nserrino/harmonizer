import argparse
import json
import os

from transformation.rock_corpus_parser import HARMONY_EXT, MELODY_EXT
from transformation.resample_harmony_melody import get_harmony_melody_pairs, resample_song
from training.train_lstm import prepare_samples, train_model
from keras.models import load_model

num_notes = 12

parser = argparse.ArgumentParser()
parser.add_argument("--model", help="Model path.", required=True)
parser.add_argument("--harmony", help="Harmony files directory", required=True)
parser.add_argument("--melody", help="Melody files directory", required=True)
parser.add_argument('--timesteps', help="Number of timesteps in the model", type=int, required=True)
parser.add_argument('--test_set', help="JSON listing songs to hold out as test set")
parser.add_argument("--train", help="Train the model", action="store_true")
parser.add_argument("--eval", help="Evaluate the model", action="store_true")
parser.add_argument("--synth", help="Synthesize more training data", action="store_true")
args = parser.parse_args()

harmony_root = os.path.abspath(args.harmony)
melody_root = os.path.abspath(args.melody)
harmony_filenames = os.listdir(harmony_root)
melody_filenames = os.listdir(melody_root)
pairs = get_harmony_melody_pairs(harmony_filenames, melody_filenames)

if args.test_set is not None:
    with open(args.test_set) as data_file:
        test_set = json.load(data_file)
else:
    test_set = []

training_pairs = [x for x in pairs if x not in test_set]
training_resamples = []
for pair in training_pairs:
    try:
        resample = resample_song(os.path.join(harmony_root, pair['harmony']),
                                 os.path.join(melody_root, pair['melody']))
        training_resamples.append(resample)
    except Exception as e:
        print "Encountered error on training song", pair['song'], ": Skipping."

trainX, trainY = prepare_samples(training_resamples, args.synth, args.timesteps)

if (args.train):
    model = train_model(args.timesteps, num_notes, trainX, trainY)
    model.save(args.model)
else:
    model = load_model(args.model)

if args.eval:
    test_pairs = []
    for song in test_set:
        entry = {}
        entry['harmony'] = song + HARMONY_EXT
        entry['melody'] = song + MELODY_EXT
        test_pairs.append(entry)

    test_resamples = []
    for pair in test_pairs:
        try:
            resample = resample_song(os.path.join(harmony_root, pair['harmony']),
                                     os.path.join(melody_root, pair['melody']))
            training_resamples.append(resample)
        except Exception as e:
            print "Encountered error on", pair['song'], ": Skipping."
    testX, testY = prepare_samples(training_resamples, args.synth, args.timesteps)

    generated_harmonies = model.predict(testX, batch_size=32, verbose=1)
    print "Printing 10 generated harmonies: "
    for i in 10:
        try:
            result = generated_harmonies[i]
            print "Result:  [",
            for row in result:
                print row.tolist().index(max(row)),
            print "]\nExpected: [",
            for act in testY[i]:
                print act.index(max(act)),
            print "]\n"
        except Exception as e:
            print "Error printing results", e
    result = model.evaluate(testX, testY)
    print "Overall loss on test set:", result
