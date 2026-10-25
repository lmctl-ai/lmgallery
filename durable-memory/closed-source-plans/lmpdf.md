# Closed-source split dry-run: lmpdf

- Source repo: `/home/mma/repos/dsl/lmpdf`
- Source revision: `821ebcede14c7b3775df2f934d8287dec4807888`
- Private peer target: `lmctlhq/lmpdf` (transfer this repository, then set it private, only after owner approval)
- Public peer target: `lmctl-ai/lmpdf` (recreate at the old slug after transfer; preserve README/example paths)

## Exact tracked-file plan

### Public peer (`lmctl-ai/lmpdf`): 66 tracked files
- `assets/fonts/LICENSE-DejaVu.txt` → `docs/third-party-licenses/assets/fonts/LICENSE-DejaVu.txt`
- `assets/fonts/LICENSE-Kosugi-Apache-2.0.txt` → `docs/third-party-licenses/assets/fonts/LICENSE-Kosugi-Apache-2.0.txt`
- `assets/fonts/LICENSE-OFL-1.1.txt` → `docs/third-party-licenses/assets/fonts/LICENSE-OFL-1.1.txt`
- `docs/examples/bilingual-arabic-cjk.png`
- `docs/examples/certificate.png`
- `docs/examples/contract-pdfa.png`
- `docs/examples/invoice-multipage.png`
- `docs/examples/letterhead-footnotes.png`
- `docs/examples/newsletter-two-column.png`
- `docs/examples/report-40-pages.png`
- `docs/examples/results.json`
- `docs/examples/resume.png`
- `docs/gallery/parity/business-agenda.png`
- `docs/gallery/parity/business-job-offer.png`
- `docs/gallery/parity/business-letter.png`
- `docs/gallery/parity/business-memo.png`
- `docs/gallery/parity/business-press-release.png`
- `docs/gallery/parity/business-proposal.png`
- `docs/gallery/parity/business-purchase-order.png`
- `docs/gallery/parity/business-report-with-toc.png`
- `docs/gallery/parity/cross-workbook-memo.png`
- `docs/gallery/parity/education-assessment-rubric.png`
- `docs/gallery/parity/education-certificate.png`
- `docs/gallery/parity/education-lesson-plan.png`
- `docs/gallery/parity/education-syllabus.png`
- `docs/gallery/parity/hr-offer-letter.png`
- `docs/gallery/parity/hr-onboarding-checklist.png`
- `docs/gallery/parity/hr-org-chart.png`
- `docs/gallery/parity/hr-performance-review.png`
- `docs/gallery/parity/invoice.png`
- `docs/gallery/parity/legal-demand-letter.png`
- `docs/gallery/parity/legal-lease.png`
- `docs/gallery/parity/legal-nda.png`
- `docs/gallery/parity/legal-power-of-attorney.png`
- `docs/gallery/parity/legal-services-agreement.png`
- `docs/gallery/parity/legal-terms-of-service.png`
- `docs/gallery/parity/markdown-business-letter.png`
- `docs/gallery/parity/markdown-lesson-plan.png`
- `docs/gallery/parity/markdown-meeting-minutes.png`
- `docs/gallery/parity/markdown-nda.png`
- `docs/gallery/parity/markdown-report-toc.png`
- `docs/gallery/parity/markdown-resume.png`
- `docs/gallery/parity/markdown-review-notes.png`
- `docs/gallery/parity/markdown-services-agreement.png`
- `docs/gallery/parity/marketing-case-study.png`
- `docs/gallery/parity/marketing-content-plan.png`
- `docs/gallery/parity/meetingminutes.png`
- `docs/gallery/parity/operations-inspection-checklist.png`
- `docs/gallery/parity/operations-lease-abstract.png`
- `docs/gallery/parity/report.png`
- `docs/gallery/parity/resume-academic-cv.png`
- `docs/gallery/parity/resume-classic.png`
- `docs/gallery/parity/resume-cover-letter.png`
- `docs/gallery/parity/resume-reference-sheet.png`
- `docs/gallery/parity/resume-two-column.png`
- `examples/bilingual-arabic-cjk.lms`
- `examples/certificate.lms`
- `examples/contract-pdfa.lms`
- `examples/invoice-multipage.lms`
- `examples/letterhead-footnotes.lms`
- `examples/newsletter-two-column.lms`
- `examples/render.py`
- `examples/report-40-pages.lms`
- `examples/resume.lms`
- `README.md`
- `THIRD_PARTY_NOTICES.md`
- `LICENSE` (new binary-license draft from templates/LICENSE-binaries.md)
- `LICENSE-examples` (MIT text from templates/LICENSE-examples-MIT; source repo LICENSE stays private)

### Private peer (`lmctlhq/lmpdf`): 395 tracked files
- ``
- `.gitattributes`
- `.github/workflows/ci.yml`
- `.github/workflows/parity.yml`
- `.gitignore`
- `assets/fonts/Caladea-Bold.ttf`
- `assets/fonts/Caladea-BoldItalic.ttf`
- `assets/fonts/Caladea-Italic.ttf`
- `assets/fonts/Caladea-Regular.ttf`
- `assets/fonts/Carlito-Bold.ttf`
- `assets/fonts/Carlito-BoldItalic.ttf`
- `assets/fonts/Carlito-Italic.ttf`
- `assets/fonts/Carlito-Regular.ttf`
- `assets/fonts/DejaVuSans-Bold.ttf`
- `assets/fonts/DejaVuSans.ttf`
- `assets/fonts/DejaVuSansMono-Bold.ttf`
- `assets/fonts/DejaVuSansMono.ttf`
- `assets/fonts/Kosugi-Regular.ttf`
- `assets/fonts/LiberationMono-Bold.ttf`
- `assets/fonts/LiberationMono-BoldItalic.ttf`
- `assets/fonts/LiberationMono-Italic.ttf`
- `assets/fonts/LiberationMono-Regular.ttf`
- `assets/fonts/LiberationSans-Bold.ttf`
- `assets/fonts/LiberationSans-BoldItalic.ttf`
- `assets/fonts/LiberationSans-Italic.ttf`
- `assets/fonts/LiberationSans-Regular.ttf`
- `assets/fonts/LiberationSerif-Bold.ttf`
- `assets/fonts/LiberationSerif-BoldItalic.ttf`
- `assets/fonts/LiberationSerif-Italic.ttf`
- `assets/fonts/LiberationSerif-Regular.ttf`
- `assets/fonts/NotoNaskhArabic-Bold.ttf`
- `assets/fonts/NotoNaskhArabic-Regular.ttf`
- `Cargo.lock`
- `Cargo.toml`
- `deny.toml`
- `docx-schema.lock`
- `dslvm/Cargo.toml`
- `dslvm/src/lib.rs`
- `dslvm/src/sha256.rs`
- `dslvm/src/stdlib.rs`
- `dslvm/src/stdlib/collections.rs`
- `dslvm/src/stdlib/file.rs`
- `dslvm/src/stdlib/math.rs`
- `dslvm/src/stdlib/testing_tests.rs`
- `dslvm/src/stdlib/testing.rs`
- `durable-memory/01-library-research.md`
- `durable-memory/02-docx-alignment.md`
- `durable-memory/03-pdf-foundation-ResearchArgon.md`
- `durable-memory/03-pdf-foundation-ResearchOpus.md`
- `durable-memory/03-pdf-foundation-ResearchSol.md`
- `durable-memory/04-decision.md`
- `durable-memory/05-architecture.md`
- `durable-memory/06-docx-parity.md`
- `durable-memory/07-parity-report.md`
- `durable-memory/08-release.md`
- `durable-memory/09-pdf-examples.md`
- `durable-memory/index.md`
- `fonts.json`
- `LICENSE`
- `release/budget-notes/.gitkeep`
- `release/budgets.json`
- `release/native-baseline.json`
- `release/poppler-linux-64.explicit`
- `release/poppler-packages.json`
- `research/.gitignore`
- `research/cpp-skia-pdf/assets/DejaVuSans.ttf`
- `research/cpp-skia-pdf/assets/logo.png`
- `research/cpp-skia-pdf/main.cpp`
- `research/go-maroto/assets/DejaVuSans-Bold.ttf`
- `research/go-maroto/assets/DejaVuSans.ttf`
- `research/go-maroto/assets/logo.png`
- `research/go-maroto/go.mod`
- `research/go-maroto/go.sum`
- `research/go-maroto/main.go`
- `research/README.md`
- `research/ResearchArgon/c-libharu/main.c`
- `research/ResearchArgon/c-libharu/README.md`
- `research/ResearchArgon/cpp-cairo-pango/main.cpp`
- `research/ResearchArgon/cpp-cairo-pango/README.md`
- `research/ResearchArgon/cpp-podofo/main.cpp`
- `research/ResearchArgon/cpp-podofo/README.md`
- `research/ResearchArgon/cpp-skia-pdf/main.cpp`
- `research/ResearchArgon/cpp-skia-pdf/README.md`
- `research/ResearchArgon/csharp-skiasharp/csharp-skiasharp.csproj`
- `research/ResearchArgon/csharp-skiasharp/Program.cs`
- `research/ResearchArgon/csharp-skiasharp/README.md`
- `research/ResearchArgon/go-gopdf/go.mod`
- `research/ResearchArgon/go-gopdf/go.sum`
- `research/ResearchArgon/go-gopdf/main.go`
- `research/ResearchArgon/go-gopdf/README.md`
- `research/ResearchArgon/go-maroto/go.mod`
- `research/ResearchArgon/go-maroto/go.sum`
- `research/ResearchArgon/go-maroto/main.go`
- `research/ResearchArgon/go-maroto/README.md`
- `research/ResearchArgon/java-fop/fop.xconf`
- `research/ResearchArgon/java-fop/pom.xml`
- `research/ResearchArgon/java-fop/README.md`
- `research/ResearchArgon/java-fop/src/main/java/com/argon/pdf/FopProof.java`
- `research/ResearchArgon/java-openpdf/pom.xml`
- `research/ResearchArgon/java-openpdf/README.md`
- `research/ResearchArgon/java-openpdf/src/main/java/com/argon/pdf/OpenPdfProof.java`
- `research/ResearchArgon/java-pdfbox/pom.xml`
- `research/ResearchArgon/java-pdfbox/README.md`
- `research/ResearchArgon/java-pdfbox/src/main/java/com/argon/pdf/PdfBoxProof.java`
- `research/ResearchArgon/README.md`
- `research/ResearchArgon/rust-krilla/Cargo.toml`
- `research/ResearchArgon/rust-krilla/README.md`
- `research/ResearchArgon/rust-krilla/src/main.rs`
- `research/ResearchArgon/rust-pdf-writer/Cargo.toml`
- `research/ResearchArgon/rust-pdf-writer/README.md`
- `research/ResearchArgon/rust-pdf-writer/src/main.rs`
- `research/ResearchArgon/rust-printpdf/Cargo.toml`
- `research/ResearchArgon/rust-printpdf/README.md`
- `research/ResearchArgon/rust-printpdf/src/main.rs`
- `research/ResearchArgon/rust-typst/Cargo.toml`
- `research/ResearchArgon/rust-typst/README.md`
- `research/ResearchArgon/rust-typst/src/main.rs`
- `research/ResearchOpus/.gitignore`
- `research/ResearchOpus/assets/logo-alpha.png`
- `research/ResearchOpus/assets/photo.jpg`
- `research/ResearchOpus/assets/sRGB.icc`
- `research/ResearchOpus/cpp-cairo-pango/build.sh`
- `research/ResearchOpus/cpp-cairo-pango/Dockerfile`
- `research/ResearchOpus/cpp-cairo-pango/main.c`
- `research/ResearchOpus/cpp-cairo-pango/NOTES.md`
- `research/ResearchOpus/cpp-libharu/build.sh`
- `research/ResearchOpus/cpp-libharu/Dockerfile`
- `research/ResearchOpus/cpp-libharu/main.c`
- `research/ResearchOpus/cpp-libharu/NOTES.md`
- `research/ResearchOpus/cpp-others/NOTES.md`
- `research/ResearchOpus/cpp-podofo/build.sh`
- `research/ResearchOpus/cpp-podofo/Dockerfile`
- `research/ResearchOpus/cpp-podofo/main.cpp`
- `research/ResearchOpus/cpp-podofo/NOTES.md`
- `research/ResearchOpus/cpp-skia/build.sh`
- `research/ResearchOpus/cpp-skia/main.cpp`
- `research/ResearchOpus/cpp-skia/NOTES.md`
- `research/ResearchOpus/cs-migradoc/cs-migradoc.csproj`
- `research/ResearchOpus/cs-migradoc/NOTES.md`
- `research/ResearchOpus/cs-migradoc/Program.cs`
- `research/ResearchOpus/cs-questpdf/cs-questpdf.csproj`
- `research/ResearchOpus/cs-questpdf/NOTES.md`
- `research/ResearchOpus/cs-questpdf/Program.cs`
- `research/ResearchOpus/cs-skiasharp/cs-skiasharp.csproj`
- `research/ResearchOpus/cs-skiasharp/NOTES.md`
- `research/ResearchOpus/cs-skiasharp/Program.cs`
- `research/ResearchOpus/go-fpdf/go.mod`
- `research/ResearchOpus/go-fpdf/go.sum`
- `research/ResearchOpus/go-fpdf/main.go`
- `research/ResearchOpus/go-fpdf/NOTES.md`
- `research/ResearchOpus/go-gopdf/go.mod`
- `research/ResearchOpus/go-gopdf/go.sum`
- `research/ResearchOpus/go-gopdf/main.go`
- `research/ResearchOpus/go-gopdf/NOTES.md`
- `research/ResearchOpus/go-gopdf/pdfa.go`
- `research/ResearchOpus/go-gopdf/shape.go`
- `research/ResearchOpus/go-maroto/go.mod`
- `research/ResearchOpus/go-maroto/go.sum`
- `research/ResearchOpus/go-maroto/main.go`
- `research/ResearchOpus/go-maroto/NOTES.md`
- `research/ResearchOpus/go-maroto/pdfa.go`
- `research/ResearchOpus/go-misc/NOTES.md`
- `research/ResearchOpus/go-pdfcpu/NOTES.md`
- `research/ResearchOpus/java-fop/NOTES.md`
- `research/ResearchOpus/java-fop/pom.xml`
- `research/ResearchOpus/java-fop/src/main/java/proof/Main.java`
- `research/ResearchOpus/java-fop/src/main/resources/META-INF/native-image/ropus/java-fop/jni-config.json`
- `research/ResearchOpus/java-fop/src/main/resources/META-INF/native-image/ropus/java-fop/proxy-config.json`
- `research/ResearchOpus/java-fop/src/main/resources/META-INF/native-image/ropus/java-fop/reflect-config.json`
- `research/ResearchOpus/java-fop/src/main/resources/META-INF/native-image/ropus/java-fop/resource-config.json`
- `research/ResearchOpus/java-fop/src/main/resources/META-INF/native-image/ropus/java-fop/serialization-config.json`
- `research/ResearchOpus/java-fop/src/main/resources/META-INF/services/org.apache.fop.render.ImageHandler`
- `research/ResearchOpus/java-fop/src/main/resources/META-INF/services/org.apache.xmlgraphics.image.loader.spi.ImageLoaderFactory`
- `research/ResearchOpus/java-fop/src/main/resources/META-INF/services/org.apache.xmlgraphics.image.loader.spi.ImagePreloader`
- `research/ResearchOpus/java-openpdf/NOTES.md`
- `research/ResearchOpus/java-openpdf/pom.xml`
- `research/ResearchOpus/java-openpdf/src/main/java/proof/Main.java`
- `research/ResearchOpus/java-openpdf/src/main/resources/META-INF/native-image/ropus/java-openpdf/jni-config.json`
- `research/ResearchOpus/java-openpdf/src/main/resources/META-INF/native-image/ropus/java-openpdf/reflect-config.json`
- `research/ResearchOpus/java-openpdf/src/main/resources/META-INF/native-image/ropus/java-openpdf/resource-config.json`
- `research/ResearchOpus/java-others/NOTES.md`
- `research/ResearchOpus/java-pdfbox/NOTES.md`
- `research/ResearchOpus/java-pdfbox/pom.xml`
- `research/ResearchOpus/java-pdfbox/src/main/java/proof/Cjk.java`
- `research/ResearchOpus/java-pdfbox/src/main/java/proof/Main.java`
- `research/ResearchOpus/java-pdfbox/src/main/resources/META-INF/native-image/ropus/java-pdfbox/jni-config.json`
- `research/ResearchOpus/java-pdfbox/src/main/resources/META-INF/native-image/ropus/java-pdfbox/reflect-config.json`
- `research/ResearchOpus/java-pdfbox/src/main/resources/META-INF/native-image/ropus/java-pdfbox/resource-config.json`
- `research/ResearchOpus/MATRIX-KEYS.md`
- `research/ResearchOpus/parity-nda/docx.typ`
- `research/ResearchOpus/parity-nda/model.json`
- `research/ResearchOpus/parity-nda/nda-overlay.png`
- `research/ResearchOpus/parity-nda/NOTES.md`
- `research/ResearchOpus/rust-genpdf/Cargo.lock`
- `research/ResearchOpus/rust-genpdf/Cargo.toml`
- `research/ResearchOpus/rust-genpdf/NOTES.md`
- `research/ResearchOpus/rust-genpdf/src/main.rs`
- `research/ResearchOpus/rust-krilla/Cargo.lock`
- `research/ResearchOpus/rust-krilla/Cargo.toml`
- `research/ResearchOpus/rust-krilla/NOTES.md`
- `research/ResearchOpus/rust-krilla/src/main.rs`
- `research/ResearchOpus/rust-lopdf/Cargo.lock`
- `research/ResearchOpus/rust-lopdf/Cargo.toml`
- `research/ResearchOpus/rust-lopdf/NOTES.md`
- `research/ResearchOpus/rust-lopdf/src/main.rs`
- `research/ResearchOpus/rust-pdfwriter/Cargo.lock`
- `research/ResearchOpus/rust-pdfwriter/Cargo.toml`
- `research/ResearchOpus/rust-pdfwriter/NOTES.md`
- `research/ResearchOpus/rust-pdfwriter/src/main.rs`
- `research/ResearchOpus/rust-printpdf/Cargo.lock`
- `research/ResearchOpus/rust-printpdf/Cargo.toml`
- `research/ResearchOpus/rust-printpdf/NOTES.md`
- `research/ResearchOpus/rust-printpdf/src/main.rs`
- `research/ResearchOpus/rust-typst/Cargo.lock`
- `research/ResearchOpus/rust-typst/Cargo.toml`
- `research/ResearchOpus/rust-typst/NOTES.md`
- `research/ResearchOpus/rust-typst/src/main.rs`
- `research/ResearchOpus/rust-typst/src/template.typ`
- `research/ResearchOpus/SPEC.md`
- `research/ResearchOpus/tools/Dockerfile.tools`
- `research/ResearchOpus/tools/fetch-assets.sh`
- `research/ResearchOpus/tools/package.json`
- `research/ResearchOpus/tools/parity_lines.py`
- `research/ResearchOpus/tools/pdfjs-check.mjs`
- `research/ResearchOpus/tools/validate.py`
- `research/ResearchSol/.gitignore`
- `research/ResearchSol/coverage.csv`
- `research/ResearchSol/csharp/pdfsharp/PdfSharpProof.csproj`
- `research/ResearchSol/csharp/pdfsharp/Program.cs`
- `research/ResearchSol/csharp/questpdf/Program.cs`
- `research/ResearchSol/csharp/questpdf/QuestPdfProof.csproj`
- `research/ResearchSol/csharp/results.md`
- `research/ResearchSol/csharp/run.sh`
- `research/ResearchSol/csharp/skia-sharp/Program.cs`
- `research/ResearchSol/csharp/skia-sharp/SkiaSharpProof.csproj`
- `research/ResearchSol/go/go.mod`
- `research/ResearchSol/go/go.sum`
- `research/ResearchSol/go/main.go`
- `research/ResearchSol/go/run.sh`
- `research/ResearchSol/java/fop/fop.xconf`
- `research/ResearchSol/java/fop/Generate.java`
- `research/ResearchSol/java/fop/GeneratePdfA.java`
- `research/ResearchSol/java/openpdf/Generate.java`
- `research/ResearchSol/java/pdfbox/Generate.java`
- `research/ResearchSol/java/pom.xml`
- `research/ResearchSol/java/results.md`
- `research/ResearchSol/java/run.sh`
- `research/ResearchSol/native/cairo_pango_proof.c`
- `research/ResearchSol/native/cairo-run.sh`
- `research/ResearchSol/native/libharu_proof.c`
- `research/ResearchSol/native/podofo_proof.cpp`
- `research/ResearchSol/native/results.md`
- `research/ResearchSol/native/skia/results.md`
- `research/ResearchSol/native/skia/skia_pdf_proof.cpp`
- `research/ResearchSol/native/validator-results.txt`
- `research/ResearchSol/README.md`
- `research/ResearchSol/registry.json`
- `research/ResearchSol/rust/.gitignore`
- `research/ResearchSol/rust/Cargo.lock`
- `research/ResearchSol/rust/Cargo.toml`
- `research/ResearchSol/rust/results.md`
- `research/ResearchSol/rust/results/verapdf-krilla-a2b-positive.xml`
- `research/ResearchSol/rust/run.sh`
- `research/ResearchSol/rust/src/bin/krilla_proof.rs`
- `research/ResearchSol/rust/src/bin/pdfwriter_proof.rs`
- `research/ResearchSol/rust/src/bin/printpdf_proof.rs`
- `research/ResearchSol/rust/src/main.rs`
- `research/ResearchSol/typst/bench.typ`
- `research/ResearchSol/typst/fixture.typ`
- `research/ResearchSol/typst/font-manifest.json`
- `research/ResearchSol/typst/results.md`
- `research/ResearchSol/typst/run.sh`
- `research/ResearchSol/validation/binary-sizes.json`
- `research/ResearchSol/validation/cairo-a2b-negative.xml`
- `research/ResearchSol/validation/corpus.json`
- `research/ResearchSol/validation/pdfjs-results.jsonl`
- `research/ResearchSol/validation/pdfjs.mjs`
- `research/ResearchSol/validation/README.md`
- `research/ResearchSol/validation/typst-a1.xml`
- `research/ResearchSol/validation/typst-a4.xml`
- `research/ResearchSol/validation/typst-final-a2b.xml`
- `research/ResearchSol/validation/typst-final-a3b.xml`
- `research/ResearchSol/validation/typst-final-ua.xml`
- `research/ResearchSol/validation/validate.py`
- `research/rust-typst/assets/DejaVuSans-Bold.ttf`
- `research/rust-typst/assets/DejaVuSans.ttf`
- `research/rust-typst/assets/logo.png`
- `research/rust-typst/Cargo.lock`
- `research/rust-typst/Cargo.toml`
- `research/rust-typst/doc.typ`
- `research/rust-typst/src/main.rs`
- `schema/docx.dsl.json`
- `scripts/.gitignore`
- `scripts/benchmark-release.py`
- `scripts/bootstrap/Cargo.lock`
- `scripts/bootstrap/Cargo.toml`
- `scripts/bootstrap/src/main.rs`
- `scripts/check-budgets.py`
- `scripts/check-linkage.py`
- `scripts/check-parity-report.py`
- `scripts/check-pins.py`
- `scripts/check-signatures.py`
- `scripts/compile-release.sh`
- `scripts/conformance.py`
- `scripts/generate-notices.py`
- `scripts/install-libreoffice.sh`
- `scripts/install-poppler.sh`
- `scripts/install-verapdf.sh`
- `scripts/licenses/0BSD.txt`
- `scripts/licenses/Apache-2.0.txt`
- `scripts/licenses/CC0-1.0.txt`
- `scripts/licenses/fonts/Carlito.txt`
- `scripts/licenses/fonts/Liberation.txt`
- `scripts/licenses/fonts/NotoNaskhArabic.txt`
- `scripts/licenses/fonts/SOURCES.txt`
- `scripts/licenses/MIT.txt`
- `scripts/licenses/OFL-1.1.txt`
- `scripts/licenses/policy.json`
- `scripts/licenses/runtime-notices.json`
- `scripts/licenses/runtime/llvm-21.1.3/libunwind-LICENSE.TXT`
- `scripts/licenses/runtime/llvm-21.1.3/LICENSE.TXT`
- `scripts/licenses/runtime/musl-1.2.5-COPYRIGHT.txt`
- `scripts/licenses/runtime/rust-1.92.0-COPYRIGHT.txt`
- `scripts/licenses/runtime/rust-1.92.0-LICENSE-APACHE.txt`
- `scripts/licenses/runtime/rust-1.92.0-LICENSE-MIT.txt`
- `scripts/licenses/UPSTREAM-SHA256SUMS.txt`
- `scripts/measure-build.py`
- `scripts/package-release.py`
- `scripts/release/compiler.py`
- `scripts/release/test_notices.py`
- `scripts/render-release-fixture.py`
- `scripts/report-ci-time.py`
- `scripts/stamp-version.sh`
- `scripts/sync-docx-schema.sh`
- `scripts/sync-sdk.sh`
- `scripts/test-package-release.py`
- `scripts/test-parity-gate.py`
- `scripts/test-release-budgets.py`
- `sdk.lock`
- `src/lib.rs`
- `src/main.rs`
- `src/markdown/.gitignore`
- `src/markdown/Cargo.lock`
- `src/markdown/Cargo.toml`
- `src/markdown/examples/md_check.rs`
- `src/markdown/examples/pdf_dump.rs`
- `src/markdown/examples/pdf_markdown.rs`
- `src/markdown/src/lib.rs`
- `src/markdown/src/readback.rs`
- `src/markdown/src/record.rs`
- `src/markdown/src/render.rs`
- `src/markdown/src/syntax.rs`
- `src/markdown/tests/diff/lmoffice_diff.py`
- `src/markdown/tests/fuzz.rs`
- `src/markdown/tests/readback.rs`
- `src/markdown/tests/snapshot.rs`
- `src/markdown/tests/vectors.rs`
- `src/markdown/tests/vectors/badge.png`
- `src/markdown/tests/vectors/full-grammar.calls.txt`
- `src/markdown/tests/vectors/full-grammar.md`
- `src/markdown/tests/vectors/lmoffice_diff.json`
- `src/markdown/tests/vectors/lmpdf-full-grammar.pdf`
- `src/markdown/tests/vectors/readback-fixture.pdf`
- `src/markdown/tests/vectors/readback-fixture.typ`
- `src/model/mod.rs`
- `src/model/tests.rs`
- `src/typst/mod.rs`
- `src/typst/tests.rs`
- `tests/parity/.gitignore`
- `tests/parity/expected_differences.json`
- `tests/parity/known_failures/kf-align.lms`
- `tests/parity/known_failures/kf-bullets.lms`
- `tests/parity/known_failures/kf-first-heading-level2.lms`
- `tests/parity/known_failures/kf-header-footer.lms`
- `tests/parity/known_failures/kf-heading.lms`
- `tests/parity/known_failures/kf-md-list.lms`
- `tests/parity/known_failures/kf-pagebreak.lms`
- `tests/parity/known_failures/kf-paragraphs.lms`
- `tests/parity/known_failures/kf-quote.lms`
- `tests/parity/known_failures/kf-table.lms`
- `tests/parity/known_failures/kf-textbox.lms`
- `tests/parity/known_failures/README.md`
- `tests/parity/lo_convert.py`
- `tests/parity/markdown_roundtrip.py`
- `tests/parity/report_md.py`
- `tests/parity/report.json`
- `tests/parity/run.py`
- `tests/release/.gitignore`
- `tests/release/fixture-200.json`
- `tests/release/fixture.json`
- `tests/release/test-compiler-launcher.py`
- `tests/release/test-conformance.py`
- `tests/release/test-fixture-generator.py`
- `tests/release/test-linkage.py`
- `VERSION`

## Required path and release changes

- README-relative image/docs/example paths stay byte-for-byte at their current paths in the public peer.
- Raw autorun links checked: 0/0 map to public `.lms` files.
  - No README `lmctl autorun` raw URLs were found.
- Existing CI workflow paths move to the private peer; replace them with the private CI template and add public `.github/workflows/public-ci.yml`.
  - Private CI path: `.github/workflows/ci.yml`
  - Private CI path: `.github/workflows/parity.yml`
- Expected public release assets: `lmpdf-linux-x64`, `lmpdf-linux-arm64`, `lmpdf-macos-x64`, `lmpdf-macos-arm64`, `lmpdf-windows-x64.exe`, plus `SHA256SUMS`.
- README links to private source paths checked: 0 finding(s).
- Public-plan secret scan: 0 finding(s); values are never printed.
- Licensing: Carry generated crate/font notices, font hashes/attribution, and Rust runtime notices; GPL/AGPL-only dependencies remain disallowed.

## Verification result

- Autorun path check: PASS
- Public docs source-reference check: PASS
- Public-plan secret scan: PASS

This is a read-only plan. No files were copied or changed, no GitHub operation was performed, and no visibility was changed.

## Staging results (2026-10-25, STAGING only; nothing flipped)

- Staged from `origin/main` `821ebce` (unchanged at staging time) into `/home/mma/staging/closed-source/lmpdf-public/`: 69 files, public CI included, 8 examples under `examples/`.
- Release assets: latest `v0.1.60` downloaded to `lmpdf-release/` with `SHA256SUMS`; all five binaries verify. Three releases were published on 2026-10-25 (`v0.1.54`, `v0.1.57`, `v0.1.60`).
- Verified: no README autorun lines (0 targets); 59 local image/link refs resolve; no `/home/` path, no secret-like text, no source/blob link.
- Verified with the released binary `lmpdf 0.1.60` on PATH: `lmscript --check` 8/8 examples, and all 8 executed successfully.
- Hand corrections in the staged tree (re-apply after any refresh):
  1. `LICENSE` boundary sentence: releases up to and including `v0.1.60` are MIT; later releases use the Personal Use License (the tool hard-codes the lmaudio boundary).
  2. `THIRD_PARTY_NOTICES.md`: the Apache-2.0 URL was rewritten by the sanitizer to `https://www.apache.org/docs/third-party-licenses/LICENSE-2.0`, which is not an Apache address; restored to `https://www.apache.org/licenses/LICENSE-2.0`. The sanitizer also replaced `scripts/generate-notices.py` with `private implementation detail`; that placeholder is harmless but should read as the generator's name or be removed.

### Blockers

1. **Font licence classification.** The notices classify the bundled `Caladea-*.ttf` as `SPDX-License-Identifier: Apache-2.0`, while `durable-memory/08-release.md` records that the upstream release is OFL-1.1 and that the bundled bytes declare Apache-2.0. The owner must decide the classification (or replace the bytes) before publishing. Do not infer the licence from the name.
2. **Release contents differ.** The public release for `v0.1.60` includes build metrics, linkage reports and CI timing JSON. The closed-source template publishes only the five binaries, `SHA256SUMS`, `LICENSE` and notices. Decide which set is published.
3. **Active pipeline.** Each `main` push creates a release (`package-release.py`). The private workflow must not publish on pushes; it publishes only on dispatch or tag.

### Private CI

Staged at `/home/mma/staging/closed-source/lmpdf-private-ci.yml`, adapted from the current `ci.yml` and `parity.yml`: fast Linux path on `main` (pins, notices, release regression tests, host/Markdown tests, linux-x64 musl build, signature parity, determinism, public examples on a `lmpdf` copy in a runner bin dir); five-platform build with measured budgets and linkage, replay, conformance and parity (parity reads the public release anonymously); version from the tag (`LMPDF_VERSION`), not `0.1.<run>`; publish via `RELEASE_TOKEN` and `scripts/release-to-public.sh`. Not run. It needs `scripts/release-to-public.sh` in `lmctlhq/lmpdf` (template in `scripts/closed-source/templates/release-to-public.sh`).

### Pin inventory (8 consumers)

- `lmgallery` examples 43, 44, 45, 46, 49, 50 (`cli="lmpdf docx" install="github:lmctl-ai/lmpdf@v0.1.54"`) and `lmgallery/durable-memory/05-document-as-code.md`.
- `lmpdf/durable-memory/08-release.md` (a release link, historical, not a pin).

After the first new tag `<FIRST>` is chosen:

```sh
cd /home/mma/repos/dsl/lmgallery && git ls-files -z | xargs -0 sed -i -E 's#(github:lmctl-ai/lmpdf)@v[0-9]+\.[0-9]+\.[0-9]+#\1@<FIRST>#g'
```

### Quiesce and decisions before flip

- Stop pushes to `lmpdf` main and the release pipeline (three releases today). Re-check `origin/main` equals the staged SHA.
- Owner: resolve the Caladea classification; choose the first public tag; approve `lmpdf` in `~/tools/closed-source-approved.txt`; provide `RELEASE_TOKEN`; choose the release contents.
- Quiesce `lmgallery` pushes during the pin rewrite.

### Ready to flip: NO

Reasons: the Caladea licence classification is unresolved; the release contents are undecided; the release pipeline is active; the first tag and `RELEASE_TOKEN` are owner decisions.

## Re-staging after the decisions (2026-10-25)

- Font licences: all 30 bundled font files were checked against their own name tables (`Caladea` = Apache-2.0, `Carlito`/`Liberation`/`NotoNaskhArabic` = SIL OFL 1.1, `DejaVu` = Bitstream Vera, `Kosugi` = Apache-2.0). `fonts.json` matches every file. `scripts/generate-notices.py` now fails when a manifest licence differs from the file's own name table (demonstrated with a wrong Caladea entry). The OFL wording in `durable-memory/08-release.md` and `04-decision.md` is corrected.
- Release contents: `scripts/package-release.py` now writes only the five binaries, `SHA256SUMS`, `LICENSE` and `THIRD_PARTY_NOTICES.md` to `dist/`; metrics and linkage go to `--evidence`; CI timing goes to `ci-evidence/`. Test updated (3/3 pass). Local commit `60e062d`, not pushed. The current `v0.1.61` release still contains the extra JSON files; the next release from pushed `main` will not.
- Re-staged from `origin/main` `8647d95` (86 files). Boundary: releases up to and including `v0.1.61` are MIT (`gh release list`). Notices are byte-identical to the local source, which includes the unpushed `60e062d`.
- Verified: 0 autorun (no README autorun lines), 76 refs, no leaks; `lmscript --check` 8/8 and 8/8 executed with `lmpdf 0.1.61` (latest release, assets verified with `SHA256SUMS`).
- Non-binary extras in this release: `BUILD_METRICS.json`, `CI_JOB_TIMINGS.json`, `CI_MINUTES.json`, per-platform `*-build-metrics.json` and `*-linkage.json` (fixed in source, not yet released).

### Ready to flip: NO

1. Push local commit `60e062d` to `lmctl-ai/lmpdf` main after owner go-ahead; then the next release contains only the allowed assets; re-stage so the stage SHA equals the source.
2. Quiesce main pushes and the release pipeline (releases on every main push).
3. Install `scripts/release-to-public.sh` and the generated `lmpdf-private-ci.yml` into `lmctlhq/lmpdf`; not run.
4. Owner: first public tag and `RELEASE_TOKEN`; then pin rewrite (sed in the plan above).

## Re-staging after the release-contents and notice fixes (2026-10-25, latest)

- Source `origin/main` `60e062d` (release assembly without evidence JSON; font licence check; corrected Caladea wording). Staged 86 files; boundary `v0.1.62` (latest tag). Release `v0.1.62` contains exactly the five binaries, `SHA256SUMS`, `LICENSE` and `THIRD_PARTY_NOTICES.md`; its notice is byte-identical to the source.
- Verified: no leaks, 76 refs; `lmscript --check` 8/8 and 8/8 executed with the released `lmpdf 0.1.62`.
- Ready to flip: NO. Still open: quiesce `lmpdf` main (it releases on every push); owner selects the first public tag, approves `lmpdf` and provides `RELEASE_TOKEN`; install `scripts/release-to-public.sh` and the generated private CI in `lmctlhq/lmpdf` (not run); rewrite the consumer pins.
