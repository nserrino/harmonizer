import argparse
import os
import pickle
import random
from keras.layers import Input, LSTM, RepeatVector
from keras.models import Model, load_model
from keras.utils.np_utils import to_categorical
from transformation.rock_corpus_parser import MELODY_REL_PITCH, HARMONY_KEY_TONIC, HARMONY_REL_ROOT, HARMONY_ABS_ROOT
from transformation.resample_harmony_melody import resample_song, get_harmony_melody_pairs

def prepare_samples(resamples, synth, num_timesteps):
    X = []
    Y = []

    synth_resamples = []

    if (synth):
        for resample in resamples:
            for root in xrange(12):
                copy = resample.copy()
                copy[MELODY_REL_PITCH] = copy[MELODY_REL_PITCH].add(root).mod(12)
                copy[HARMONY_REL_ROOT] = copy[HARMONY_REL_ROOT].add(root).mod(12)
                synth_resamples.append(copy)

    resamples += synth_resamples

    chunked = []
    for i in xrange(len(resamples)):
        curent_resample = resamples[i]
        num_chunks = len(curent_resample) / num_timesteps
        for j in xrange(num_chunks):
            chunk = curent_resample[j:(j + num_timesteps)]
            chunked.append(chunk)
    random.shuffle(chunked)

    for i in xrange(len(chunked)):
        chunk = chunked[i]
        rel_mel = chunk[MELODY_REL_PITCH].get_values().tolist()
        rel_har = chunk[HARMONY_REL_ROOT].get_values().tolist()
        X.append(to_categorical(rel_mel, num_classes=12).tolist())
        Y.append(to_categorical(rel_har, num_classes=12).tolist())

    return X, Y


def train_model(num_timesteps, num_notes, X, Y):
    inputs = Input(shape=(num_timesteps, num_notes))
    outputs = LSTM(num_notes, return_sequences=True)(inputs)
    harmony_generator = Model(inputs, outputs)
    harmony_generator.summary()
    harmony_generator.compile(loss='mse', optimizer='adam')
    harmony_generator.fit(X, Y, batch_size=32, nb_epoch=100)
    return harmony_generator
