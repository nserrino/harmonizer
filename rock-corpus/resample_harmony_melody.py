import argparse
import os
import pandas


CLEAN = True
MELODY_EXT = ".nlt"
HARMONY_EXT = ".clt"


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
        harmony = pandas.read_csv(harmony_path, header=None, delimiter=r"\s+")
        melody = pandas.read_csv(melody_path, header=None, delimiter=r"\s+")
    except:
        print "Encountered error reading song for", output_path
        return

    harmony.dropna()
    melody.dropna()
    harmony.columns = ['Seconds', 'Beats', 'Harmony Roman Numeral',
                       'Harmony chromatic key-relative root', 'Harmony diatonic root',
                       'Harmony key tonic', 'Harmony absolute root']
    melody.columns = ['Seconds', 'Beats', 'Melody absolute pitch', 'Melody key-relative pitch']
    del harmony['Seconds']
    del melody['Seconds']

    if len(harmony) == 0 or len(melody) == 0:
        print "Skipping", output_path
        return

    output = pandas.concat([harmony, melody])
    output = output.sort("Beats").fillna(method="ffill").dropna()

    int_columns = ['Harmony chromatic key-relative root', 'Harmony diatonic root',
                   'Harmony key tonic', 'Harmony absolute root', 'Melody absolute pitch',
                   'Melody key-relative pitch']

    for col_name in int_columns:
        output[col_name] = output[col_name].astype(int)

    if store_as_json:
        output.to_json(output_path, orient="records")
    else:
        output.to_csv(output_path, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--harmony", help="Path to harmony file(s)", required=True)
    parser.add_argument("--melody", help="Path to melody file(s)", required=True)
    parser.add_argument("--dest", help="Output destination", required=True)
    parser.add_argument("--json", help="Store as JSON", action="store_true")
    args = parser.parse_args()
    harmony_path = os.path.abspath(args.harmony)
    melody_path = os.path.abspath(args.melody)
    dest_path = os.path.abspath(args.dest)

    if os.path.isdir(harmony_path) and os.path.isdir(melody_path):
        # cut off extension
        harmony_songs = [f[:-4] for f in os.listdir(harmony_path) if f.endswith(HARMONY_EXT)]
        melody_songs = [f[:-4] for f in os.listdir(melody_path) if f.endswith(MELODY_EXT)]
        songs = set.intersection(set(harmony_songs), set(melody_songs))

        for song in songs:
            harmony = os.path.join(harmony_path, song + HARMONY_EXT)
            melody = os.path.join(melody_path, song + MELODY_EXT)
            filename = song + ".json" if args.json else song + ".csv"
            output = os.path.join(dest_path, filename)
            parse_and_write_song(harmony, melody, output, args.json)

        print "Wrote", len(songs), "songs to", dest_path
    else:
        parse_and_write_song(harmony_path, melody_path, dest_path, args.json)
