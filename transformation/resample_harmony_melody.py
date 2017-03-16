import os
import pandas
import rock_corpus_parser

CLEAN = True

# Resamples harmony and melody files to be located on the same time axis.
# Expects input to be in the rock corpus format.


def get_harmony_melody_pairs(harmony_filenames, melody_filenames):
    harmony_songs = [f[:-len(rock_corpus_parser.HARMONY_EXT)] for f in harmony_filenames
                     if f.endswith(rock_corpus_parser.HARMONY_EXT)]
    melody_songs = [f[:-len(rock_corpus_parser.MELODY_EXT)] for f in melody_filenames
                    if f.endswith(rock_corpus_parser.MELODY_EXT)]
    pairs = []
    for song in set.intersection(set(harmony_songs), set(melody_songs)):
        s = {}
        s['song'] = song
        s['harmony'] = song + rock_corpus_parser.HARMONY_EXT
        s['melody'] = song + rock_corpus_parser.MELODY_EXT
        pairs.append(s)
    return pairs


def resample_song(harmony_path, melody_path):
    harmony = rock_corpus_parser.parse_harmony(harmony_path)
    melody = rock_corpus_parser.parse_melody(melody_path)

    if len(harmony) == 0 or len(melody) == 0:
        raise Exception("Harmony or melody has no entries")
        return

    output = pandas.concat([harmony, melody])
    output = output.sort(rock_corpus_parser.BEATS).fillna(method="ffill").dropna()

    int_columns = [rock_corpus_parser.HARMONY_KEY_TONIC, rock_corpus_parser.MELODY_ABS_PITCH,
                   rock_corpus_parser.MELODY_REL_PITCH]

    for col_name in int_columns:
        output[col_name] = output[col_name].astype(int)

    return output


def parse_and_write_song(harmony_path, melody_path, output_path, store_as_json):
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if os.path.exists(output_path):
        if CLEAN:
            os.remove(output_path)
        else:
            raise Exception("Output path exists: " + output_path)

    try:
        output = resample_song(harmony_path, melody_path)
    except:
        print "Skipping", output_path, "due to error during parsing/resampling"
        return

    if store_as_json:
        output.to_json(output_path, orient="records")
    else:
        output.to_csv(output_path, index=False)
