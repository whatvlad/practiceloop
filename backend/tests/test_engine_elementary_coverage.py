"""The source audit links delivered computations without claiming deferred work."""

import json
from pathlib import Path

from app.engine.generators.elementary import generators


def test_source_components_link_exactly_the_delivered_versions_and_keep_deferrals():
    index = json.loads(
        (Path(__file__).parents[2] / "docs/architecture/analysis_pdf_source_index.json").read_text(
            encoding="utf-8"
        )
    )
    versions = {generator.version for generator in generators()}
    delivery = index["deliveries"]["235"]
    assert set(delivery["generator_versions"]) == versions
    assert len(index["items"]) == 830
    assert len(index["family_contracts"]) == 146
    references, components, linked = [], [], set()
    for row in index["items"]:
        delivered = [component for component in row["components"] if component["issue"] == 235]
        if not delivered:
            continue
        references.append(row["id"])
        for component in delivered:
            components.append(component)
            assert component["status"] == "implemented-mathematically-verified"
            assert component["verified_versions"]
            assert set(component["verified_versions"]) <= versions
            linked.update(component["verified_versions"])
        for component in row["components"]:
            if component["issue"] != 235:
                # Another Issue may deliver its own part of a mixed row (#259), never with
                # the versions delivered here.
                assert component["issue"] != 244 or "status" not in component
                assert versions.isdisjoint(component.get("verified_versions", ()))
        if any(component["issue"] not in {235, 244} for component in row["components"]):
            assert row["coverage"] == "partial"
    # Two extra bounded variants extend a source family without claiming a PDF row.
    assert linked | set(delivery["additional_family_variants"]) == versions
    assert linked.isdisjoint(delivery["additional_family_variants"])
    assert len(references) == delivery["source_references"] == 102
    assert len(components) == delivery["computational_components"] == 102
    contracts = [
        contract
        for contract in index["family_contracts"].values()
        if contract.get("delivery", {}).get("issue") == 235
    ]
    assert len(contracts) == delivery["family_contracts"] == 20
    assert set().union(*(set(contract["verified_versions"]) for contract in contracts)) == versions


def test_local_computational_audit_matches_the_registry_and_golden_fixture():
    from app.engine.generators.catalogue import registry

    root = Path(__file__).parents[2]
    index = json.loads(
        (root / "docs/architecture/analysis_pdf_source_index.json").read_text(encoding="utf-8")
    )
    fixtures = json.loads(
        (root / "backend/tests/fixtures/engine_golden_v1.json").read_text(encoding="utf-8")
    )
    deliveries = index["deliveries"]
    audit = deliveries["232"]
    components = [component for row in index["items"] for component in row["components"]]
    verified = [
        component
        for component in components
        if component.get("status") == "implemented-mathematically-verified"
        and 235 <= component["issue"] <= 242
    ]
    assert all(component["verified_versions"] for component in verified)
    linked = {version for component in verified for version in component["verified_versions"]}
    parents = [deliveries[str(issue)] for issue in range(235, 243)]
    versions = {version for delivery in parents for version in delivery["generator_versions"]}
    extras = {
        version
        for delivery in parents
        for version in delivery.get("additional_family_variants", ())
    }
    assert linked.isdisjoint(extras)
    assert linked | extras == versions
    assert versions <= set(registry().versions())
    assert all(len(fixtures[version]) == 3 for version in versions)
    assert audit["verified_generator_count"] == len(versions)
    assert audit["computational_components"] == len(verified)
    assert not audit["pending_source_references"]
    assert (
        sum(component["issue"] == 244 for component in components)
        == audit["deferred_learner_components"]
    )
