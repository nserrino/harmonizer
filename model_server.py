import json
import numpy
import os
import pickle
import random
from flask import Flask, send_file, Response, request
from keras.models import load_model
from keras.utils.np_utils import to_categorical
from transformation.resample_harmony_melody import resample_melody
from transformation.rock_corpus_parser import parse_melody, BEATS, MELODY_ABS_PITCH
from transformation.rock_corpus_parser import parse_harmony, HARMONY_KEY_TONIC

app = Flask(__name__)

CHORDS_LIST = 'supported_chords.json'
ROCK_CORPUS_MELODIES = 'rock-corpus/rs200_melody_nlt'
ROCK_CORPUS_HARMONIES = 'rock-corpus/rs200_harmony_clt'
SONG_LIST = 'sample_song_names.json'

MODEL_PATHS = {
    # Takes in relative melody notes, outputs roman numeral harmony chords
    # E.g. ["I", "IV", "I", "IV"]
    'discrete_chords_hmm':  'models/discrete_chords_hmm.pkl',
    # Takes in relative melody notes, outputs relative harmony notes
    # E.g. [0, 5, 0, 5]
    'discrete_numeric_hmm': 'models/discrete_numeric_hmm.pkl',
    'discrete_numeric_lstm': 'models/lstm_20timestep_dedup_harmony_100epoch.h5' #'models/discrete_numeric_lstm.h5'
}

# Sequence length outputted by the endpoint, in beats.
SEQUENCE_LENGTH = 20

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

f = open(SONG_LIST, 'r')
songs = json.load(f)
f.close()

models = {}
for model_name in MODEL_PATHS:
    model_path = MODEL_PATHS[model_name]
    if model_path.endswith('.pkl'):
        f = open(MODEL_PATHS[model_name], 'r')
        models[model_name] = pickle.load(f)
        f.close()
    elif model_path.endswith('.h5'):
        models[model_name] = load_model(model_path)


@app.route("/")
def index():
    return send_file('static/partials/demo.html')


def midi_notes_to_relative(sequence, offset):
    # MIDI note 60 in key 7 should become 5. 60-7 = 53 -> 53 % 12 = 5.
    return [(s - offset) % 12 for s in sequence]


# Returns notes relative to the key predicted by the model.
def generate_hmm_sequence(sequence, model, is_roman_numeral):
    current = {
        'logprob': float("-inf"),
        'key': None,
        'sequence': None,
        'numeral': None
    }

    for key in xrange(12):
        relative_sequence = midi_notes_to_relative(sequence, key)
        test = numpy.array([relative_sequence]).T
        logprob, states = model.decode(test, algorithm="viterbi")

        # If it's better than the last one
        if (logprob > current['logprob']):
            current['logprob'] = logprob
            current['key'] = key
            if is_roman_numeral:
                current['sequence'] = [chords[s] for s in states]
                current['numeral'] = True
            else:
                current['sequence'] = states.tolist()
                current['numeral'] = False

    return current


# Returns notes relative to the input key, which is not predicted by this model.
def generate_lstm_sequence(sequence, model, key):
    if len(sequence) is not SEQUENCE_LENGTH:
        raise Exception('Current LSTM implementation requires input of length ' + SEQUENCE_LENGTH)

    result = {}
    result['numeral'] = False

    relative_sequence = midi_notes_to_relative(sequence, key)
    categorical = to_categorical(relative_sequence, num_classes=12)
    inputs = numpy.array([categorical.tolist()])
    generated = model.predict(inputs, batch_size=32, verbose=1)
    predicted_notes = []
    for note_probabilities in generated[0]:
        predicted = note_probabilities.tolist().index(max(note_probabilities))
        predicted_notes.append(predicted)

    result['sequence'] = predicted_notes
    return result


def generate_sequence(sequence, model_type, key=None):
    if model_type not in models:
        raise Exception("Model " + model_type + " does not exist on server")

    model = models[model_type]
    if model_type.endswith('hmm'):
        return generate_hmm_sequence(sequence, model, "chords" in model_type)
    elif model_type.endswith('lstm'):
        return generate_lstm_sequence(sequence, model, key)


def get_harmony_key(songname):
    harmony_filepath = os.path.join(ROCK_CORPUS_HARMONIES, songname + '.clt')
    harmony = parse_harmony(harmony_filepath)
    return harmony[HARMONY_KEY_TONIC][0]


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

    input_sequence = []
    for i in xrange(SEQUENCE_LENGTH):
        sample = resampled[i]
        input_sequence.append(sample[MIDI_NOTE])

    key = get_harmony_key(songname)
    # Pass the key in for LSTM models, which don't predict key
    result = generate_sequence(input_sequence, modelname, key)
    result['start_beat'] = resampled[0][BEAT]

    # Add in the key if we used a model that doesn't predict key.
    if 'key' not in result:
        result['key'] = key

    return Response(json.dumps(result), status=200, mimetype='application/json')


@app.route('/harmony/generate_random/<songname>', methods=['GET'])
def generate_random(songname):
    filepath = os.path.join(ROCK_CORPUS_MELODIES, songname + '.nlt')
    resampled = resample_melody(filepath, BEAT, MIDI_NOTE)

    sequence = []
    for i in xrange(SEQUENCE_LENGTH):
        sequence.append(random.choice(chords))

    result = {}
    result['key'] = 0
    result['sequence'] = sequence
    result['start_beat'] = resampled[0][BEAT]
    result['beats_per_chord'] = BEATS_PER_HARMONY_CHORD
    return Response(json.dumps(result), status=200, mimetype='application/json')


@app.route('/melody/get_sequence/<songname>', methods=['GET'])
def get_melody_sequence(songname):
    melody_filepath = os.path.join(ROCK_CORPUS_MELODIES, songname + '.nlt')
    melody = parse_melody(melody_filepath)
    melody_seq = []
    start_melody_beat = melody.get_value(0, BEATS)

    for i, row in melody.iterrows():
        if row[BEATS] > (start_melody_beat + SEQUENCE_LENGTH):
            break
        new_el = {}
        new_el[BEAT] = row[BEATS]
        new_el[MIDI_NOTE] = int(row[MELODY_ABS_PITCH])
        melody_seq.append(new_el)

    return Response(json.dumps(melody_seq), status=200, mimetype='application/json')


@app.route('/songs/get_song_list', methods=['GET'])
def get_song_list():
    return Response(json.dumps(songs), status=200, mimetype='application/json')


if __name__ == "__main__":
    # Keras with Tensorflow backend doesn't work unless debug is set to false...
    # See https://github.com/fchollet/keras/issues/2397 and
    # http://stackoverflow.com/questions/41991756/valueerror-tensor-is-not-an-element-of-this-graph
    app.run(host='0.0.0.0', debug=False)
