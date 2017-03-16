import numpy
import json
import pickle
from flask import Flask, send_file, Response, request

app = Flask(__name__)

CHORDS_LIST = 'supported_chords.json'
MODEL_PATH = 'models/discrete_hmm.pkl'

f = open(CHORDS_LIST, 'r')
chords = json.load(f)
f.close()

f = open(MODEL_PATH, 'r')
model = pickle.load(f)
f.close()


@app.route("/")
def index():
    return send_file('static/partials/index.html')


def midi_notes_to_relative(sequence, offset):
    return [(s + offset) % 12 for s in sequence]


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
            current['sequence'] = [chords[s] for s in sequence]

    return current


@app.route('/harmony/generate', methods=['POST'])
def generate_harmony():
    test_sequence = request.json['sequence']
    output = generate_sequence(test_sequence)
    resp = Response(json.dumps(output), status=200, mimetype='application/json')
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
