Raw .iq/.wav files are intentionally NOT shipped in this package (the full
demo dataset is ~1.9GB). Regenerate them locally in under a minute with:

    python src/dataset/generate_dataset.py --samples-per-condition 4 --n-symbols 1500

metadata.jsonl / metadata.csv (in ../metadata/) ARE included, and
features_cache.parquet (the DSP feature vectors used to train the shipped
model) is also included, so train_modulation.py / evaluate.py will work
immediately without regenerating raw IQ files at all -- only needed if you
want to inspect/replay the actual waveforms.
