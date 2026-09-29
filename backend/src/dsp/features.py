"""
DSP feature extraction.

Produces a fixed-length numeric feature vector used as ML classifier input,
PLUS a human-readable dict of the same quantities for the analysis report /
frontend "parameter table". Every value here is SOURCE=dsp_estimated (or
directly computed statistics of the samples, which we label
SOURCE=dsp_measured since they are exact functions of the data, not
estimates of an external physical quantity).
"""
from __future__ import annotations
import numpy as np
from scipy import stats
from src.dsp.psd import compute_psd
from src.dsp.bandwidth import estimate_occupied_bandwidth
from src.dsp.snr import estimate_snr
from src.dsp.symbol_rate import estimate_symbol_rate


FEATURE_NAMES = [
    "mean_i", "mean_q", "std_i", "std_q", "rms", "peak_amplitude", "crest_factor",
    "iq_correlation", "amplitude_variance", "phase_variance",
    "inst_freq_mean", "inst_freq_std",
    "spectral_centroid", "spectral_bandwidth", "spectral_flatness", "peak_psd_db",
    "occupied_bandwidth_hz",
    "kurtosis_amp", "skewness_amp", "kurtosis_iq", "papr_db",
    "zero_crossing_rate", "envelope_std_norm",
]


def _instantaneous_frequency(iq: np.ndarray, sample_rate_hz: float) -> np.ndarray:
    phase = np.unwrap(np.angle(iq))
    inst_freq = np.diff(phase) / (2 * np.pi) * sample_rate_hz
    return inst_freq


def extract_features(iq: np.ndarray, sample_rate_hz: float) -> dict:
    iq = iq.astype(np.complex128)
    amp = np.abs(iq)
    i, q = iq.real, iq.imag

    mean_i, mean_q = float(np.mean(i)), float(np.mean(q))
    std_i, std_q = float(np.std(i)), float(np.std(q))
    rms = float(np.sqrt(np.mean(amp ** 2)))
    peak_amplitude = float(np.max(amp))
    crest_factor = float(peak_amplitude / (rms + 1e-12))

    iq_correlation = float(np.corrcoef(i, q)[0, 1]) if len(i) > 1 else 0.0
    amplitude_variance = float(np.var(amp))
    phase = np.angle(iq)
    phase_variance = float(np.var(phase))

    inst_freq = _instantaneous_frequency(iq, sample_rate_hz)
    inst_freq_mean = float(np.mean(inst_freq)) if len(inst_freq) else 0.0
    inst_freq_std = float(np.std(inst_freq)) if len(inst_freq) else 0.0

    freqs, psd_db = compute_psd(iq, sample_rate_hz, nperseg=min(1024, len(iq)))
    psd_linear = 10 ** (psd_db / 10)
    psd_norm = psd_linear / (np.sum(psd_linear) + 1e-15)
    spectral_centroid = float(np.sum(freqs * psd_norm))
    spectral_bandwidth = float(np.sqrt(np.sum(((freqs - spectral_centroid) ** 2) * psd_norm)))
    geo_mean = np.exp(np.mean(np.log(psd_linear + 1e-15)))
    arith_mean = np.mean(psd_linear) + 1e-15
    spectral_flatness = float(geo_mean / arith_mean)
    peak_psd_db = float(np.max(psd_db))

    bw_info = estimate_occupied_bandwidth(iq, sample_rate_hz)
    occupied_bandwidth_hz = bw_info["bandwidth_hz"]

    kurtosis_amp = float(stats.kurtosis(amp))
    skewness_amp = float(stats.skew(amp))
    kurtosis_iq = float(stats.kurtosis(np.concatenate([i, q])))
    papr_db = float(10 * np.log10((peak_amplitude ** 2) / (rms ** 2 + 1e-12)))

    zero_crossings = np.sum(np.diff(np.sign(i)) != 0)
    zero_crossing_rate = float(zero_crossings / len(i))
    envelope_std_norm = float(np.std(amp) / (np.mean(amp) + 1e-12))

    feature_dict = {
        "mean_i": mean_i, "mean_q": mean_q, "std_i": std_i, "std_q": std_q,
        "rms": rms, "peak_amplitude": peak_amplitude, "crest_factor": crest_factor,
        "iq_correlation": iq_correlation, "amplitude_variance": amplitude_variance,
        "phase_variance": phase_variance,
        "inst_freq_mean": inst_freq_mean, "inst_freq_std": inst_freq_std,
        "spectral_centroid": spectral_centroid, "spectral_bandwidth": spectral_bandwidth,
        "spectral_flatness": spectral_flatness, "peak_psd_db": peak_psd_db,
        "occupied_bandwidth_hz": occupied_bandwidth_hz,
        "kurtosis_amp": kurtosis_amp, "skewness_amp": skewness_amp, "kurtosis_iq": kurtosis_iq,
        "papr_db": papr_db, "zero_crossing_rate": zero_crossing_rate,
        "envelope_std_norm": envelope_std_norm,
    }
    return feature_dict


def features_to_vector(feature_dict: dict) -> np.ndarray:
    return np.array([feature_dict[name] for name in FEATURE_NAMES], dtype=np.float64)


def extract_full_dsp_report(iq: np.ndarray, sample_rate_hz: float, modulation_hint: str | None = None) -> dict:
    """Everything the frontend 'parameter table' needs, all SOURCE=dsp_estimated
    unless noted otherwise."""
    from src.dsp.frequency_offset import estimate_carrier_offset

    features = extract_features(iq, sample_rate_hz)
    snr_info = estimate_snr(iq, sample_rate_hz)
    bw_info = estimate_occupied_bandwidth(iq, sample_rate_hz)
    symrate_info = estimate_symbol_rate(iq, sample_rate_hz)
    offset_info = estimate_carrier_offset(iq, sample_rate_hz, modulation_hint)

    return {
        "features": features,
        "snr": snr_info,
        "bandwidth": bw_info,
        "symbol_rate": symrate_info,
        "carrier_offset": offset_info,
    }
