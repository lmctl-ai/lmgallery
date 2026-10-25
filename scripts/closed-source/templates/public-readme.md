# <Product name>

<One-sentence description and representative image. Keep this README as the
product's demo page. Public documentation and example paths are stable so the
`lmctl autorun` links continue to work.>

![<Alt text>](docs/images/<hero-image>.png)

## Install

Use the public release for your platform. Verify the downloaded asset with
[`SHA256SUMS`](https://github.com/lmctl-ai/<product>/releases/latest).
In an lmscript host block, keep the existing public identity:

```lms
p = _lmcode_ cli="<product>" install="github:lmctl-ai/<product>@latest";
// Example calls...
end _lmcode_
```

## Examples

Keep each existing `examples/*.lms` path and its committed picture. Captions
include the raw public URL, for example:

```text
lmctl autorun https://raw.githubusercontent.com/lmctl-ai/<product>/main/examples/<example>.lms
```

## License and support

The public README, docs, and examples use the license stated in [`LICENSE`](LICENSE).
The binary license is [`LICENSE-binaries`](LICENSE-binaries); third-party
terms and required notices are in [`THIRD_PARTY_NOTICES`](THIRD_PARTY_NOTICES)
and [`licenses/`](licenses/).

This public peer contains the demo/docs/examples and released binaries. New
implementation source is maintained in the private `lmctlhq/<product>` peer;
older public MIT commits and tags remain in this repository's history.

Open product questions in [Issues](https://github.com/lmctl-ai/<product>/issues).
Source-code pull requests are not accepted here. <State whether docs/example
pull requests are welcome and where to report a security issue.>
