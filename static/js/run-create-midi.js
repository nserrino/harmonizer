var createMidi = require('./create-midi').createMidi,
    minimist = require('minimist')
    request = require('request'),
    fs = require('fs');

var argv = minimist(process.argv.slice(2), {
    boolean: "verbose"
}),
    songName = argv.song_name,
    beatsPerSecond = parseFloat(argv.beats_per_second),
    outputFile = argv.output,
    endpoint = argv.endpoint;

// This midi sounds funky........
request(endpoint, function(err, response, body) {
    if (err) {
        console.log(err);
        return;
    }
    var sequence = JSON.parse(body),
        midi = createMidi(sequence);

    fs.writeFileSync(outputFile, midi.toBytes(), 'binary');
})

// Creates a midi file

