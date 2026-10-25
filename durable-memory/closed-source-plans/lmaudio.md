# Closed-source split dry-run: lmaudio

- Source repo: `/home/mma/repos/dsl/lmaudio`
- Source revision: `56b7a1952ac55e76ffa5b1ed3227e6986f891a33`
- Private peer target: `lmctlhq/lmaudio` (create/copy only after owner approval)
- Public peer target: `lmctl-ai/lmaudio` (preserve the existing public URL)

## Exact tracked-file plan

### Public peer (`lmctl-ai/lmaudio`): 71 tracked files
- `docs/audio/analog_drum_kit.wav`
- `docs/audio/biquad_filter_bank.wav`
- `docs/audio/chirp_spectrogram.wav`
- `docs/audio/compressor_transfer_curve.wav`
- `docs/audio/convolution_reverb_rt60.wav`
- `docs/audio/drum_machine_pattern.wav`
- `docs/audio/eq_before_after.wav`
- `docs/audio/fm_bell_spectrum.wav`
- `docs/audio/granular_texture.wav`
- `docs/audio/harmonic_morph_anim.wav`
- `docs/audio/karplus_strong_harp.wav`
- `docs/audio/karplus_strong_tuning.wav`
- `docs/audio/loudness_normalization_lufs.wav`
- `docs/audio/moog_ladder_sweep.wav`
- `docs/audio/polyblep_harmonics.wav`
- `docs/audio/reverb_and_wavefolder.wav`
- `docs/audio/reverb_impulse_response.wav`
- `docs/audio/sample_rate_conversion_quality.wav`
- `docs/audio/synth_lead_melody.wav`
- `docs/audio/synthesis_methods_compared.wav`
- `docs/audio/vocal_pitch_tracking.wav`
- `docs/audio/xylophone_bar_modes.wav`
- `docs/images/analog_drum_kit.png`
- `docs/images/biquad_filter_bank.png`
- `docs/images/chirp_spectrogram.png`
- `docs/images/compressor_transfer_curve.png`
- `docs/images/convolution_reverb_rt60.png`
- `docs/images/drum_machine_pattern.png`
- `docs/images/eq_before_after.png`
- `docs/images/fm_bell_spectrum.png`
- `docs/images/granular_texture.png`
- `docs/images/harmonic_morph_anim.gif`
- `docs/images/karplus_strong_harp.png`
- `docs/images/karplus_strong_tuning.png`
- `docs/images/loudness_normalization_lufs.png`
- `docs/images/moog_ladder_sweep.png`
- `docs/images/polyblep_harmonics.png`
- `docs/images/reverb_and_wavefolder.png`
- `docs/images/reverb_impulse_response.png`
- `docs/images/sample_rate_conversion_quality.png`
- `docs/images/synth_lead_melody.png`
- `docs/images/synthesis_methods_compared.png`
- `docs/images/vocal_pitch_tracking.png`
- `docs/images/xylophone_bar_modes.png`
- `examples/analog_drum_kit.lms`
- `examples/biquad_filter_bank.lms`
- `examples/chirp_spectrogram.lms`
- `examples/compressor_transfer_curve.lms`
- `examples/convolution_reverb_rt60.lms`
- `examples/drum_machine_pattern.lms`
- `examples/eq_before_after.lms`
- `examples/fm_bell_spectrum.lms`
- `examples/granular_texture.lms`
- `examples/harmonic_morph_anim.lms`
- `examples/karplus_strong_harp.lms`
- `examples/karplus_strong_tuning.lms`
- `examples/loudness_normalization_lufs.lms`
- `examples/moog_ladder_sweep.lms`
- `examples/polyblep_harmonics.lms`
- `examples/README.md`
- `examples/render-all.sh`
- `examples/reverb_and_wavefolder.lms`
- `examples/reverb_impulse_response.lms`
- `examples/sample_rate_conversion_quality.lms`
- `examples/synth_lead_melody.lms`
- `examples/synthesis_methods_compared.lms`
- `examples/vocal_pitch_tracking.lms`
- `examples/xylophone_bar_modes.lms`
- `LICENSE`
- `README.md`
- `THIRD_PARTY_NOTICES`
- `LICENSE-binaries` (new owner-approved binary license text; not present in this source checkout unless listed above)

### Private peer (`lmctlhq/lmaudio`): 43 tracked files
- ``
- `.gitattributes`
- `.github/workflows/ci.yml`
- `.gitignore`
- `CMakeLists.txt`
- `cpp/audio.cpp`
- `cpp/audio.hpp`
- `cpp/dslvm.hpp`
- `cpp/expr.hpp`
- `cpp/main.cpp`
- `cpp/memory_budget.cpp`
- `cpp/memory_budget.hpp`
- `cpp/std/lmcode-std.schema.json`
- `cpp/stdlib/collections.hpp`
- `cpp/stdlib/file.hpp`
- `cpp/stdlib/math.hpp`
- `cpp/stdlib/std.hpp`
- `cpp/stdlib/string.hpp`
- `cpp/stdlib/testing.hpp`
- `deps.lock`
- `durable-memory/01-purpose.md`
- `durable-memory/02-architecture.md`
- `durable-memory/03-api.md`
- `durable-memory/04-Visuals.md`
- `durable-memory/05-testing.md`
- `durable-memory/06-build-and-ci.md`
- `durable-memory/07-decisions.md`
- `durable-memory/08-limitations.md`
- `durable-memory/index.md`
- `schema/lmaudio.dsl.json`
- `scripts/gen-schema.py`
- `scripts/merge-std.py`
- `scripts/select-compiler.sh`
- `scripts/sync-deps.sh`
- `scripts/sync-sdk.sh`
- `sdk.lock`
- `test.sh`
- `tests/fft_and_parseval.lms`
- `tests/filters_and_biquad.lms`
- `tests/loudness_convolution_and_synthesis.lms`
- `tests/physical_effects_and_seq.lms`
- `tests/synthesis_and_pitch.lms`
- `tests/wav_and_editing.lms`

## Required path and release changes

- README-relative image/docs/example paths stay byte-for-byte at their current paths in the public peer.
- Raw autorun links checked: 23/23 map to public `.lms` files.
- Existing CI workflow paths move to the private peer; replace them with the private CI template and add public `.github/workflows/public-ci.yml`.
  - Private CI path: `.github/workflows/ci.yml`
- Expected public release assets: `lmaudio-linux-x64`, `lmaudio-linux-arm64`, `lmaudio-macos-x64`, `lmaudio-macos-arm64`, `lmaudio-windows-x64.exe`, plus `SHA256SUMS`.
- README links to private source paths checked: 1 finding(s).
  - SOURCE REFERENCE TO REVIEW: `README.md:353 -> ](schema/lmaudio.dsl.json)`
- Public-plan secret scan: 0 finding(s); values are never printed.
- Licensing: Ship LICENSE and full THIRD_PARTY_NOTICES. Preserve MIT notices for DaisySP, Soundpipe's selected modules, lmcode-cpp and the listed BSD-3-Clause KissFFT/MT19937 texts; do not include the excluded Csound/GPL Soundpipe modules.

## Verification result

- Autorun path check: PASS
- Public docs source-reference check: REVIEW REQUIRED
- Public-plan secret scan: PASS

This is a read-only plan. No files were copied or changed, no GitHub operation was performed, and no visibility was changed.
