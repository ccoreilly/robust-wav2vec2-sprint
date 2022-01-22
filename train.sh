export CUDA_VISIBLE_DEVICES="0,1"

python train.py \
	--dataset_path="data/out" \
    --audio_column_name="wav_filename" \
    --text_column_name="transcript" \
	--model_name_or_path="facebook/wav2vec2-xls-r-1b" \
	--output_dir="./model_output" \
	--overwrite_output_dir \
	--evaluation_strategy="steps" \
	--length_column_name="input_length" \
	--gradient_checkpointing \
	--fp16 \
	--group_by_length \
	--num_train_epochs="10" \
	--per_device_train_batch_size="64" \
	--per_device_eval_batch_size="64" \
	--gradient_accumulation_steps="4" \
	--learning_rate="3e-4" \
	--warmup_steps="2000" \
	--save_steps="1000" \
	--eval_steps="5000" \
	--logging_steps="5000" \
	--layerdrop="0.0" \
	--activation_dropout="0.1" \
	--save_total_limit="3" \
	--freeze_feature_encoder \
	--feat_proj_dropout="0.0" \
	--mask_time_prob="0.75" \
	--mask_time_length="10" \
	--mask_feature_prob="0.25" \
	--mask_feature_length="64" \
	--do_train --do_eval &> train.log
