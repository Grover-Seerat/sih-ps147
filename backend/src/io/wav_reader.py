"""
WAV representation of IQ data.

DOCUMENTED FORMAT (read this before touching the code):
    - WAV sample rate  : same as the IQ sample rate (Hz), stored in the WAV header.
    - Channels         : 2 (stereo). Left channel = I, right channel = Q.
    - Sample width     : 32-bit IEEE float (WAVE_FORMAT_IEEE_FLOAT), range approx [-1, 1]
                          after the generator's power-normalization step.
    - Content          : This WAV stores raw I/Q, NOT demodulated audio. It is a
                          convenience container so IQ can be shared/played with tools
                          that expect .wav, and so the pipeline can accept a WAV upload
                          as an alternative to a raw .iq file.
    - Real audio WAVs  : are also produced separately as the OUTPUT of AM/FM
                          demodulation (mono, 16-bit PCM, audio sample rate) -- that is
                          a different kind of WAV file, produced by src/demod/am.py and
                          src/demod/fm.py, not by this module.

Conversion back to internal representation:
    universal_reader.py reads the two WAV channels, reconstructs
    `complex64 = left + 1j * right`.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
from scipy.io import wavfile


def write_iq_as_wav(iq: np.ndarray, sample_rate_hz: int, path: str | Path) -> None:
    stereo = np.empty((len(iq), 2), dtype=np.float32)
    stereo[:, 0] = iq.real.astype(np.float32)
    stereo[:, 1] = iq.imag.astype(np.float32)
    wavfile.write(str(path), int(sample_rate_hz), stereo)


def read_iq_from_wav(path: str | Path) -> tuple[np.ndarray, int]:
    """Returns (complex64 IQ array, sample_rate_hz) from a 2-channel IQ WAV."""
    sample_rate_hz, data = wavfile.read(str(path))
    if data.ndim == 1:
        raise ValueError(
            f"{path}: mono WAV has no Q channel -- cannot reconstruct IQ. "
            "This file is likely real demodulated audio, not an IQ capture."
        )
    data = data.astype(np.float32)
    # normalize integer PCM to [-1, 1] if needed
    if np.issubdtype(data.dtype, np.integer):
        data = data / np.iinfo(data.dtype).max
    iq = (data[:, 0] + 1j * data[:, 1]).astype(np.complex64)
    return iq, int(sample_rate_hz)


def write_audio_wav(audio: np.ndarray, sample_rate_hz: int, path: str | Path) -> None:
    """Write demodulated REAL audio (mono, 16-bit PCM) -- distinct from IQ WAVs above."""
    audio = np.asarray(audio, dtype=np.float64)
    peak = np.max(np.abs(audio)) or 1.0
    audio = audio / peak * 0.9
    pcm16 = (audio * 32767).astype(np.int16)
    wavfile.write(str(path), int(sample_rate_hz), pcm16)
