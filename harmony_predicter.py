import argparse
import os
import pickle
import random
from keras.layers import Input, LSTM, RepeatVector
from keras.models import Model, load_model
from keras.utils.np_utils import to_categorical
from transformation.rock_corpus_parser import MELODY_REL_PITCH, HARMONY_KEY_TONIC, HARMONY_REL_ROOT, HARMONY_ABS_ROOT
from transformation.resample_harmony_melody import resample_song, get_harmony_melody_pairs

timesteps = 25
num_notes = 12

def prepare_training_test_sets():
    trainX = []
    trainY = []
    testX = []
    testY = []

    resamples_path = 'pkl/new_resamples_abs.pkl'

    try:
        f = open(resamples_path, 'r')
        resamples = pickle.load(f)
    except:
        harmony_root = 'rock-corpus/rs200_harmony_clt'
        melody_root = 'rock-corpus/rs200_melody_nlt'
        harmony_filenames = os.listdir(harmony_root)
        melody_filenames = os.listdir(melody_root)
        pairs = get_harmony_melody_pairs(harmony_filenames, melody_filenames)
        resamples = []

        for pair in pairs:
            try:
                resample = resample_song(os.path.join(harmony_root, pair['harmony']),
                                         os.path.join(melody_root, pair['melody']))
                resample["Melody relative pitch in C"] = resample[MELODY_REL_PITCH].mod(12)
                resamples.append(resample)
            except Exception as e:
                print "Encountered error on", pair['song'], ": Skipping."

        output = open('pkl/new_resamples.pkl', 'w')
        pickle.dump(resamples, output)
        output.close()

    shuffled_chunks_path = 'pkl/shuffled.pkl'

    try:
        f = open(shuffled_chunks_path, 'r')
        chunked = pickle.load(f)
    except:
        chunked = []
        for i in xrange(len(resamples)):
            curent_resample = resamples[i]
            num_chunks = len(curent_resample) / timesteps
            for j in xrange(num_chunks):
                chunk = curent_resample[j:(j + timesteps)]
                chunked.append(chunk)

        random.shuffle(chunked)
        shuffled = open(shuffled_chunks_path, 'w')
        pickle.dump(chunked, shuffled)

    for i in xrange(len(chunked)):
        chunk = chunked[i]
        rel_mel = chunk["Melody relative pitch in C"].get_values().tolist()
        rel_har = chunk[HARMONY_ABS_ROOT].get_values().tolist()
        if i % 100 < 80:
            trainX.append(to_categorical(rel_mel, num_classes=12).tolist())
            trainY.append(to_categorical(rel_har, num_classes=12).tolist())
        else:
            testX.append(to_categorical(rel_mel, num_classes=12).tolist())
            testY.append(to_categorical(rel_har, num_classes=12).tolist())

    return trainX, trainY, testX, testY

parser = argparse.ArgumentParser()
parser.add_argument("--model", help="Model path.", required=True)
parser.add_argument("--train", help="Train the model", action="store_true")
parser.add_argument("--eval", help="Evaluate the model", action="store_true")
args = parser.parse_args()


trainX, trainY, testX, testY = prepare_training_test_sets()

if args.train:
    inputs = Input(shape=(timesteps, num_notes))
    outputs = LSTM(num_notes, return_sequences=True)(inputs)
    harmony_generator = Model(inputs, outputs)
    harmony_generator.summary()
    harmony_generator.compile(loss='mse', optimizer='adam')
    harmony_generator.fit(trainX, trainY, batch_size=32, nb_epoch=100)
    harmony_generator.save(args.model)
else:
    harmony_generator = load_model(args.model)

if args.eval:
    generated_harmonies = harmony_generator.predict(testX, batch_size=32, verbose=1)
    for i in xrange(len(generated_harmonies)):
        try:
            result = generated_harmonies[i]
            print "Result:   ",
            for row in result:
                print row.tolist().index(max(row)),
            print "\nExpected: ",
            for act in testY[i]:
                print act.index(max(act)),
            print "\n\n\n"
        except Exception as e:
            print generated_harmonies[i]
            print e
