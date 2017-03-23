import json
from mido import MidiFile
from model_server import generate_sequence, generate_from_csv, get_melody_sequence, get_melody_seq, create_midi


def test_generate_sequence():
    output = generate_sequence([0, 7, 7, 9, 9, 7], 'discrete_hmm_chords')
    assert(output['logprob'] > -100)
    assert(output['logprob'] < 0)
    assert(output['key'] == 7)
    assert(output['sequence'][0] == 'IV')


def test_generate_from_csv():
    output = generate_from_csv('discrete_hmm_numeric', 'a_hard_days_night_tdc')
    assert(output.status_code == 200)
    result = json.loads(output.get_data())
    assert(result['key'] == 2)
    assert(result['beats_per_chord'] == 2)
    assert(result['start_beat'] == 1.0)
    assert(result['sequence'][0] == 0)


def test_get_melody_sequence():
    output = get_melody_sequence('a_hard_days_night_tdc')
    assert(output.status_code == 200)
    result = json.loads(output.get_data())
    assert(result[0]['beat'] == 0.62)
    assert(result[0]['midi_note'] == 60)
