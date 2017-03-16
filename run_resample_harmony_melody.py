import argparse
import os
from transformation.resample_harmony_melody import get_harmony_melody_pairs, parse_and_write_song

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
    pairs = get_harmony_melody_pairs(os.listdir(harmony_path), os.listdir(melody_path))
    for pair in pairs:
        filename = pair['song'] + ".json" if args.json else pair['song'] + ".csv"
        output = os.path.join(dest_path, filename)
        parse_and_write_song(os.path.join(harmony_path, pair['harmony']),
                             os.path.join(melody_path, pair['melody']),
                             output, args.json)

    print "Wrote", len(pairs), "songs to", dest_path
else:
    parse_and_write_song(harmony_path, melody_path, dest_path, args.json)
