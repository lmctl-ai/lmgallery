# Cross-host compositions

Every command runs from an empty directory and writes the listed image. Each computation is passed to a separate rendering host through generated data.

| | |
| :---: | :---: |
| <a href="#damped-oscillator-dashboard"><img src="../docs/images/showcase-01-oscillator.png" width="400" alt="Damped oscillator dashboard"></a><br>Damped oscillator dashboard | <a href="#discounted-project-cashflows"><img src="../docs/images/showcase-02-finance-cashflows.png" width="400" alt="Discounted project cashflows"></a><br>Discounted project cashflows |
| <a href="#shallow-water-gravity-pulse"><img src="../docs/images/showcase-03-weather-pulse.png" width="400" alt="Shallow-water gravity pulse"></a><br>Shallow-water gravity pulse | <a href="#hohmann-transfer-equal-time-markers"><img src="../docs/images/showcase-04-space-orbit-cad.png" width="400" alt="Hohmann transfer: equal-time markers"></a><br>Hohmann transfer: equal-time markers |
| <a href="#cargo-ramp-force-balance"><img src="../docs/images/showcase-05-physics-free-body.png" width="400" alt="Cargo-ramp force balance"></a><br>Cargo-ramp force balance | <a href="#finite-element-poisson-field"><img src="../docs/images/showcase-06-fluid-poisson-plot.png" width="400" alt="Finite-element Poisson field"></a><br>Finite-element Poisson field |
| <a href="#michaelis-menten-from-mechanism"><img src="../docs/images/showcase-07-enzyme-response.png" width="400" alt="Michaelis-Menten from mechanism"></a><br>Michaelis-Menten from mechanism | <a href="#cell-growth-and-motility"><img src="../docs/images/showcase-08-cell-pattern.png" width="400" alt="Cell growth and motility"></a><br>Cell growth and motility |
| <a href="#photon-attenuation-and-build-up-in-water"><img src="../docs/images/showcase-09-photon-transport.png" width="400" alt="Photon attenuation and build-up in water"></a><br>Photon attenuation and build-up in water | <a href="#water-dimer-hydrogen-bond-in-3d"><img src="../docs/images/showcase-10-molecule-dimer-cad.png" width="400" alt="Water dimer: hydrogen bond in 3D"></a><br>Water dimer: hydrogen bond in 3D |
| <a href="#shielding-by-mass-lead-aluminum-water"><img src="../docs/images/showcase-11-particle-shield-layout.png" width="400" alt="Shielding by mass: lead, aluminum, water"></a><br>Shielding by mass: lead, aluminum, water | <a href="#geostrophic-adjustment-animated"><img src="../docs/images/showcase-12-weather-adjustment.gif" width="400" alt="Geostrophic adjustment, animated"></a><br>Geostrophic adjustment, animated |
| <a href="#dosing-regimen-inside-a-therapeutic-window"><img src="../docs/images/showcase-13-bio-dosing-regimen.png" width="400" alt="Dosing regimen inside a therapeutic window"></a><br>Dosing regimen inside a therapeutic window | <a href="#damping-ratio-sweep-as-a-contact-sheet"><img src="../docs/images/showcase-14-num-sweep-contact-sheet.png" width="400" alt="Damping-ratio sweep as a contact sheet"></a><br>Damping-ratio sweep as a contact sheet |
| <a href="#equalizer-designed-versus-measured"><img src="../docs/images/showcase-15-audio-eq-measurement.png" width="400" alt="Equalizer: designed versus measured"></a><br>Equalizer: designed versus measured | <a href="#kepler-orbit-energy-check"><img src="../docs/images/showcase-16-kepler-conservation.png" width="400" alt="Kepler orbit energy check"></a><br>Kepler orbit energy check |
| <a href="#driven-oscillator-transient-to-steady-state"><img src="../docs/images/showcase-17-oscillator-driven.png" width="400" alt="Driven oscillator: transient to steady state"></a><br>Driven oscillator: transient to steady state | <a href="#intermediate-axis-tumble-of-a-free-plate"><img src="../docs/images/showcase-18-rigid-body-intermediate-axis.png" width="400" alt="Intermediate-axis tumble of a free plate"></a><br>Intermediate-axis tumble of a free plate |
| <a href="#finite-element-error-against-a-known-answer"><img src="../docs/images/showcase-19-fem-poisson-error.png" width="400" alt="Finite-element error against a known answer"></a><br>Finite-element error against a known answer | <a href="#heat-conduction-in-x-and-t"><img src="../docs/images/showcase-20-heat-spacetime.png" width="400" alt="Heat conduction in x and t"></a><br>Heat conduction in x and t |
| <a href="#forecast-with-a-95-%-prediction-band"><img src="../docs/images/showcase-21-forecast-band.png" width="400" alt="Forecast with a 95 % prediction band"></a><br>Forecast with a 95 % prediction band | <a href="#seasonal-decomposition-by-least-squares"><img src="../docs/images/showcase-22-seasonal-decomposition.png" width="400" alt="Seasonal decomposition by least squares"></a><br>Seasonal decomposition by least squares |
| <a href="#regression-diagnostics-predicted-actual-and-residuals"><img src="../docs/images/showcase-23-regression-residuals.png" width="400" alt="Regression diagnostics: predicted, actual and residuals"></a><br>Regression diagnostics: predicted, actual and residuals | <a href="#daily-sign-ups-on-a-date-axis"><img src="../docs/images/showcase-24-signups-date-axis.png" width="400" alt="Daily sign-ups on a date axis"></a><br>Daily sign-ups on a date axis |
| <a href="#call-centre-queue-over-one-day"><img src="../docs/images/showcase-25-queue-erlang-c.png" width="400" alt="Call-centre queue over one day"></a><br>Call-centre queue over one day | <a href="#quarterly-business-review-deck-with-lmvideo-charts"><img src="../docs/images/showcase-26-qbr-deck.png" width="400" alt="Quarterly business review deck with lmvideo charts"></a><br>Quarterly business review deck with lmvideo charts |

## Damped oscillator dashboard

lmnum integrates a damped second-order oscillator with CVODE and checks the endpoint against the closed form; lmplot builds a three-panel dashboard from the saved solution: time series against the analytic response, phase portrait, and energy decaying inside its exp(-2 zeta omega t) envelope.

Hosts: lmnum → lmplot. Output: `images/showcase-01-oscillator.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/01-oscillator-ode-plot.lms
```

## Discounted project cashflows

lmfinance discounts project cashflows continuously at 8%; lmnum reads those computed values and lmdraw draws their amounts, present values and net present value.

Hosts: lmfinance → lmnum → lmdraw. Output: `images/showcase-02-finance-cashflows.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/02-finance-cashflows-draw.lms
```

## Shallow-water gravity pulse

lmweather evolves a Gaussian shallow-water pulse; lmplot overlays four snapshots and labels the gravity-wave speed.

Hosts: lmweather → lmplot. Output: `images/showcase-03-weather-pulse.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/03-weather-pulse-plot.lms
```

## Hohmann transfer: equal-time markers

lmspace propagates a Hohmann transfer from a 7000 km orbit to geostationary radius; lmcad renders the sampled trajectory as a tube between the departure and arrival rings, with markers at equal time intervals that bunch up near apogee where the spacecraft is slowest.

Hosts: lmspace → lmcad. Output: `images/showcase-04-space-orbit-cad.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/04-space-orbit-cad.lms
```

## Cargo-ramp force balance

lmphysics measures acceleration of a six-kilogram cargo block on a 24-degree ramp; lmdraw draws the force balance with correctly oriented, consistently scaled vectors.

Hosts: lmphysics → lmdraw. Output: `images/showcase-05-physics-free-body.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/05-physics-free-body.lms
```

## Finite-element Poisson field

lmfluid solves a manufactured Poisson problem and lmplot renders the sampled field with a color ramp.

Hosts: lmfluid → lmplot. Output: `images/showcase-06-fluid-poisson-plot.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/06-fluid-poisson-plot.lms
```

## Michaelis-Menten from mechanism

lmbio integrates the elementary reactions E + S <-> ES -> E + P at ten substrate levels and measures the quasi-steady rate of each run; lmplot shows those rates falling on the hyperbola Vmax S / (Km + S) with Km = (koff + kcat) / kon and Vmax = kcat E0, constants the mechanism never states.

Hosts: lmbio → lmplot. Output: `images/showcase-07-enzyme-response.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/07-enzyme-response.lms
```

## Cell growth and motility

lmcell evolves two motile populations with different cycle and death rates; lmplot compares their computed final positions and total living-cell count over time.

Hosts: lmcell → lmplot. Output: `images/showcase-08-cell-pattern.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/08-cell-pattern.lms
```

## Photon attenuation and build-up in water

lmparticle runs seeded Monte Carlo histories of 662 keV photons through six water slabs and counts uncollided photons and all forward crossings; lmplot compares the uncollided fraction with exp(-mu x) on a log axis and shows the scattered build-up above it.

Hosts: lmparticle → lmplot. Output: `images/showcase-09-photon-transport.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/09-photon-transport.lms
```

## Water dimer: hydrogen bond in 3D

lmmolecule minimizes two flexible TIP3P molecules into the hydrogen-bonded dimer (about -6.5 kcal/mol at R(O-O) = 2.74 A) and scans the acceptor along the O-O axis; lmcad renders the minimized coordinates as ball-and-stick with the hydrogen bond as a cyan rod; lmplot places that render beside the energy curve.

Hosts: lmmolecule → lmcad → lmplot. Output: `images/showcase-10-molecule-dimer-cad.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/10-molecule-dimer-cad.lms
```

## Shielding by mass: lead, aluminum, water

lmparticle transports 662 keV photons through lead, aluminum and water slabs of equal mass per area; lmdraw draws the three layouts to scale; lmplot combines that layout with the measured transmission curves, showing that per gram lead is only modestly better where Compton scattering dominates.

Hosts: lmparticle → lmdraw → lmplot. Output: `images/showcase-11-particle-shield-layout.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/11-particle-shield-layout.lms
```

## Geostrophic adjustment, animated

lmweather releases a 600 km Gaussian height bump at rest on an f-plane: inertia-gravity waves radiate at sqrt(gH) while a weaker balanced bump set by the Rossby radius stays behind, with potential vorticity conserved; lmplot renders a frame every 30 minutes and ffmpeg assembles the 14-hour animation.

Hosts: lmweather → lmplot. Output: `images/showcase-12-weather-adjustment.gif`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/12-weather-adjustment-gif.lms
```

## Dosing regimen inside a therapeutic window

lmbio integrates a one-compartment oral model for 800 mg a day given as 400 mg every 12 h or 800 mg daily, restarting at each dose; both share the asserted average level 7.2 mg/L but only the twice-daily regimen stays inside 3-12 mg/L. lmdraw draws the compartment model; lmplot overlays window, average and both profiles.

Hosts: lmbio → lmdraw → lmplot. Output: `images/showcase-13-bio-dosing-regimen.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/13-bio-dosing-regimen.lms
```

## Damping-ratio sweep as a contact sheet

lmnum integrates the unit-step response of a second-order system for six damping ratios and checks each overshoot against exp(-pi zeta / sqrt(1 - zeta^2)); lmplot draws one panel per case; lmimg assembles the panels into a labelled report sheet with a header band.

Hosts: lmnum → lmplot → lmimg. Output: `images/showcase-14-num-sweep-contact-sheet.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/14-num-sweep-contact-sheet.lms
```

## Equalizer: designed versus measured

lmaudio designs a three-band equalizer as biquads (low shelf, presence peak, high shelf), measures the whole chain by passing a unit impulse through it, and sends a plucked string through the same chain; lmplot overlays the designed band responses with the measured chain and the dry and equalized string spectra.

Hosts: lmaudio → lmplot. Output: `images/showcase-15-audio-eq-measurement.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/15-audio-eq-measurement.lms
```

## Kepler orbit energy check

lmspace propagates an eccentric orbit (perigee 7000 km, apogee 15000 km) for two periods with RK45 at 1e-12 tolerance; lmplot draws the path, the radius against time and the relative energy error, whose largest excursion is about 2e-12, a measured integrator noise floor.

Hosts: lmspace → lmplot. Output: `images/showcase-16-kepler-conservation.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/16-kepler-conservation.lms
```

## Driven oscillator: transient to steady state

lmnum integrates a damped oscillator driven near resonance from rest, with the forcing carried as a third ODE state, and checks the late-time amplitude against the closed form; lmplot draws the beating transient settling onto the steady amplitude and the (x, v) phase portrait.

Hosts: lmnum → lmplot. Output: `images/showcase-17-oscillator-driven.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/17-oscillator-driven-transient.lms
```

## Intermediate-axis tumble of a free plate

lmphysics spins a free plate at 10 rad/s about its intermediate principal axis, nudged by 0.01 rad/s; the recorded body angular velocity shows the tennis-racket instability growing into tumbles every 3 s, while kinetic energy and angular momentum drift below 1e-5. The composition is drawn in lmplot, and the same flip appears in the lmphysics tennis_racket example.

Hosts: lmphysics → lmplot. Output: `images/showcase-18-rigid-body-intermediate-axis.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/18-rigid-body-intermediate-axis.lms
```

## Finite-element error against a known answer

lmfluid solves a Poisson problem on an 8 x 8 mesh with linear and quadratic elements for a quadratic exact solution; the quadratic elements reproduce it to solver tolerance while the linear error map shows the element pattern. lmplot draws both |error| maps on one colour scale.

Hosts: lmfluid → lmplot. Output: `images/showcase-19-fem-poisson-error.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/19-fem-poisson-error.lms
```

## Heat conduction in x and t

lmnum integrates one-dimensional heat conduction by the method of lines with its stiff solver and checks the result against the exact exponential decay; lmplot draws the x-t spacetime heat map and the profiles at three times against the exact curves.

Hosts: lmnum → lmplot. Output: `images/showcase-20-heat-spacetime.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/20-heat-spacetime.lms
```

## Forecast with a 95 % prediction band

lmnum fits a trend with annual harmonics to 60 months of demand by least squares, computes the residual deviation and the 95 % prediction interval of each of 12 future months from the design matrix, and checks that the true future values fall inside the band; lmplot draws the history, the fit, the forecast and its widening band.

Hosts: lmnum → lmplot. Output: `images/showcase-21-forecast-band.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/21-forecast-prediction-band.lms
```

## Seasonal decomposition by least squares

lmnum fits a quadratic trend with annual and semi-annual harmonics to eight years of monthly data in one least-squares solve, and recovers the 10-unit annual amplitude and the 2.5 residual deviation within stated tolerances; lmplot draws observed, trend, seasonal and residual panels on a shared time axis.

Hosts: lmnum → lmplot. Output: `images/showcase-22-seasonal-decomposition.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/22-seasonal-decomposition.lms
```

## Regression diagnostics: predicted, actual and residuals

lmnum fits a linear model to 120 observations that contain a quadratic term it does not include, with R^2 and RMSE from the least-squares solve; the predicted-against-actual and residuals-against-predicted panels show the misfit as a curve in the residuals.

Hosts: lmnum → lmplot. Output: `images/showcase-23-regression-residuals.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/23-regression-residuals.lms
```

## Daily sign-ups on a date axis

lmnum generates a seeded year of daily sign-ups with a trend and a weekend effect, builds the trailing 7-day mean and checks that weekends fall about 12 below weekdays; lmplot draws the daily counts and the mean on a real date axis, with the start date converted by gnuplot strptime.

Hosts: lmnum → lmplot. Output: `images/showcase-24-signups-date-axis.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/24-signups-date-axis.lms
```

## Call-centre queue over one day

lmnum evaluates the M/M/c Erlang-C formula for eight agents at each hour of a day with a peak arrival rate of 70 calls per hour, after checking the textbook value C(2, 1) = 1/3; lmplot draws the busy agents on the right axis and the mean queue length on the left.

Hosts: lmnum → lmplot. Output: `images/showcase-25-queue-erlang-c.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/25-queue-erlang-c.lms
```

## Quarterly business review deck with lmvideo charts

lmvideo draws three Skia charts (quarterly revenue, operating margin, regional mix) from one set of figures; lmoffice places them on the slides of a six-slide Open XML deck with highlights, bullets and notes. The picture is a LibreOffice render of the finished deck.

Hosts: lmvideo → lmoffice. Output: `images/showcase-26-qbr-deck.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/26-qbr-deck-charts.lms
```
