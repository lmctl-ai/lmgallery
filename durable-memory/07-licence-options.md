# Binary licence options and EULA lineage — draft, 2026-10-26

Scope: lmaudio, lmcad, lmdraw, lmfilament, lmimg, lmmagnum, lmoffice, lmpdf and lmvideo binaries; other repos stay open source.
Intent: free, as-is personal or commercial use; standard restrictions on redistribution, sublicensing, selling, renting, leasing, lending, notice removal and reverse engineering, subject to legal/open-source rights; each release's shipped LICENSE governs it.

## Recommendation: an established proprietary freeware/binary EULA family

Use the **Obsidian/JetBrains-style proprietary end-user agreement** family, with original Lattice-specific text in [LICENSE-binaries.md](../scripts/closed-source/templates/LICENSE-binaries.md).
Public sources studied: [Obsidian terms](https://obsidian.md/terms) and [licence overview](https://obsidian.md/license), [JetBrains User Agreement](https://www.jetbrains.com/legal/docs/toolbox/user/) and [Toolbox individual subscription terms](https://www.jetbrains.com/legal/docs/toolbox/license_personal/).
These provide a familiar clause structure and vocabulary; Lattice's permissions and wording are original. Recognition/fit below is an assessment, not measured adoption or an enforceability opinion.
Obsidian permits free commercial use; JetBrains has product-specific trials, freemium modes and subscriptions. Lattice's free-use scope, copy-transfer restrictions and USD 50 cap are its own choices.
Choosing different terms for a future release of rights the licensor controls is implicit; no terms-change clause is needed. Keep only the neutral release-scope sentence, preserving earlier grants and MIT cutoffs.

## Clause lineage for counsel

| Lattice clause | Public family structure mirrored; deliberate tailoring |
| --- | --- |
| Definitions / Grant | JetBrains User §§2–3 and Toolbox §§2–3; Obsidian License and free-use overview. Lattice permits personal and commercial use without subscriptions or per-user fees. |
| Restrictions | Obsidian License/Content and Ownership; JetBrains User §3.5 and Toolbox §3.2(B). Lattice keeps standard copy-transfer/notice controls and limits reverse engineering with legal/component exceptions. |
| Ownership | Obsidian Content and Ownership/Your content; JetBrains User §§4.1–4.2 and Toolbox §3.5. Lattice retains code rights and disclaims ownership of user outputs. |
| Third-party software | JetBrains User §4.4 and Toolbox §8 distinguish component terms; Lattice adds the explicit LGPL/OCCT relink/debug override. Obsidian's Third Party Services provisions concern integrations, not this bundled-library carve-out. |
| Release scope / updates | Obsidian Acceptance amendments and JetBrains User §§3.4/10.3 were reviewed. Lattice uses release-local terms; it does not import continued-use amendments, notification/account machinery or service-update promises. |
| Termination | Obsidian Term and Termination; JetBrains User §8. Lattice uses a short written-breach notice clause; counsel should assess cure rights rather than assume the vendors' periods apply. |
| Warranty / Liability | Obsidian Disclaimer of Warranties/Limitations of Liability; JetBrains User §§6–7/10.9 and Toolbox §§10–11. Lattice keeps mandatory-law protections and its own cap. |
| Commercial contact / law | Obsidian's separate Access Agreements and JetBrains subscriptions/contact/legal provisions illustrate separate arrangements. Lattice's required permission and placeholders are original business choices; Obsidian's optional commercial support is different. |

## Other realistic families

Every family requires separate compliance with bundled-component terms; first-party restrictions cannot narrow those rights. Future owned releases can use new terms, but existing grants and promised conversions remain binding under their terms.

| Family | Fit for the owner intent; binary use and principal risk |
| --- | --- |
| Proprietary freeware/binary EULA | Recommended: free personal/commercial use with standard copy-transfer restrictions; natural binary-only fit. Familiar vendor family, with original provisions requiring counsel review. |
| [Elastic License 2.0](https://www.elastic.co/licensing/elastic-license/) | Free use and redistribution; adds a hosted/managed-service restriction. Binary-compatible and recognisable from Elastic, but permits redistribution and imposes an unwanted service limitation. |
| [FSL 1.1](https://fsl.software/) | Free non-competing use and redistribution; Apache/MIT conversion after two years. Standardised fair-source family, source-oriented rather than a binary EULA; permits redistribution and adds unwanted competition limits. |
| [Business Source License 1.1](https://mariadb.com/bsl11/) | Non-production default needs an additional production grant; redistribution allowed; conversion within four years. MariaDB-origin source-oriented family; not the desired binary-only/free-commercial-use policy. |
| [PolyForm Internal Use](https://polyformproject.org/licenses/internal-use/1.0.0) | Internal business use and modifications, no distribution; binary use possible. Specialist standard with a narrower permitted-purpose grant; modified text must lose PolyForm branding. |
| [PolyForm Noncommercial](https://polyformproject.org/licenses/noncommercial/1.0.0) / [Shield](https://polyformproject.org/licenses/shield/1.0.0) | Binary use possible; both grant redistribution. Noncommercial excludes commercial use; Shield adds unwanted competition restrictions. Specialist standards with the wrong permission boundaries. |
| [SSPL](https://www.mongodb.com/legal/licensing/server-side-public-license) / [Commons Clause](https://commonsclause.com/) | SSPL allows service provision with extensive source disclosure, defeating closed binary-only distribution. Commons Clause also restricts paid service/support activities while allowing free redistribution. Recognisable but mismatched; its disclaimer depends on the base licence. |
| [MIT](https://opensource.org/license/mit) / [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) plus trademark/service terms | Familiar, binary-compatible, permitting commercial use, redistribution and sale. Trademark/service contracts cannot withdraw those software grants; no fit for a nonredistributable binary. |

## Deployment boundary and README footer

Preserve each existing MIT cutoff and per-release LICENSE; change no old grant or release asset. This is a draft only, with no product-repo publishing.
The override covers [LGPL-2.1](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html), [OCCT's exception](https://github.com/Open-Cascade-SAS/OCCT/blob/master/OCCT_LGPL_EXCEPTION.txt), applicable [GCC runtime exceptions](https://www.gnu.org/licenses/gcc-exception-3.1.html) and other components; it does not replace required source, objects, notices or relinking materials for both architectures.
A later approved rollout must update future-facing Personal Use labels without moving MIT cutoffs. Copy this footer while retaining the product's separate cutoff sentence:
```markdown
Binaries are free for personal and commercial use under [Lattice Systems Binary License 1.0](LICENSE), as-is, with redistribution, sublicensing, sale, rental, leasing and lending requiring separate written permission; examples/docs and third-party components retain their own licences.
```

## First five lawyer review priorities

1. Grant/Redistribution definitions, copy-transfer restrictions, staff copies, outputs and acceptance/enforceability.
2. Third-party compatibility, LGPL relinking/debugging, OCCT exceptions and required source/object delivery.
3. Release scope, immutable MIT grants and ownership/contributor authority; future-release choice remains implicit.
4. Warranty, USD 50 cap, mandatory protections and breach notice/cure.
5. Governing law and licensor/contact identification: resolve `[JURISDICTION]` and `[BUSINESS CONTACT]`.

This is a model-drafted template and technical comparison, not legal advice; obtain qualified legal review before adopting or distributing it.
