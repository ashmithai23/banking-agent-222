"""
VectraBank Benchmark Metrics Engine
Evaluates agent outputs against standard regulatory and computational benchmarks.
"""

def calculate_dti_error(predicted: float, expected: float) -> float:
    """Calculates absolute percentage error for DTI calculations."""
    return abs(predicted - expected)

def verify_aml_compliance(detected_flags: list, expected_flags: list) -> dict:
    """Calculates precision and recall for regulatory AML flags."""
    detected_set = set(detected_flags)
    expected_set = set(expected_flags)
    tp = len(detected_set & expected_set)
    fp = len(detected_set - expected_set)
    fn = len(expected_set - detected_set)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    return {"precision": precision, "recall": recall, "exact_match": detected_set == expected_set}
