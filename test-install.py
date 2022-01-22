from transformers import AutoModelForCTC, AutoProcessor
from datasets import load_dataset

dummy_dataset = load_dataset("common_voice", "ab", split="test")

model = AutoModelForCTC.from_pretrained("hf-internal-testing/tiny-random-wav2vec2")
model.to("cuda")

processor = AutoProcessor.from_pretrained("hf-internal-testing/tiny-random-wav2vec2")

input_values = processor(dummy_dataset[0]["audio"]["array"], return_tensors="pt", sampling_rate=16_000).input_values
input_values = input_values.to("cuda")

logits = model(input_values).logits

assert logits.shape[-1] == 32