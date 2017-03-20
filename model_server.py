import random
import os
import numpy
import json
import pickle
from flask import Flask, send_file, Response, request
from transformation.resample_harmony_melody import resample_melody

app = Flask(__name__)

CHORDS_LIST = 'supported_chords.json'
ROCK_CORPUS_MELODIES = 'rock-corpus/rs200_melody_nlt'

MODEL_PATHS = {
    'discrete_hmm_numerals':  'models/discrete_hmm.pkl',
    'discrete_hmm_numeric': 'models/discrete_numeric_hmm.pkl'
}

BEAT = 'beat'
MELODY = 'midi_note'

BEATS_PER_HARMONY_CHORD = 2

f = open(CHORDS_LIST, 'r')
chords = json.load(f)
f.close()

models = {}
for model_name in MODEL_PATHS:
    f = open(MODEL_PATHS[model_name], 'r')
    models[model_name] = pickle.load(f)
    f.close()


@app.route("/")
def index():
    return send_file('static/partials/index.html')


def midi_notes_to_relative(sequence, offset):
    # MIDI note 60 in key 7 should become 5. 60-7 = 53 -> 53 % 12 = 5.
    return [(s - offset) % 12 for s in sequence]


def generate_sequence(sequence):
    current = {
        'logprob': float("-inf"),
        'key': None,
        'sequence': None
    }

    for key in xrange(12):
        relative_sequence = midi_notes_to_relative(sequence, key)
        test = numpy.array([relative_sequence]).T
        logprob, states = model.decode(test, algorithm="viterbi")

        # If it's better than the last one
        if (logprob > current['logprob']):
            current['logprob'] = logprob
            current['key'] = key
            current['sequence'] = [chords[s] for s in states]

    return current


@app.route('/harmony/generate_from_notes', methods=['POST'])
def generate_from_notes():
    test_sequence = request.json['sequence']
    output = generate_sequence(test_sequence)
    return Response(json.dumps(output), status=200, mimetype='application/json')


@app.route('/harmony/generate_from_csv/<songname>', methods=['GET'])
def generate_from_csv(songname):
    filepath = os.path.join(ROCK_CORPUS_MELODIES, songname + '.nlt')
    resampled = resample_melody(filepath, BEAT, MELODY)

    # grab a melody note at each BEATS_PER_HARMONY_CHORD interval.
    input_sequence = []
    for index, sample in enumerate(resampled):
        if index % BEATS_PER_HARMONY_CHORD > 0:
            continue
        input_sequence.append(sample[MELODY])

    result = generate_sequence(input_sequence)
    result['start_beat'] = resampled[0][BEAT]
    result['beats_per_chord'] = BEATS_PER_HARMONY_CHORD
    return Response(json.dumps(result), status=200, mimetype='application/json')


@app.route('/harmony/generate_random/<songname>', methods=['GET'])
def generate_random(songname):
    filepath = os.path.join(ROCK_CORPUS_MELODIES, songname + '.nlt')
    resampled = resample_melody(filepath, BEAT, MELODY)

    # grab a melody note at each BEATS_PER_HARMONY_CHORD interval.
    sequence = []
    for index, sample in enumerate(resampled):
        if index % BEATS_PER_HARMONY_CHORD > 0:
            continue
        sequence.append(random.choice(chords))

    result = {}
    result['key'] = 0
    result['sequence'] = sequence
    result['start_beat'] = resampled[0][BEAT]
    result['beats_per_chord'] = BEATS_PER_HARMONY_CHORD
    return Response(json.dumps(result), status=200, mimetype='application/json')


@app.route('/melody/get_sequence/<songname>', methods=['GET'])
def get_melody_sequence(songname):
    filepath = os.path.join(ROCK_CORPUS_MELODIES, songname + '.nlt')
    rows = open(filepath, 'r').readlines()

    output = []
    for row in rows:
        new_el = {}
        data = row.split()
        new_el[BEAT] = data[1]
        new_el[MELODY] = data[2]
        output.append(new_el)

    return Response(json.dumps(output), status=200, mimetype='application/json')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
