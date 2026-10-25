# Compositions 34-42 (part 2): hosts and pins

Pinned host releases (latest published tags when written): lmimg v0.1.3, lmfinance v0.1.3,
lmhtml v0.7.3, lmssl v0.1.0, lmmagnum v0.2.11, lmaudio v0.2.1, lmbio v0.1.3, lmweather v0.1.3,
lmcell v0.1.3, lmvideo v0.1.28 (v0.1.25 for the older compositions), lmoffice v0.1.9 (v0.1.8 where
noted), lmplot v0.2.1. lmproxy has no published release, so it has no composition.

Host limits found while writing them:
- lmvideo and lmoffice cannot read files. Data reaches them only as `${...}` scalars that lmscript
  read back from the host output lines (`split(r.stdout, "\n")`). Keep series short (12 points) or
  reduce them to scalars.
- An lmscript `${...}` of a whole-number float is an integer literal. Add a tiny offset (1e-9) when
  the value must be a float in the DSL, e.g. for `Series.add`.
- lmimg image operations work in place and return the same image. Copy the input before each step
  (`img.copy().levels(...)`), otherwise the original picture changes too. The vignette step pushed
  SSIM to near zero, so the pipeline keeps levels, unsharp and curves only.
- lmbio `simulate` returns the full run; values come from `Result.value(name, row)`, `max`, `final`.
- lmcell `Result.counts()` is a time-by-live-count matrix (201 rows, 2 columns); `history()` is per
  event and far too long to sample.
- lmweather: the energy of a pulse changes by about 1e-8 over two hours with linear drag up to
  0.01, so an energy-decay figure is flat. The gravity-wave crest speed (sqrt(gH)) is the usable
  known answer. A Gaussian of sigma 283 km overlaps its own halves at 2000 s; sigma 50 km separates
  them.
- lmssl: fixed test certificates are inlined as PEM text (no key material). `valid_days`, `expired`
  depend on the clock and are not used, so the output is deterministic.
- lmhtml: the gallery check rejects any `../` in a script, so the fixture uses root-relative links.
- lmfinance: `pricing.price(...).price()` gives the Black-Scholes value; the at-the-money call with
  S = K = 100, r = 5 %, sigma = 20 %, T = 1 is 10.4506.

Blocked or skipped:
- lmcloud needs an OpenTofu (`tofu`) executable; this machine has only `terraform`.
- lmssh needs a reachable sshd; CI runners have none, so no fleet report was added.
- lmproxy has no published release; lmfilament was not added (lmmagnum covers the 3D product render).
- lmmolecule was not added in this batch.
