def evidence_prefixes(client, claim):
    detail = {
        "claim": {
            "claim_id": "TEST",
            "prior_auth_required": False,
            "prior_auth_present": True,
            "missing_required_auth": False,
            "provider_network": "in_network",
            "coding_mismatch_flag": False,
            "timely_filing_flag": False,
            "duplicate_claim_flag": False,
            "documentation_complete": True,
            **claim,
        },
        "prediction": {"top_factors": []},
    }
    result = client.app.state.retrieval_service.evidence_for_claim(detail, top_k=5)
    return [source["source_id"].split(":")[0] for source in result["sources"]]


def test_missing_auth_retrieves_prior_authorization(client):
    prefixes = evidence_prefixes(client, {"prior_auth_required": True, "prior_auth_present": False, "missing_required_auth": True})
    assert "prior_authorization" in prefixes


def test_timely_filing_false_retrieves_timely_policy(client):
    prefixes = evidence_prefixes(client, {"timely_filing_flag": False})
    assert "timely_filing" in prefixes


def test_out_of_network_retrieves_network_policy(client):
    prefixes = evidence_prefixes(client, {"provider_network": "out_of_network"})
    assert "network_coverage" in prefixes


def test_coding_mismatch_retrieves_coding_policy(client):
    prefixes = evidence_prefixes(client, {"coding_mismatch_flag": True})
    assert "coding_guidelines" in prefixes


def test_duplicate_claim_retrieves_duplicate_policy(client):
    prefixes = evidence_prefixes(client, {"duplicate_claim_flag": True})
    assert "duplicate_claims" in prefixes
