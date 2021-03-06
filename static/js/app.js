var tonal = require('tonal'),
    constants = require('./constants'),
    createMidi = require('./create-midi');

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

// Pass in beatOffset > 0 if we want to fast forward through the "blank" beginning of a song.
function playMelody(melody, secondsPerBeat, velocity, beatOffset, maxSeconds) {
    for (var i = 0; i < melody.length; ++i) {
        var letterKey = 'C',
            beat = melody[i].beat - beatOffset,
            melodyNote = melody[i].midi_note,
            nextBeat;

        if (i == melody.length - 1) {
            nextBeat = beat + 1;
        } else {
            nextBeat = melody[i + 1].beat - beatOffset;
        }

        if (maxSeconds != null && secondsPerBeat * nextBeat > maxSeconds) {
            break;
        }

        MIDI.noteOn(0, melodyNote, velocity, secondsPerBeat * beat);
        MIDI.noteOff(0, melodyNote, secondsPerBeat * nextBeat);
    }
}

function noteToNumeral(relNoteInt, keyInt) {
    var absNote = (relNoteInt + keyInt) % 12,
        letterNote = constants.TONIC_INT_TO_STRING[absNote],
        letterKey = constants.TONIC_INT_TO_STRING[keyInt],
        numeral = tonal.progression.abstract(letterNote, letterKey);
    return numeral[0];
}

function bucketRepeatedChords(sequence) {
    var output = [],
        lastChord;

    for (var i = 0; i < sequence.length; ++i) {
        var newChord = sequence[i];
        if (newChord !== lastChord) {
            output.push({
                numBeats: 1,
                chord: newChord
            })
        } else {
            output[output.length - 1].numBeats++;
        }
        lastChord = newChord;
    }

    return output;
}

// Pass in beatOffset > 0 if we want to fast forward through the "blank" beginning of a song.
function playHarmony(harmony, secondsPerBeat, harmonyOctave, velocity, beatOffset, maxSeconds) {
    beatOffset = beatOffset == null ? 0 : beatOffset;

    var letterKey = constants.TONIC_INT_TO_STRING[harmony['key']],
        currentBeat = harmony['start_beat'] - beatOffset,
        isNumeral = harmony['numeral'],
        bucketed = bucketRepeatedChords(harmony.sequence);

    for (var i = 0; i < bucketed.length; ++i) {
        var romanNumeral = isNumeral ? bucketed[i].chord :
            noteToNumeral(bucketed[i].chord, harmony['key']),
            duration = bucketed[i].numBeats;

        // Figure out the progression and then play the notes from that chord.
        var progression = tonal.progression.concrete(romanNumeral, letterKey),
            chord = tonal.chord.notes(progression[0]);

        if (maxSeconds != null && secondsPerBeat * (currentBeat + duration) > maxSeconds) {
            break;
        }

        for (var j = 0; j < chord.length; ++j) {
            // Make sure to increase the octave up if our root note of the chord is "above" the
            // accompanying notes.
            var octave = (j > 0 &&
                constants.TONIC_STRING_TO_INT[chord[0]] >
                constants.TONIC_STRING_TO_INT[chord[j]]) ?
                harmonyOctave + 1 : harmonyOctave,
                midiNote = tonal.midi.toMidi(chord[j] + octave);

            MIDI.noteOn(1, midiNote, velocity, secondsPerBeat * currentBeat);
            MIDI.noteOff(1, midiNote, secondsPerBeat * (currentBeat + duration));
        }
        currentBeat += duration;
    }
}

module.exports = {
    React: require('react'),
    ReactDOM: require('react-dom'),
    createMidi: createMidi.createMidi,
    createMidiBase64: createMidi.createMidiBase64,
    load: load,
    playMelody: playMelody,
    playHarmony: playHarmony
}
