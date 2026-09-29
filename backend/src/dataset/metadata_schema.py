"""
Metadata schema for the RF signal dataset.

Every field is tagged with a SOURCE so downstream code (and the frontend)
never pretends to know something it didn't actually measure.

SOURCE values:
    "ground_truth"   -> known exactly because WE generated the signal
    "file_metadata"  -> read directly from a file header / sidecar file
    "dsp_estimated"  -> computed by a DSP algorithm from the samples
    "ml_predicted"   -> output of a trained ML classifier
    "inferred"       -> derived indirectly (e.g. from file metadata + assumptions)
    "unknown"        -> not determinable with current data/algorithms

For SYNTHETIC data every physical parameter is ground truth, because we
literally generated the waveform. For REAL captures (Section 19 of the
brief) most of these fields will instead be "unknown" or "dsp_estimated"
-- the schema below is written so that transition requires no code changes,
only different values.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional

SCHEMA_FIELD_DOCS = {
    "sample_id": "Unique id for this recording.",
    "file": "Relative path to the IQ (or WAV) file.",
    "format": "Storage format: 'complex64' (raw IQ) or 'wav'.",
    "modulation": "Ground-truth modulation label (synthetic only). SOURCE=ground_truth.",
    "sample_rate_hz": "Sample rate the IQ was generated/recorded at. SOURCE=ground_truth for synthetic, file_metadata/unknown for real captures.",
    "symbol_rate_hz": "Symbol (baud) rate for digital modulations. None for AM/FM. SOURCE=ground_truth.",
    "snr_db": "AWGN SNR injected at generation time. SOURCE=ground_truth.",
    "carrier_frequency_hz": "Baseband center frequency the signal was placed at (0 = centered).",
    "carrier_offset_hz": "Deliberate carrier/frequency offset injected. SOURCE=ground_truth.",
    "bandwidth_hz": "Approximate occupied bandwidth used at generation time (nominal, not measured).",
    "num_samples": "Number of complex samples in the file.",
    "duration_seconds": "num_samples / sample_rate_hz.",
    "pulse_shape": "Pulse shaping filter used for digital signals ('RRC', 'gaussian', 'none').",
    "rolloff": "Roll-off factor of the RRC filter, if used.",
    "channel": "Channel model applied: 'AWGN', 'rayleigh', 'multipath'.",
    "phase_offset_rad": "Random constant phase offset injected. SOURCE=ground_truth.",
    "timing_offset": "Fractional-symbol timing offset injected (0-1). SOURCE=ground_truth.",
    "fec": "Forward error correction scheme. 'none' for this prototype (see Section 17). SOURCE=ground_truth (we control it).",
    "interleaving": "Interleaving scheme. 'none' for this prototype. SOURCE=ground_truth.",
    "split": "Which evaluation split this example belongs to: 'train' or 'test'. See Section 11 of the design doc for the held-out strategy.",
}


@dataclass
class SignalMetadata:
    sample_id: str
    file: str
    format: str
    modulation: str
    sample_rate_hz: float
    symbol_rate_hz: Optional[float]
    snr_db: float
    carrier_frequency_hz: float
    carrier_offset_hz: float
    bandwidth_hz: float
    num_samples: int
    duration_seconds: float
    pulse_shape: str
    rolloff: Optional[float]
    channel: str
    phase_offset_rad: float
    timing_offset: float
    fec: str = "none"
    interleaving: str = "none"
    split: str = "train"

    def to_dict(self) -> dict:
        return asdict(self)


MODULATIONS = ["BPSK", "QPSK", "8PSK", "16QAM", "FSK", "GFSK", "AM", "FM"]
DIGITAL_MODULATIONS = {"BPSK", "QPSK", "8PSK", "16QAM", "FSK", "GFSK"}
ANALOG_MODULATIONS = {"AM", "FM"}

FEC_TYPES = ["none", "convolutional", "BCH", "reed_solomon", "LDPC", "unknown"]
INTERLEAVING_TYPES = ["none", "block", "convolutional", "random", "unknown"]
