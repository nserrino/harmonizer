import argparse
import json
import os

CLEAN = True
MELODY_EXT = ".nlt"
HARMONY_EXT = ".clt"


def get_harmony_data(filepath):
    harmony_file = open(filepath, 'r')
    harmony_lines = harmony_file.readlines()
    output_data = []

    for line in harmony_lines:
        data = line.split()
        if data[2] == 'End':
            break

        output = [float(data[0]), float(data[1]), data[2], int(data[3]), int(data[4]),
                  int(data[5]), int(data[6])]
        output_data.append(output)

    return output_data


def get_melody_data(filepath):
    melody_file = open(filepath, 'r')
    melody_lines = melody_file.readlines()
    output_data = []
    for line in melody_lines:
        data = line.split()
        output = [float(data[0]), float(data[1]), int(data[2]), int(data[3])]
        output_data.append(output)
    return output_data


def extract_melody_to_record(new_record, melody, index):
    new_record['relative_melody'] = melody[index][3]


def extract_harmony_to_record(new_record, harmony, index):
    new_record['key'] = harmony[index][5]
    new_record['relative_harmony'] = harmony[index][3]


# The harmony files and the melody files each track their own lineage but we want
# to see how they change together. So we use this function to parse them both at once
# into a single output format.
def merge_harmony_and_melody(harmony, melody):
    harmony_done = False
    melody_done = False
    output_data = []
    current_harmony_index = 0
    current_melody_index = 0

    while not harmony_done and not melody_done:
        # Check if melody or harmony changes first
        next_harmony_beat = harmony[current_harmony_index][1]
        next_melody_beat = melody[current_melody_index][1]

        new_record = None
        last_record = None
        if len(output_data):
            last_record = output_data[-1].copy()
        else:
            last_record = {}
            last_record['relative_melody'] = None
            last_record['relative_harmony'] = None
            last_record['key'] = None

        # TODO: Remove repetitive boilerplate/cleanup
        if (next_melody_beat < next_harmony_beat):
            new_record = last_record
            new_record['beat'] = next_melody_beat
            extract_melody_to_record(new_record, melody, current_melody_index)

            if (current_melody_index < len(melody) - 1):
                current_melody_index += 1
            else:
                melody_done = True
        elif (next_harmony_beat < next_melody_beat):
            new_record = last_record
            new_record['beat'] = next_harmony_beat
            extract_harmony_to_record(new_record, harmony, current_harmony_index)

            if (current_harmony_index < len(harmony) - 1):
                current_harmony_index += 1
            else:
                harmony_done = True
        else:
            new_record = last_record
            new_record['beat'] = next_melody_beat
            extract_melody_to_record(new_record, melody, current_melody_index)
            extract_harmony_to_record(new_record, harmony, current_harmony_index)

            if (current_melody_index < len(melody) - 1):
                current_melody_index += 1
            else:
                melody_done = True

            if (current_harmony_index < len(harmony) - 1):
                current_harmony_index += 1
            else:
                harmony_done = True

        # print new_record
        output_data.append(new_record)
        # print output_data

    return output_data


def parse_and_write_song(harmony_path, melody_path, output_path):
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if os.path.exists(output_path):
        if CLEAN:
            os.remove(output_path)
        else:
            raise Exception("Output path exists: " + output_path)

    harmony = None
    melody = None

    try:
        harmony = get_harmony_data(harmony_path)
    except Exception as e:
        print "Failed to get harmony data for", harmony_path, e
        return

    try:
        melody = get_melody_data(melody_path)
    except Exception as e:
        print "Failed to get melody data for", melody_path, e
        return

    if len(harmony) == 0 or len(melody) == 0:
        print "Skipping", output_path
        return

    result = merge_harmony_and_melody(harmony, melody)
    f = open(output_path, 'w')
    f.write(json.dumps(result))
    f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--harmony", help="Path to harmony file(s)", required=True)
    parser.add_argument("--melody", help="Path to melody file(s)", required=True)
    parser.add_argument("--dest", help="Output destination", required=True)
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
            output = os.path.join(dest_path, song + ".json")
            parse_and_write_song(harmony, melody, output)

        print "Wrote", len(songs), "songs to", dest_path
    else:
        parse_and_write_song(harmony_path, melody_path, dest_path)
