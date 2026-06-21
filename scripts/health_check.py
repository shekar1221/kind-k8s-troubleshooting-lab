#!/usr/bin/env python3
"""
Simple Kubernetes service health checker.

Run this from:
1. Inside a debug pod, for ClusterIP service DNS checks.
2. Your laptop, for localhost/NodePort/Ingress checks.

No external Python packages are required.
"""

import argparse
import http.client
import socket
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class Target:
    name: str
    host: str
    port: int
    path: Optional[str] = None


DEFAULT_TARGETS = [
    Target("orders-api", "orders-api.troubleshooting-lab.svc.cluster.local", 80, "/"),
    Target("selector-backend", "selector-backend.troubleshooting-lab.svc.cluster.local", 80, "/"),
    Target("targetport-api", "targetport-api.troubleshooting-lab.svc.cluster.local", 80, "/"),
    Target("payments-db", "payments-db.troubleshooting-lab.svc.cluster.local", 5432, None),
]


def resolve_host(host: str, timeout: float) -> tuple[bool, str]:
    socket.setdefaulttimeout(timeout)
    try:
        records = socket.getaddrinfo(host, None)
        ips = sorted({record[4][0] for record in records})
        return True, ", ".join(ips)
    except socket.gaierror as exc:
        return False, f"DNS failed: {exc}"
    except Exception as exc:
        return False, f"DNS check error: {exc}"


def check_tcp(host: str, port: int, timeout: float) -> tuple[bool, str]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, "TCP connected"
    except Exception as exc:
        return False, f"TCP failed: {exc}"


def check_http(host: str, port: int, path: str, timeout: float) -> tuple[bool, str]:
    try:
        conn = http.client.HTTPConnection(host, port, timeout=timeout)
        conn.request("GET", path)
        response = conn.getresponse()
        response.read()
        conn.close()
        ok = 200 <= response.status < 400
        return ok, f"HTTP {response.status} {response.reason}"
    except Exception as exc:
        return False, f"HTTP failed: {exc}"


def parse_target(value: str) -> Target:
    parts = value.split(":")
    if len(parts) < 3:
        raise argparse.ArgumentTypeError(
            "target must be name:host:port or name:host:port:path"
        )
    name = parts[0]
    host = parts[1]
    try:
        port = int(parts[2])
    except ValueError as exc:
        raise argparse.ArgumentTypeError("port must be a number") from exc
    path = parts[3] if len(parts) > 3 else None
    return Target(name=name, host=host, port=port, path=path)


def print_result(label: str, ok: bool, detail: str) -> None:
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {label}: {detail}")


def run_target(target: Target, timeout: float) -> bool:
    print(f"\n== {target.name} ==")
    print(f"host={target.host} port={target.port} path={target.path or '-'}")

    dns_ok, dns_detail = resolve_host(target.host, timeout)
    print_result("DNS", dns_ok, dns_detail)
    if not dns_ok:
        return False

    tcp_ok, tcp_detail = check_tcp(target.host, target.port, timeout)
    print_result("TCP", tcp_ok, tcp_detail)
    if not tcp_ok:
        return False

    if target.path:
        http_ok, http_detail = check_http(target.host, target.port, target.path, timeout)
        print_result("HTTP", http_ok, http_detail)
        return http_ok

    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Kubernetes service health.")
    parser.add_argument(
        "--target",
        action="append",
        type=parse_target,
        help="Custom target: name:host:port or name:host:port:path",
    )
    parser.add_argument("--timeout", type=float, default=3.0, help="Timeout in seconds")
    args = parser.parse_args()

    targets = args.target if args.target else DEFAULT_TARGETS
    failed = 0
    for target in targets:
        if not run_target(target, args.timeout):
            failed += 1

    print("\nSummary")
    print(f"checked={len(targets)} failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

