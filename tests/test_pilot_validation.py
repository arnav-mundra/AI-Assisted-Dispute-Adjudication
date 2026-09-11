from src.validation.validate_pilot import validate

def test_pilot_dataset_is_valid():
    errors = validate()
    assert errors == [], "\n".join(errors)