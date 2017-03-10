import argparse
import json
import os

INPUT_HARMONY = '/Users/natalieserrino/harmony/rock-corpus/rs200_harmony_clt/1999_tdc.clt'
INPUT_MELODY = '/Users/natalieserrino/harmony/rock-corpus/rs200_melody_nlt/1999_tdc.nlt'
OUPTUT_FILE = '/Users/natalieserrino/harmony/rock-corpus/1999_tdc.csv'

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--harmony", help="Path to harmony file(s)", required=True)
    parser.add_argument("--melody", help="Path to melody file(s)", required=True)
    parser.add_argument("--dest", help="Output destination", required=True)
    args = parser.parse_args()

    harmony = get_harmony_data(os.path.abspath(args.harmony))
    melody = get_melody_data(os.path.abspath(args.melody))

    f = open(os.path.abspath(args.dest), 'w')
    result = merge_harmony_and_melody(harmony, melody)
    f.write(json.dumps(result))
    f.close()
