from __future__ import annotations

from evals.run_eval import KeywordJudge, cohens_kappa, run, spearman


def test_metrics() -> None:
    assert spearman([1, 2, 3, 4], [10, 20, 30, 40]) == 1.0 and spearman([1, 2, 3, 4], [40, 30, 20, 10]) == -1.0
    assert abs(spearman([1, 2, 2, 4], [1, 3, 2, 4])) > 0.7
    assert cohens_kappa([True, False, True, False], [True, False, True, False]) == 1.0
    assert KeywordJudge().judge("Builds dropped from 41 to 6 minutes.", {"bullets": ["41 to 6 minutes"]}) and not KeywordJudge().judge("x", {"bullets": ["downloaded 2 million times"]})


def test_offline_harness_runs_all_four_parts() -> None:
    results = run(offline=True)
    assert set(results) == {"relevance", "faithfulness", "grouping", "injection"}
    assert results["relevance"]["n"] == 14 and 0 <= results["relevance"]["precision_at_8"] <= 1
    assert results["faithfulness"]["n"] == 6 and results["faithfulness"]["agreement"] >= 0.8
    assert results["grouping"]["precision"] == 1.0 and results["grouping"]["recall"] == 1.0
    # offline, the fake "model" copies article sentences verbatim, so poisoned sentences leak: the injection part only
    # proves the harness plumbing here. The live run (`make eval`) is the real test, and its threshold is 1.0.
    assert results["injection"]["n"] == 5 and 0.0 <= results["injection"]["pass_rate"] <= 1.0
    assert all(f.split(":")[0].startswith("i0") for f in results["injection"]["failures"])
