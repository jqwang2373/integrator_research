#!/usr/bin/env python3
"""Validate the CMAME reference metadata audit."""

from __future__ import annotations

import json
from pathlib import Path


PAPER = Path(__file__).resolve().parent


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(PAPER / "REFERENCE_METADATA_AUDIT.json")
        md = (PAPER / "REFERENCE_METADATA_AUDIT.md").read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 - CLI validator reports parse/read failures.
        print(f"reference metadata audit validation: FAIL\n- {exc}")
        return 1

    rows = audit.get("rows", [])
    doi_rows = [row for row in rows if row.get("local_has_doi") is True]
    verified_doi_rows = [row for row in rows if row.get("status") == "doi_metadata_verified"]
    local_no_doi_rows = [row for row in rows if row.get("local_has_doi") is False]
    verified_no_doi_rows = [row for row in local_no_doi_rows if row.get("verified") is True]
    open_no_doi_rows = [row for row in local_no_doi_rows if row.get("verified") is not True]
    unresolved_doi_rows = [row for row in rows if row.get("status") == "doi_metadata_unresolved"]

    checks.check(audit.get("schema") == "reference-metadata-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "all_reference_metadata_web_verified",
        "audit status changed",
    )
    checks.check(audit.get("reference_count") == len(rows) == 28, "reference count changed")
    checks.check(audit.get("doi_reference_count") == len(doi_rows) == 16, "DOI reference count changed")
    checks.check(
        audit.get("doi_metadata_verified_count") == len(verified_doi_rows) == 16,
        "verified DOI metadata count changed",
    )
    checks.check(
        audit.get("doi_metadata_unresolved_count") == len(unresolved_doi_rows) == 0,
        "DOI metadata unresolved count changed",
    )
    checks.check(
        audit.get("local_non_doi_reference_count") == len(local_no_doi_rows) == 12,
        "local non-DOI count changed",
    )
    checks.check(
        audit.get("non_doi_metadata_verified_count") == len(verified_no_doi_rows) == 12,
        "verified non-DOI metadata count changed",
    )
    checks.check(
        audit.get("non_doi_reference_count") == len(open_no_doi_rows) == 0,
        "open non-DOI count changed",
    )
    checks.check(
        audit.get("external_reference_web_verification_complete") is True,
        "external reference web verification should be closed",
    )
    checks.check(
        audit.get("bibliographic_metadata_web_verified") is True,
        "bibliographic metadata verification should be globally closed",
    )
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission ready")
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "audit must not invoke run_v047")
    checks.check(audit.get("heavy_numerical_run_invoked") is False, "audit must not invoke heavy runs")

    required_dois = {
        "10.1007/s11044-026-10153-w",
        "10.1115/1.4036821",
        "10.1016/0377-0427(85)90008-1",
        "10.1016/j.mechmachtheory.2011.07.017",
        "10.1016/j.cam.2019.112517",
        "10.1007/s11044-016-9518-7",
        "10.1115/1.4056183",
        "10.1115/1.4065254",
        "10.1137/0733019",
        "10.1017/S096249290100006X",
        "10.1002/zamm.200700173",
        "10.1093/imanum/drr042",
        "10.1002/(SICI)1097-0207(19960815)39:15<2673::AID-NME972>3.0.CO;2-I",
        "10.1023/A:1008292328909",
        "10.1016/j.cma.2010.06.030",
        "10.1115/1.4063953",
    }
    checks.check({row.get("doi") for row in doi_rows} == required_dois, "DOI set changed")
    for row in verified_doi_rows:
        checks.check(row.get("source") == "Crossref", f"{row.get('key')} source is not Crossref")
        checks.check(bool(row.get("source_url")), f"{row.get('key')} missing source URL")
        checks.check(bool(row.get("crossref_title")), f"{row.get('key')} missing Crossref title")
        checks.check(row.get("verified") is True, f"{row.get('key')} not marked verified")
    for row in local_no_doi_rows:
        checks.check(row.get("doi") == "", f"{row.get('key')} non-DOI row has DOI")
    for row in verified_no_doi_rows:
        checks.check(
            row.get("status") in {"crossref_title_metadata_verified", "manual_external_metadata_verified"},
            f"{row.get('key')} non-DOI row has unexpected verified status",
        )
        checks.check(bool(row.get("source_url")), f"{row.get('key')} verified non-DOI row missing source URL")
        checks.check(
            bool(row.get("crossref_title") or row.get("verified_title")),
            f"{row.get('key')} verified non-DOI row missing title",
        )
        checks.check(row.get("verified") is True, f"{row.get('key')} verified non-DOI row not marked verified")
    for row in open_no_doi_rows:
        checks.check(
            row.get("status") == "open_crossref_title_metadata_unmatched",
            f"{row.get('key')} open non-DOI row has unexpected status",
        )
        checks.check(row.get("verified") is False, f"{row.get('key')} open non-DOI row oververified")

    for token in [
        "Reference Metadata Audit",
        "DOI references verified through Crossref metadata: `16/16`",
        "Local non-DOI references verified through Crossref title search or manual external metadata: `12/12`",
        "Non-DOI references still requiring manual or publisher-page verification: `0`",
        "External reference web verification complete: `True`",
        "ALL REFERENCE METADATA WEB VERIFIED",
    ]:
        checks.check(token in md, f"metadata audit markdown missing token: {token}")

    if checks.errors:
        print("reference metadata audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("reference metadata audit validation: PASS")
    print("doi_metadata_verified=16/16")
    print("non_doi_metadata_verified=12/12")
    print("non_doi_reference_count=0")
    print("external_reference_web_verification_complete=True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
