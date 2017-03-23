var tonal = require('tonal'),
    constants = require('./constants');

// TODO: Move loading of MIDI module using require statement to this file.
function load(params, done) {
    MIDI.loadPlugin({
        soundfontUrl: params.soundfontUrl,
        instrument: params.instruments,
        onsuccess: function() {
            for (var channel in params.channels) {
                var instrument = params.channels[channel];
                MIDI.programChange(channel, MIDI.GM.byName[instrument].number);
            }
            return done();
        },
        onerror: done
    });
}

function playMelody(melody, secondsPerBeat) {
    for (var i = 0; i < melody.length; ++i) {
        var letterKey = 'C',
            beat = melody[i].beat,
            melodyNote = melody[i].midi_note,
            nextBeat;

        if (i == melody.length - 1) {
            nextBeat = beat + 1;
        } else {
            nextBeat = melody[i + 1].beat;
        }

        MIDI.noteOn(0, melodyNote, 100, secondsPerBeat * beat);
        MIDI.noteOff(0, melodyNote, secondsPerBeat * nextBeat);
    }
}

function playHarmony(harmony, secondsPerBeat, harmonyOctave) {
    var letterKey = constants.TONIC_INT_TO_STRING[harmony['key']],
        beatsPerChord = harmony['beats_per_chord'],
        currentBeat = harmony['start_beat'];

    for (var i = 0; i < harmony.sequence.length; ++i) {
        var romanNumeral = harmony.sequence[i],
            nextBeat = currentBeat + beatsPerChord;

        // Figure out the progression and then play the notes from that chord.
        var progression = tonal.progression.concrete(romanNumeral, letterKey),
            chord = tonal.chord.notes(progression[0]);

        for (var j = 0; j < chord.length; ++j) {
            // Make sure to increase the octave up if our root note of the chord is "above" the accompanying notes.
            var octave = (j > 0 &&
                constants.TONIC_STRING_TO_INT[chord[0]] >
                constants.TONIC_STRING_TO_INT[chord[j]]) ?
                harmonyOctave + 1 : harmonyOctave,
                midiNote = tonal.midi.toMidi(chord[j] + octave);

            MIDI.noteOn(1, midiNote, 30, secondsPerBeat * currentBeat);
            MIDI.noteOff(1, midiNote, secondsPerBeat * nextBeat);
        }

        currentBeat = nextBeat;
    }
}

module.exports = {
    createMidi: require('./create-midi'),
    load: load,
    playMelody: playMelody,
    playHarmony: playHarmony
}
