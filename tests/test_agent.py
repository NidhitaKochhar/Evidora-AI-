from evidora.agent import _query_plan

def test_query_plan_keeps_original_and_keyword_query():
    plan = _query_plan("Which vital signs are used for sepsis prediction?")
    assert plan[0] == "Which vital signs are used for sepsis prediction?"
    assert len(plan) <= 2
    assert any("sepsis" in q.lower() for q in plan)
