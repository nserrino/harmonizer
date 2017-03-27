from transformation.rock_corpus_parser import HARMONY_REL_ROOT


def get_training_set_distribution(resamples):
    num_notes = 0
    distribution = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for sample in resamples:
        for index, row in sample.iterrows():
            root = row[HARMONY_REL_ROOT]
            distribution[root] += 1
            num_notes += 1

    return num_notes, distribution


def get_lstm_result_distribution(sequences):
    num_notes = 0
    distribution = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for sequence in sequences:
        for note_probs in sequence:
            predicted = note_probs.tolist().index(max(note_probs))
            distribution[predicted] += 1
            num_notes += 1

    return num_notes, distribution


def get_hmm_result_distribution(sequences):
    num_notes = 0
    distribution = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for sequence in sequences:
        for predicted in sequence:
            distribution[predicted] += 1
            num_notes += 1

    return num_notes, distribution
