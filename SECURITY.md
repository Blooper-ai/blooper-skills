# Security Policy

## Reporting a vulnerability

If you discover a security issue in a skill's tool code, in `scripts/`, or in the registry pipeline, please report it privately. Do NOT open a public GitHub issue.

Email **security@blooper.ai** with:

- A description of the issue.
- Steps to reproduce.
- The affected skill slug or file path.
- (Optional) your name/handle for credit.

We aim to:

- Acknowledge your report within **2 business days**.
- Provide an initial assessment within **5 business days**.
- Coordinate a fix and public disclosure within **90 days** of the initial report.

## Scope

In scope:

- Tool code under `skills/*/tools/` that could leak credentials, exfiltrate data, or escape the runtime sandbox.
- Manifests crafted to bypass `applies_to`, `budget`, or `permissions` enforcement.
- Vulnerabilities in `scripts/validate.py`, `scripts/build_registry.py`, or the CI workflows that could allow malicious skills to land on `main`.

Out of scope:

- Issues in the Blooper app or platform runtime itself. Report those to security@blooper.ai too, but mention they are platform-side.
- Denial-of-service against the GitHub repo (e.g. spam PRs).
- Theoretical attacks that require already-compromised maintainer credentials.

## Safe harbor

We will not pursue legal action against researchers who:

- Make a good-faith effort to follow this policy.
- Avoid privacy violations, destruction of data, and interruption of service.
- Give us reasonable time to fix the issue before any public disclosure.

Thanks for helping keep Blooper skills safe.
