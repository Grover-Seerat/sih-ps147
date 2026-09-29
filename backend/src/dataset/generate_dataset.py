"""
Generate the synthetic RF/IQ dataset.

Usage (from project root):
    python src/dataset/generate_dataset.py --samples-per-condition 20 --out dataset

This creates:
    dataset/raw/iq/sample_XXXXXX.iq        (complex64 raw binary)
    dataset/raw/wav/sample_XXXXXX.wav      (WAV representation, see wav_reader.py docstring)
    dataset/metadata/metadata.jsonl
    dataset/metadata/metadata.csv
"""
from __future__ import annotations
import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # project root

from src.dataset.metadata_schema import SignalMetadata, MODULATIONS, DIGITAL_MODULATIONS
from src.dataset.signal_generators import (
    generate_psk_qam, generate_fsk, generate_am, generate_fm, apply_channel_and_impairments,
)
from src.io.wav_reader import write_iq_as_wav

SAMPLE_RATES = [1_000_000, 2_000_000]
SYMBOL_RATES = [50_000, 100_000, 250_000]
SNRS = [0, 5, 10, 15, 20]
FREQ_OFFSETS = [-20_000, -5_000, 0, 5_000, 20_000]

# Held-out combinations for generalization testing (Section 11).
# Anything matching these goes to the TEST split; everything else -> TRAIN.
TEST_SNRS = {20}
TEST_FREQ_OFFSETS = {20_000, -20_000}


def make_split(snr_db: int, freq_offset: int) -> str:
    if snr_db in TEST_SNRS or freq_offset in TEST_FREQ_OFFSETS:
        return "test"
    return "train"


def generate_one(modulation: str, sample_rate_hz: int, symbol_rate_hz: int, snr_db: int,
                  freq_offset_hz: int, rng: np.random.Generator, n_symbols: int = 2000):
    phase_offset = float(rng.uniform(-np.pi, np.pi))
    timing_offset = float(rng.uniform(0, 1))
    channel = rng.choice(["AWGN", "AWGN", "AWGN", "rayleigh", "multipath"])  # mostly AWGN
    rolloff = float(rng.uniform(0.25, 0.5))

    if modulation in ("BPSK", "QPSK", "8PSK", "16QAM"):
        iq, info = generate_psk_qam(modulation, n_symbols, sample_rate_hz, symbol_rate_hz,
                                     phase_offset, timing_offset, rng, rolloff=rolloff)
        bandwidth_hz = info["symbol_rate_hz"] * (1 + rolloff)
    elif modulation == "FSK":
        iq, info = generate_fsk(n_symbols, sample_rate_hz, symbol_rate_hz, phase_offset, rng,
                                 mod_index=float(rng.uniform(0.4, 1.0)), gaussian=False)
        bandwidth_hz = 2 * (info["freq_deviation_hz"] + info["symbol_rate_hz"])
    elif modulation == "GFSK":
        iq, info = generate_fsk(n_symbols, sample_rate_hz, symbol_rate_hz, phase_offset, rng,
                                 mod_index=float(rng.uniform(0.4, 0.8)), gaussian=True, bt=0.5)
        bandwidth_hz = 2 * (info["freq_deviation_hz"] + info["symbol_rate_hz"])
    elif modulation == "AM":
        duration = n_symbols / symbol_rate_hz
        audio_freq = float(rng.uniform(1000, 4000))
        iq, info = generate_am(duration, sample_rate_hz, audio_freq, mod_index=float(rng.uniform(0.4, 0.9)), rng=rng)
        bandwidth_hz = 2 * audio_freq * 2.3
    elif modulation == "FM":
        duration = n_symbols / symbol_rate_hz
        audio_freq = float(rng.uniform(300, 3000))
        freq_dev = float(rng.uniform(5000, 15000))
        iq, info = generate_fm(duration, sample_rate_hz, audio_freq, freq_dev, rng=rng)
        bandwidth_hz = 2 * (freq_dev + audio_freq * 1.7)
    else:
        raise ValueError(modulation)

    iq = apply_channel_and_impairments(iq, sample_rate_hz, snr_db, freq_offset_hz, phase_offset, channel, rng)
    iq = iq.astype(np.complex64)

    meta_extra = dict(info)
    meta_extra.update({"channel": channel, "phase_offset_rad": phase_offset, "timing_offset": timing_offset,
                        "bandwidth_hz": float(bandwidth_hz)})
    return iq, meta_extra


def main():
    ap = argparse.ArgumentParser(description="Generate synthetic RF signal dataset")
    ap.add_argument("--samples-per-condition", type=int, default=3,
                     help="Randomized examples per (modulation, snr, symbol_rate, freq_offset) combo")
    ap.add_argument("--out", type=str, default="dataset", help="Output dataset directory")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n-symbols", type=int, default=2000, help="Symbols (or symbol-equivalents) per example")
    ap.add_argument("--write-wav", action="store_true", default=True)
    args = ap.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    out_dir = project_root / args.out
    iq_dir = out_dir / "raw" / "iq"
    wav_dir = out_dir / "raw" / "wav"
    meta_dir = out_dir / "metadata"
    for d in (iq_dir, wav_dir, meta_dir):
        d.mkdir(parents=True, exist_ok=True)

    rng_master = np.random.default_rng(args.seed)

    records: list[dict] = []
    idx = 0
    combos = [
        (mod, sr, symr, snr, fo)
        for mod in MODULATIONS
        for sr in SAMPLE_RATES
        for symr in SYMBOL_RATES
        for snr in SNRS
        for fo in FREQ_OFFSETS
    ]
    total = len(combos) * args.samples_per_condition
    print(f"Generating {total} examples ({len(combos)} conditions x {args.samples_per_condition})...")

    for mod, sample_rate_hz, symbol_rate_hz, snr_db, freq_offset_hz in combos:
        for _ in range(args.samples_per_condition):
            idx += 1
            seed = rng_master.integers(0, 2**31 - 1)
            rng = np.random.default_rng(seed)
            iq, extra = generate_one(mod, sample_rate_hz, symbol_rate_hz, snr_db, freq_offset_hz, rng,
                                      n_symbols=args.n_symbols)
            sample_id = f"sample_{idx:06d}"
            iq_path = iq_dir / f"{sample_id}.iq"
            iq.tofile(iq_path)

            wav_rel = None
            if args.write_wav:
                wav_path = wav_dir / f"{sample_id}.wav"
                write_iq_as_wav(iq, sample_rate_hz, wav_path)
                wav_rel = str(wav_path.relative_to(out_dir))

            meta = SignalMetadata(
                sample_id=sample_id,
                file=str(iq_path.relative_to(out_dir)),
                format="complex64",
                modulation=mod,
                sample_rate_hz=float(sample_rate_hz),
                symbol_rate_hz=extra.get("symbol_rate_hz"),
                snr_db=float(snr_db),
                carrier_frequency_hz=0.0,
                carrier_offset_hz=float(freq_offset_hz),
                bandwidth_hz=float(extra.get("bandwidth_hz", 0.0)),
                num_samples=len(iq),
                duration_seconds=len(iq) / sample_rate_hz,
                pulse_shape=extra.get("pulse_shape", "none"),
                rolloff=extra.get("rolloff"),
                channel=extra.get("channel", "AWGN"),
                phase_offset_rad=extra.get("phase_offset_rad", 0.0),
                timing_offset=extra.get("timing_offset", 0.0),
                fec="none",
                interleaving="none",
                split=make_split(snr_db, freq_offset_hz),
            )
            d = meta.to_dict()
            d["wav_file"] = wav_rel
            records.append(d)

            if idx % 200 == 0:
                print(f"  {idx}/{total}")

    jsonl_path = meta_dir / "metadata.jsonl"
    with open(jsonl_path, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    csv_path = meta_dir / "metadata.csv"
    fieldnames = list(records[0].keys())
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Done. {len(records)} examples written to {out_dir}")
    print(f"Metadata: {jsonl_path}, {csv_path}")


if __name__ == "__main__":
    main()
