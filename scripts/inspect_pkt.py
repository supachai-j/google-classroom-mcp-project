"""Inspect a Cisco Packet Tracer .pkt/.pkz file — decrypts and extracts device configs.

Uses Unpacket (github.com/Punkcake21/Unpacket) — pure-Python decryptor in scripts/lib/Decipher/.

Usage:
    python scripts/inspect_pkt.py <file.pkt>           # summary
    python scripts/inspect_pkt.py <file.pkt> --config  # full IOS config per device
    python scripts/inspect_pkt.py <file.pkz>           # handles compressed pkz
"""
from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
import zipfile
import io
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
from Decipher.pt_crypto import decrypt_pkt  # type: ignore


def load_pkt_bytes(path: Path) -> bytes:
    """Return raw .pkt bytes, handling .pkz (zip) and .pka transparently."""
    data = path.read_bytes()
    if path.suffix.lower() == ".pkz":
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            inner = next((n for n in z.namelist() if n.endswith((".pkt", ".pka"))), None)
            if not inner:
                raise ValueError(f"{path.name}: pkz contains no .pkt/.pka")
            return z.read(inner)
    return data


def decrypt_to_xml(pkt_bytes: bytes) -> ET.Element:
    xml_bytes = decrypt_pkt(pkt_bytes)
    try:
        return ET.fromstring(xml_bytes)
    except ET.ParseError:
        # Fallback to lxml recover mode for malformed .pka activity files
        from lxml import etree as _letree
        parser = _letree.XMLParser(recover=True, huge_tree=True)
        lroot = _letree.fromstring(xml_bytes, parser=parser)
        cleaned = _letree.tostring(lroot)
        return ET.fromstring(cleaned)


def extract_devices(root: ET.Element) -> list[dict]:
    """Return [{name, model, type, config_lines}] for each network device."""
    devices = []
    for dev in root.iter("DEVICE"):
        engine = dev.find("ENGINE")
        if engine is None:
            continue
        type_el = engine.find("TYPE")
        name_el = engine.find("NAME")
        if name_el is None or not name_el.text:
            continue
        # Collect <LINE> elements (IOS config lines)
        lines = [l.text for l in dev.iter("LINE") if l.text]
        if not lines:
            continue  # skip non-config devices (PCs, hubs, etc.)
        devices.append({
            "name": name_el.text,
            "type": (type_el.text if type_el is not None else "?"),
            "model": type_el.get("customModel", "?") if type_el is not None else "?",
            "config_lines": lines,
        })
    return devices


def summarize(devices: list[dict]) -> str:
    out = []
    out.append(f"# Topology — {len(devices)} configured device(s)\n")
    for d in devices:
        cfg = d["config_lines"]
        # quick heuristics for what's configured
        vlans = sorted({
            l.split()[-1] for l in cfg
            if ("switchport access vlan " in l or l.lstrip().startswith("vlan "))
            and l.split() and l.split()[-1].isdigit()
        }, key=int)
        interfaces = [l for l in cfg if l.startswith("interface ")]
        has_routing = any(l.startswith(("router ospf", "router rip", "router eigrp", "router bgp", "ip route ")) for l in cfg)
        has_acl = any(l.startswith(("access-list ", "ip access-list ")) for l in cfg)
        has_nat = any("ip nat" in l for l in cfg)
        has_dhcp = any("ip dhcp" in l for l in cfg)
        has_ipv6 = any("ipv6 " in l for l in cfg)
        has_stp = any("spanning-tree " in l for l in cfg)
        has_channel = any("channel-group" in l for l in cfg)
        flags = []
        if vlans: flags.append(f"VLANs={','.join(vlans)}")
        if has_routing: flags.append("Routing")
        if has_acl: flags.append("ACL")
        if has_nat: flags.append("NAT")
        if has_dhcp: flags.append("DHCP")
        if has_ipv6: flags.append("IPv6")
        if has_stp: flags.append("STP")
        if has_channel: flags.append("EtherChannel")
        out.append(f"## {d['name']}  [{d['model']}]")
        out.append(f"   Interfaces: {len(interfaces)}, Config lines: {len(cfg)}")
        if flags:
            out.append(f"   Configured: {' · '.join(flags)}")
        out.append("")
    return "\n".join(out)


def full_configs(devices: list[dict]) -> str:
    out = []
    for d in devices:
        out.append(f"\n{'='*60}\n{d['name']}  [{d['model']}]\n{'='*60}")
        out.append("\n".join(d["config_lines"]))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("path", help=".pkt / .pkz / .pka file path")
    ap.add_argument("--config", action="store_true", help="dump full IOS running-config per device")
    args = ap.parse_args()

    path = Path(args.path)
    if not path.exists():
        sys.exit(f"file not found: {path}")

    pkt = load_pkt_bytes(path)
    root = decrypt_to_xml(pkt)
    devices = extract_devices(root)

    print(summarize(devices))
    if args.config:
        print(full_configs(devices))


if __name__ == "__main__":
    main()
