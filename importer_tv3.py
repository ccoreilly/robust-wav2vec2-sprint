#!/usr/bin/env python
"""
Use "python3 import_parlament.py -h" for help
"""
import csv
import os
import subprocess
import argparse
import re
from subprocess import run
from multiprocessing import Pool

import progressbar
import sox
from cvutils import Validator
from downloader import SIMPLE_BAR
from util import (
    get_counter,
    get_imported_samples,
    print_import_report,
)

FIELDNAMES = ["wav_filename", "wav_filesize", "transcript"]
SAMPLE_RATE = 16000
CHANNELS = 1
MAX_SECS = 19
PARAMS = None
FILTER_OBJ = None

def init_worker(params):
    global FILTER_OBJ  # pylint: disable=global-statement
    FILTER_OBJ = Validator('ca')


def one_sample(sample):
    """ Take an audio file, and optionally convert it to 16kHz WAV """
    wav_orig_filename = sample[0]
    output_filepath = os.path.join(sample[2], wav_orig_filename.split('/')[-1])
    wav_filename = os.path.splitext(output_filepath)[0] + ".wav"
    _maybe_convert_wav(wav_orig_filename, wav_filename)
    file_size = -1
    frames = 0
    if os.path.exists(wav_filename):
        file_size = os.path.getsize(wav_filename)
        frames = int(
            subprocess.check_output(
                ["soxi", "-s", wav_filename], stderr=subprocess.STDOUT
            )
        )
    label = FILTER_OBJ.validate(sample[1])
    rows = []
    counter = get_counter()
    if file_size == -1:
        # Excluding samples that failed upon conversion
        counter["failed"] += 1
    elif label is None:
        # Excluding samples that failed on label validation
        counter["invalid_label"] += 1
    elif int(frames / SAMPLE_RATE * 1000 / 10 / 2) < len(str(label)):
        # Excluding samples that are too short to fit the transcript
        counter["too_short"] += 1
    elif frames / SAMPLE_RATE > MAX_SECS:
        # Excluding very long samples to keep a reasonable batch-size
        counter["too_long"] += 1
    else:
        # This one is good - keep it for the target CSV
        rows.append((f"clips/{os.path.split(wav_filename)[-1]}", file_size, label, sample[2]))
        counter["imported_time"] += frames
    counter["all"] += 1
    counter["total_time"] += frames

    return (counter, rows)


def _maybe_convert_set(
    dataset,
    tsv_dir,
    audio_dir,
    output_dir,
    rows=None,
    exclude=None,
):
    exclude_transcripts = set()
    exclude_speakers = set()
    if exclude is not None:
        for sample in exclude:
            exclude_transcripts.add(sample[2])
            exclude_speakers.add(sample[3])

    if rows is None:
        rows = []
        transcription_file = os.path.join(os.path.abspath(tsv_dir), f"tv3_0.3_{dataset}.transcription")
        fileids_file = os.path.join(os.path.abspath(tsv_dir), f"tv3_0.3_{dataset}.fileids")

        print("Loading TSV file: ", transcription_file)
        # Get audiofile path and transcript for each sentence in tsv
        samples = []
        with open(transcription_file, encoding="utf-8") as transcription_file:
            with open(fileids_file, encoding="utf-8") as fileids_file:
                for transcription_line, fileid_line in zip(transcription_file, fileids_file):
                    sentence_match = re.match("<s> ([^<]+) <\/s", transcription_line)
                    if sentence_match:
                        samples.append(
                            (
                                os.path.join(audio_dir, fileid_line.strip()) + ".wav",
                                sentence_match[1],
                                os.path.join(output_dir, "clips"),
                            )
                        )

        counter = get_counter()
        num_samples = len(samples)

        print("Importing mp3 files...")
        pool = Pool(initializer=init_worker, initargs=(PARAMS,))
        bar = progressbar.ProgressBar(max_value=num_samples, widgets=SIMPLE_BAR)
        for i, processed in enumerate(
            pool.imap_unordered(one_sample, samples), start=1
        ):
            counter += processed[0]
            rows += processed[1]
            bar.update(i)
        bar.update(num_samples)
        pool.close()
        pool.join()

        imported_samples = get_imported_samples(counter)
        assert counter["all"] == num_samples
        assert len(rows) == imported_samples
        print_import_report(counter, SAMPLE_RATE, MAX_SECS)

    output_csv = os.path.join(os.path.abspath(output_dir), dataset + "_tv3.csv")
    print("Saving CSV file to: ", output_csv)
    with open(output_csv, "w", encoding="utf-8", newline="") as output_csv_file:
        writer = csv.DictWriter(output_csv_file, fieldnames=FIELDNAMES)
        writer.writeheader()
        bar = progressbar.ProgressBar(max_value=len(rows), widgets=SIMPLE_BAR)
        for filename, file_size, transcript, speaker in bar(rows):
            if transcript in exclude_transcripts or speaker in exclude_speakers:
                continue
            writer.writerow(
                {
                    "wav_filename": filename,
                    "wav_filesize": file_size,
                    "transcript": transcript,
                }
            )
    return rows


def _preprocess_data(tsv_dir, audio_dir, output_dir):
    exclude = []
    for dataset in ["train", "test"]:
        set_samples = _maybe_convert_set(
            dataset, tsv_dir, audio_dir, output_dir
        )


def _maybe_convert_wav(input_filename, output_filename):
    print(f"Converting {input_filename} to {output_filename}")
    if not os.path.exists(output_filename):
        run(['ffmpeg', '-y', '-i', input_filename, '-ac', '1', '-ar', '16000', '-f', 'wav', output_filename], capture_output=True)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Import data",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
    parser.add_argument("tsv_dir", help="Directory containing tsv files")
    parser.add_argument(
        "--audio_dir",
        help='Directory containing the audio clips - defaults to "<tsv_dir>/clips"',
    )
    parser.add_argument(
        "--output_dir",
        help='Where to store the results',
    )
    return parser.parse_args()


def main():
    audio_dir = (
        PARAMS.audio_dir if PARAMS.audio_dir else PARAMS.tsv_dir
    )
    _preprocess_data(PARAMS.tsv_dir, audio_dir, PARAMS.output_dir)


if __name__ == "__main__":
    PARAMS = parse_args()
    main()
