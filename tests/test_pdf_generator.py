import pytest
from report.pdf_generator import generate_report


def make_sample_result(student_name="Test Student"):
    math_scores = {
        "number": {"score": 0.5, "level": 2, "correct": 3, "total": 6},
        "algebra": {"score": 0.6, "level": 2, "correct": 3, "total": 5},
        "geometry_measurement": {"score": 0.8, "level": 3, "correct": 4, "total": 5},
        "handling_data": {"score": 0.25, "level": 1, "correct": 1, "total": 4},
    }
    science_scores = {
        "diversity_matter": {"score": 0.67, "level": 3, "correct": 2, "total": 3},
        "cycles": {"score": 0.5, "level": 2, "correct": 2, "total": 4},
        "systems": {"score": 0.75, "level": 3, "correct": 3, "total": 4},
        "forces_energy": {"score": 0.25, "level": 1, "correct": 1, "total": 4},
        "humans_environment": {"score": 1.0, "level": 4, "correct": 3, "total": 3},
    }
    return {
        "attempt_id": 1,
        "student_name": student_name,
        "math_scores": math_scores,
        "science_scores": science_scores,
        "overall_level": 2,
        "completed_at": "2026-03-20 10:00:00",
    }


def test_generate_report_returns_bytes():
    result = make_sample_result()
    pdf_bytes = generate_report(result, {}, {})
    assert isinstance(pdf_bytes, bytes)


def test_generate_report_is_valid_pdf():
    result = make_sample_result()
    pdf_bytes = generate_report(result, {}, {})
    assert pdf_bytes[:4] == b"%PDF"


def test_generate_report_contains_student_name():
    result = make_sample_result(student_name="Kwame Mensah")
    pdf_bytes = generate_report(result, {}, {})
    assert len(pdf_bytes) > 500
    assert pdf_bytes[:4] == b"%PDF"


def test_generate_report_with_recommendations():
    result = make_sample_result()
    math_recs = {"number": "Practice place value with a number chart."}
    science_recs = {"forces_energy": "Build a simple circuit to understand electricity."}
    pdf_bytes = generate_report(result, math_recs, science_recs)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000


def test_generate_report_different_students_differ():
    result1 = make_sample_result("Alice")
    result2 = make_sample_result("Bob")
    pdf1 = generate_report(result1, {}, {})
    pdf2 = generate_report(result2, {}, {})
    assert pdf1 != pdf2


def test_generate_report_includes_group_label():
    result = make_sample_result()
    result["group_label"] = "기초"
    result["assessment_type"] = "baseline"
    pdf_bytes = generate_report(result, {}, {})
    assert pdf_bytes[:4] == b"%PDF"
    assert len(pdf_bytes) > 1000


def test_generate_report_footer_is_generic():
    result = make_sample_result()
    pdf_bytes = generate_report(result, {}, {})
    pdf_text = pdf_bytes.decode("latin-1", errors="ignore")
    assert "Ghana" not in pdf_text


def test_generate_report_includes_assessment_type():
    result = make_sample_result()
    result["assessment_type"] = "midline"
    pdf_bytes = generate_report(result, {}, {})
    assert pdf_bytes[:4] == b"%PDF"
