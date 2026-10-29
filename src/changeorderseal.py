#!/usr/bin/env python3
"""
ChangeOrderSeal — local-first change-order / extra-work authorizer and QuantumGuard sealer.
Compatible with QuantumGuard CONTRACT-v1 and the Operator Pages suite.
Offline after key setup. Deterministic payload hashing.
"""
import argparse
import json
import hashlib
import base64
from datetime import datetime, timezone
from pathlib import Path

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Note: cryptography not installed. Using stub signatures. pip install cryptography for real Ed25519.")

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load_or_create_key(key_path: Path):
    """Returns (private_key_or_None, public_key_hex)"""
    if not CRYPTO_AVAILABLE:
        return None, "00" * 32
    if key_path.exists():
        with open(key_path, "rb") as f:
            priv = serialization.load_pem_private_key(f.read(), password=None)
        pub = priv.public_key()
        pub_bytes = pub.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        return priv, pub_bytes.hex()
    else:
        priv = Ed25519PrivateKey.generate()
        pub = priv.public_key()
        pub_bytes = pub.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        pem = priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        key_path.write_bytes(pem)
        return priv, pub_bytes.hex()

def sign_payload(priv, payload_hash_hex: str) -> str:
    if not CRYPTO_AVAILABLE or priv is None:
        return "00" * 64
    hash_bytes = bytes.fromhex(payload_hash_hex)
    sig = priv.sign(hash_bytes)
    return sig.hex()

def build_evidence_pack(order: dict, priv, pub_hex: str) -> dict:
    payload_obj = {
        "version": "1",
        "type": "change_order",
        "change_id": order.get("change_id", "unknown"),
        "job_id": order.get("job_id", ""),
        "client": order.get("client", ""),
        "location": order.get("location", ""),
        "description": order.get("description", ""),
        "reason": order.get("reason", ""),
        "labor_hours": order.get("labor_hours"),
        "labor_rate": order.get("labor_rate"),
        "materials": order.get("materials", []),
        "materials_total": order.get("materials_total"),
        "estimated_total": order.get("estimated_total"),
        "client_acknowledged": order.get("client_acknowledged", False),
        "client_name": order.get("client_name", ""),
        "client_signature_note": order.get("client_signature_note", ""),
        "media_hashes": order.get("media_hashes", []),
        "operator": order.get("operator", "field-tech"),
        "authorized_at": order.get("authorized_at", datetime.now(timezone.utc).isoformat()),
        "notes": order.get("notes", "")
    }
    payload_bytes = json.dumps(payload_obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.b64encode(payload_bytes).decode("ascii")
    payload_hash = sha256_hex(payload_bytes)
    signature = sign_payload(priv, payload_hash)

    pack = {
        "version": "1",
        "payload": payload_b64,
        "payload_hash": payload_hash,
        "signature": signature,
        "public_key": pub_hex,
        "alg": "ed25519"
    }
    return pack

def demo():
    sample = {
        "change_id": "CO-2026-014",
        "job_id": "JOB-2026-042",
        "client": "Acme Property Management",
        "location": "123 Main St, Springfield MO",
        "description": "Replace failed contactor and add surge protection on rooftop unit RTU-3",
        "reason": "Contactor failed during original capacitor service; surge protection recommended after voltage event",
        "labor_hours": 1.5,
        "labor_rate": 125.0,
        "materials": [
            {"item": "Contactor 40A", "qty": 1, "unit_cost": 48.0},
            {"item": "Surge protector", "qty": 1, "unit_cost": 89.0}
        ],
        "materials_total": 137.0,
        "estimated_total": 324.5,
        "client_acknowledged": True,
        "client_name": "Jordan Lee",
        "client_signature_note": "Verbal + photo of signed paper ticket",
        "media_hashes": ["a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"],
        "operator": "tech-dan",
        "notes": "Client approved on-site before parts ordered."
    }
    key_path = Path.home() / ".changeorderseal_key.pem"
    priv, pub_hex = load_or_create_key(key_path)
    pack = build_evidence_pack(sample, priv, pub_hex)
    print(json.dumps(pack, indent=2))
    print("\n# Verify with: qg verify <this.json>  (from QuantumGuard)")

def main():
    parser = argparse.ArgumentParser(description="ChangeOrderSeal — local change-order evidence sealer")
    parser.add_argument("--demo", action="store_true", help="Run demo and print sealed pack")
    parser.add_argument("--order", type=str, help="Path to change-order JSON file")
    parser.add_argument("--out", type=str, help="Output sealed pack path")
    parser.add_argument("--key", type=str, default=str(Path.home() / ".changeorderseal_key.pem"), help="Private key path")
    args = parser.parse_args()

    if args.demo:
        demo()
        return

    if not args.order:
        parser.print_help()
        return

    with open(args.order) as f:
        order = json.load(f)

    key_path = Path(args.key)
    priv, pub_hex = load_or_create_key(key_path)
    pack = build_evidence_pack(order, priv, pub_hex)

    out_path = args.out or f"sealed_change_{order.get('change_id', 'unknown')}.json"
    with open(out_path, "w") as f:
        json.dump(pack, f, indent=2)
    print(f"Sealed change order written to {out_path}")
    print(f"Payload hash: {pack['payload_hash']}")
    print("Verify with QuantumGuard: qg verify", out_path)

if __name__ == "__main__":
    main()
