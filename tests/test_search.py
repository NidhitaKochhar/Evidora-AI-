from evidora.search import tokens

def test_tokens():
    assert "mimic-iv" in tokens("The MIMIC-IV dataset")
