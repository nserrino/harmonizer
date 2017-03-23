import io
import json
import numpy
import os
import pickle
import random
from flask import Flask, send_file, Response, request
from mido import MetaMessage, Message, MidiFile, MidiTrack, bpm2tempo, second2tick
from transformation.resample_harmony_melody import resample_melody
from transformation.rock_corpus_parser import parse_melody, BEATS, MELODY_ABS_PITCH

app = Flask(__name__)

CHORDS_LIST = 'supported_chords.json'
ROCK_CORPUS_MELODIES = 'rock-corpus/rs200_melody_nlt'

MODEL_PATHS = {
    # Takes in relative melody notes, outputs roman numeral harmony chords
    # E.g. ["I", "IV", "I", "IV"]
    'discrete_hmm_chords':  'models/discrete_hmm_chords.pkl',
    # Takes in relative melody notes, outputs relative harmony notes
    # E.g. [0, 5, 0, 5]
    'discrete_hmm_numeric': 'models/discrete_hmm_numeric.pkl'
}

BEAT = 'beat'
MIDI_NOTE = 'midi_note'

BEATS_PER_SECOND = 2
BEATS_PER_MINUTE = 60 * BEATS_PER_SECOND
BEATS_PER_HARMONY_CHORD = 2
TICKS_PER_BEAT = 200
VELOCITY = 100

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


@app.route('/lol.mid')
def hello():
    return send_file('lol.mid')


@app.route('/test.mid')
def hello2():
    return send_file('test.mid')


def midi_notes_to_relative(sequence, offset):
    # MIDI note 60 in key 7 should become 5. 60-7 = 53 -> 53 % 12 = 5.
    return [(s - offset) % 12 for s in sequence]


def generate_sequence(sequence, model_type):
    if model_type not in models:
        raise Exception("Model " + model_type + " does not exist on server")
    model = models[model_type]

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
            if model_type == 'discrete_hmm_chords':
                current['sequence'] = [chords[s] for s in states]
            else:
                current['sequence'] = states.tolist()

    return current


def get_melody_seq(melody_filepath):
    melody = parse_melody(melody_filepath)
    output = []
    for i, row in melody.iterrows():
        new_el = {}
        new_el[BEAT] = row[BEATS]
        new_el[MIDI_NOTE] = int(row[MELODY_ABS_PITCH])
        output.append(new_el)
    return output


@app.route('/harmony/generate_from_notes/<modelname>', methods=['POST'])
def generate_from_notes(modelname):
    model_type = request.json['model_type']
    test_sequence = request.json['sequence']
    output = generate_sequence(test_sequence, model_type)
    return Response(json.dumps(output), status=200, mimetype='application/json')


@app.route('/harmony/generate_from_csv/<modelname>/<songname>', methods=['GET'])
def generate_from_csv(modelname, songname):
    filepath = os.path.join(ROCK_CORPUS_MELODIES, songname + '.nlt')
    resampled = resample_melody(filepath, BEAT, MIDI_NOTE)

    # grab a melody note at each BEATS_PER_HARMONY_CHORD interval.
    input_sequence = []
    for index, sample in enumerate(resampled):
        if index % BEATS_PER_HARMONY_CHORD > 0:
            continue
        input_sequence.append(sample[MIDI_NOTE])

    result = generate_sequence(input_sequence, modelname)
    result['start_beat'] = resampled[0][BEAT]
    result['beats_per_chord'] = BEATS_PER_HARMONY_CHORD
    return Response(json.dumps(result), status=200, mimetype='application/json')


@app.route('/harmony/generate_random/<songname>', methods=['GET'])
def generate_random(songname):
    filepath = os.path.join(ROCK_CORPUS_MELODIES, songname + '.nlt')
    resampled = resample_melody(filepath, BEAT, MIDI_NOTE)

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
    sequence = get_melody_seq(filepath)
    return Response(json.dumps(sequence), status=200, mimetype='application/json')


@app.route('/midi/harmonized/<modelname>/<songname>', methods=['GET'])
def get_harmonized_midi(modelname, songname):
    return


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
