# ChangeOrderSeal

**Local-first change-order / extra-work authorizer and QuantumGuard evidence sealer for field operators.**

Offline. Deterministic. Pay once. Compatible with QuantumGuard CONTRACT-v1, VeriQuote, FieldSeal, JobSeal, MediaSeal, CloseSeal, LifecycleSeal, and Evidence-Core.

## Why ChangeOrderSeal?

Field operators lose money when clients dispute extra work: "I never authorized that," "the price was different," "that wasn't in the original scope."

ChangeOrderSeal captures the change on-site (description, labor/materials estimate, client acknowledgment, optional media hashes, timestamps), then seals it into a client-verifiable QuantumGuard evidence bundle.

- No SaaS. No subscription. Runs completely offline after key setup.
- Clients (or their auditors) verify the pack with the free QuantumGuard verifier (`qg verify`).
- Pairs with VeriQuote (original quote), FieldSeal / JobSeal (work performed), MediaSeal (photos of the extra work), and Chaser (invoicing the change).
- Produces a clean, signed record of what was authorized before the truck leaves the site.

## Quick Start

```bash
# Optional but recommended for real Ed25519 signatures
pip install cryptography

python3 src/changeorderseal.py --demo
python3 src/changeorderseal.py --order samples/change-001.json --out sealed_change.json
```

Verify the output with the QuantumGuard CLI (from the quantumguard repo):

```bash
qg verify sealed_change.json
```

Expected verdict: PASS (when using real cryptography).

## What you can sell

| SKU       | Price | Includes                                      |
|-----------|-------|-----------------------------------------------|
| Operator  | $79   | CLI + templates + key setup guide + 1-year email support |
| Command   | $199  | + batch mode + HTML acknowledgment form + reseller rights |
| Agency    | $499  | + white-label HTML + design partner onboarding |

Purchase / access: danpennic@gmail.com

Source remains free under Apache-2.0 OR MIT. Commercial Operator Pack sold separately.

## Stack Fit

- Python CLI (same family as VeriQuote, FieldSeal, MediaSeal, JobSeal, CloseSeal, LifecycleSeal)
- Emits QuantumGuard CONTRACT-v1 bundles (Ed25519, deterministic hashing)
- Local key storage (PEM)
- Ready for LifecycleSeal aggregation and Chaser CSV export

## License

Apache-2.0 OR MIT
