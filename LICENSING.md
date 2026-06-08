# Licensing policy

The blooper-skills repo itself is Apache-2.0.

**Default plugin license**: when a skill's manifest doesn't declare `license`, Apache-2.0 is applied.

**Accepted plugin licenses** (SPDX identifier):
- Apache-2.0 (default)
- MIT
- BSD-2-Clause
- BSD-3-Clause
- ISC

**Rejected plugin licenses**:
- GPL family (GPL-*, LGPL-*, AGPL-*)
- SSPL-1.0
- Custom non-commercial licenses
- "Source-available" licenses (BSL, Elastic License, etc.)

Skills using a rejected license will fail PR validation. To make your skill installable in the marketplace, choose an SPDX identifier from the accepted list.

## Why

The Blooper platform is open-ecosystem: any project can install any community skill from the marketplace. Permissive licenses are the only way to keep the install experience legally consistent for every user. Copyleft (GPL) and source-available licenses create install-time obligations we can't propagate to users, so they're rejected at the manifest layer.
