import sys
import io

csv_file = sys.argv[1]

sum_bytes = 0
with io.open(csv_file) as file:
    for line in file:
        data = line.split(',')
        if data[0] == "wav_filename":
            continue
        sum_bytes += int(data[1])
    
samples = sum_bytes * 8 / 16
duration_ms = samples / 16

duration_h = duration_ms / (1000*60*60)

print(duration_h)
