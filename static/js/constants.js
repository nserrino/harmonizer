var TONIC_INT_TO_STRING = [
    'C',
    'Db',
    'D',
    'Eb',
    'E',
    'F',
    'Gb',
    'G',
    'Ab',
    'A',
    'Bb',
    'B'
];

var TONIC_STRING_TO_INT = {
    'C': 0,
    'Dbb': 0,
    'C#': 1,
    'Db': 1,
    'D': 2,
    'C##': 2,
    'Ebb': 2,
    'D#': 3,
    'Eb': 3,
    'E': 4,
    'F': 5,
    'E##': 5,
    'Gbb': 5,
    'F#': 6,
    'Gb': 6,
    'G': 7,
    'F##': 7,
    'Abb': 7,
    'G#': 8,
    'Ab': 8,
    'A': 9,
    'G##': 9,
    'Bbb': 9,
    'A#': 10,
    'Bb': 10,
    'B': 11
};

module.exports = {
    TONIC_INT_TO_STRING: TONIC_INT_TO_STRING,
    TONIC_STRING_TO_INT: TONIC_STRING_TO_INT
}
