# Cross-host compositions

Every command runs from an empty directory and writes the listed image. Each computation is passed to a separate rendering host through generated data.

## Damped engineering oscillator

lmnum integrates a damped second-order oscillator; lmplot renders displacement and velocity from the saved numerical solution.

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

lmspace propagates a low-orbit to geostationary Hohmann transfer; lmcad renders the complete sampled trajectory as tubes, with markers at equal time intervals.

Hosts: lmspace → lmcad. Output: `images/space-orbit-cad.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/04-space-orbit-cad.lms
```

## Cargo-ramp force balance

lmphysics measures acceleration of a six-kilogram cargo block on a 24-degree ramp; lmdraw draws the force balance with correctly oriented, consistently scaled vectors.

Hosts: lmphysics → lmdraw. Output: `images/physics-free-body.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/05-physics-free-body.lms
```

## Finite-element Poisson field

lmfluid solves a manufactured Poisson problem and lmplot renders the sampled field with a color ramp.

Hosts: lmfluid → lmplot. Output: `images/fluid-poisson-plot.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/06-fluid-poisson-plot.lms
```

## Enzyme response

lmbio integrates a reversible binding and catalytic mechanism at three substrate levels; lmplot compares product formation.

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

## Photon transport through water

lmparticle measures seeded 662 keV uncollided transmission through four water slab thicknesses; lmplot compares Monte Carlo estimates and uncertainty with exponential attenuation.

Hosts: lmparticle → lmplot. Output: `images/showcase-09-photon-transport.png`.

```sh
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/examples/09-photon-transport.lms
```
