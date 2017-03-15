var _ = require('lodash'),
    constants = require('./constants'),
    tonal = require('tonal'),
    minimist = require('minimist'),
    fs = require('fs');

var argv = minimist(process.argv.slice(2), {
    boolean: "verbose"
}),
    inputFile = argv.input,
    outputFile = argv.output;

// Parses the chords from an input file similar to ../chord_counts.csv into a
// list of supported/unsupported chords. If verbose is not set, simply write out
// the list of supported chords as a json file to the destination.

function getChordCounts(input) {
    var chordData = fs.readFileSync(input).toString();
    // Drop the header
    return _.map(chordData.split('\n').slice(1), function(row) {
        var parsed = row.split(',');
        return {
            chord: parsed[0],
            count: parseInt(parsed[1])
        }
    });
}

function chordToNotes(chord) {
    var rootInC = tonal.progression.concrete(chord, 'C');
    if (rootInC[0] == null) {
        return null;
    }
    var notes = tonal.chord.notes(rootInC);
    if (!notes.length) {
        return null;
    }
    return notes;
}

function allNotesSupported(notes) {
    for (var i = 0; i < notes.length; ++i) {
        if (constants.TONIC_STRING_TO_INT[notes[i]] == null) {
            return false;
        }
    }
    return true;
}

var chordCounts = getChordCounts(inputFile),
    outputs = {
        unsupported: [],
        supported: []
    };

_.each(chordCounts, function(chordCount) {
    var output = _.clone(chordCount);

    if (output.count < 10) {
        outputs.unsupported.push(output);
        return;
    }

    var notes = chordToNotes(chordCount.chord);

    if (notes == null) {
        outputs.unsupported.push(output);
        return;
    }

    output.notes = notes;
    if (!allNotesSupported(notes)) {
        outputs.unsupported.push(output);
    } else {
        outputs.supported.push(output);
    }
});

if (argv.verbose) {
    fs.writeFileSync(outputFile, JSON.stringify(outputs, null, 4));
} else {
    fs.writeFileSync(outputFile, JSON.stringify(_.map(outputs.supported, function(sup) {
        return sup.chord;
    }), null, 4));
}
