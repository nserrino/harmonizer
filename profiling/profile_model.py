from transformation.rock_corpus_parser import HARMONY_REL_ROOT
from training.train_hmm import get_emission_matrix


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


def get_result_emission_matrix(input_resamples, output_harmonies):
    if len(input_resamples) != len(output_harmonies):
        raise Exception("Input resamples and output harmonies should be the same length.")

    remapped_resamples = []
    for i in xrange(len(input_resamples)):
        resample = input_resamples[i].copy()
        harmony = output_harmonies[i]

        for j in xrange(len(resample)):
            resample.set_value(j, HARMONY_REL_ROOT, harmony[j])
        remapped_resamples.append(resample)

    return get_emission_matrix(remapped_resamples)
