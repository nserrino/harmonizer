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

		output = [float(data[0]), float(data[1]), data[2], int(data[3]), int(data[4]), int(data[5]), int(data[6])]
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
			new_record['relative_melody'] = melody[current_melody_index][3]

			if (current_melody_index < len(melody) - 1):
				current_melody_index += 1
			else:
				melody_done = True
		elif (next_harmony_beat < next_melody_beat):
			new_record = last_record
			new_record['beat'] = next_harmony_beat
			new_record['key'] = harmony[current_harmony_index][5]
			new_record['relative_harmony'] = harmony[current_harmony_index][3]

			if (current_harmony_index < len(harmony) - 1):
				current_harmony_index += 1
			else:
				harmony_done = True
		else:
			new_record = last_record
			new_record['beat'] = next_melody_beat
			new_record['key'] = harmony[current_harmony_index][5]
			new_record['relative_melody'] = melody[current_melody_index][3]
			new_record['relative_harmony'] = harmony[current_harmony_index][3]

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


if __name__ == "main":
	harmony = get_harmony_data(INPUT_HARMONY)
	melody = get_melody_data(INPUT_MELODY)

	f = open("output.json", 'w')
	result = merge_harmony_and_melody(harmony, melody)
	print result
	f.write(json.dumps(result))
	f.close()