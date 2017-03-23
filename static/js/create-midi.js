var Midi = require('jsmidgen'),
    TICKS_PER_BEAT = 128 / 2,
    MIDI_BASE64_HEADER = 'data:audio/midi;base64,';

/*
Input: sequence of the form
Output: Bytes of the output midi file
[{
    beat: 0,
    midi_note: 60
},{
    beat: 1,
    midi_note: 67
}..]
*/
function createMidi(sequence, beatsPerSecond, velocity) {
    var file = new Midi.File();
    var track = new Midi.Track();
    file.addTrack(track);
    track.setTempo(beatsPerSecond * 60, 0);

    for (var i = 0; i < sequence.length; ++i) {
        var midiPitch = sequence[i]['midi_note'],
            noteOnBeat = sequence[i]['beat'],
            noteOffBeat;
        if (i == sequence.length - 1) {
            noteOffBeat = sequence[i]['beat'] + 2;
        } else {
            noteOffBeat = sequence[i + 1]['beat'];
        }

        console.log('delta beat', noteOffBeat - noteOnBeat)
        track.addNoteOn(0, midiPitch, TICKS_PER_BEAT * noteOnBeat, velocity);
        track.addNoteOff(0, midiPitch, TICKS_PER_BEAT * noteOffBeat, velocity);
    }

    return file;
}

function createMidiBase64(sequence, beatsPerSecond, velocity) {
    var midi = createMidi(sequence, beatsPerSecond, velocity);
    return MIDI_BASE64_HEADER + btoa(midi.toBytes());
}

module.exports = {
    createMidi: createMidi,
    createMidiBase64: createMidiBase64
}
