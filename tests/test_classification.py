from board.classification import classify_text, looks_like_early_career, is_relevant, excluded_track_title


def test_supply_chain():
    result = classify_text("Demand Planning Intern")
    assert result.category == "Supply Chain"
    assert result.confidence > 0.3


def test_operations():
    result = classify_text("Business Operations Intern")
    assert result.category == "Operations"


def test_product():
    result = classify_text("Associate Product Manager Intern")
    assert result.category == "Product Management"


def test_procurement():
    result = classify_text("Strategic Sourcing Intern")
    assert result.category == "Procurement & Sourcing"


def test_logistics():
    result = classify_text("Logistics Intern, Transportation Planning")
    assert result.category == "Logistics"


def test_analytics():
    result = classify_text("Business Analytics Intern")
    assert result.category == "Business Analytics"


def test_finance_sales_marketing_are_dropped():
    assert excluded_track_title("Financial Analyst Intern")
    assert excluded_track_title("Brand Marketing Intern")
    assert excluded_track_title("Sales Intern")
    assert excluded_track_title("2027 Amazon Operations Finance Rotational Program Summer Internship")
    assert excluded_track_title("Marketing Intern, Amazon Global Logistics")
    assert excluded_track_title("Sales Ops Analyst Intern - Shanghai, Amazon Global Selling")
    assert not is_relevant("Financial Analyst Intern", "", "Other")
    assert not is_relevant("Brand Marketing Intern", "", "Other")
    assert not is_relevant("Sales Intern", "", "Other")
    assert not excluded_track_title("Sales and Operations Planning Intern")
    assert not excluded_track_title("Supply Chain Intern")


def test_low_confidence_goes_to_other():
    result = classify_text("Brand Ambassador")
    assert result.category == "Other"
    assert result.needs_review


def test_title_outweighs_description():
    result = classify_text(
        "Product Manager Intern",
        "You will work with the supply chain team on inventory reports.",
    )
    assert result.category == "Product Management"


def test_description_alone_does_not_classify_engineering():
    result = classify_text(
        "Software Engineer Intern",
        "Help customers optimize their global supply chain and logistics network.",
    )
    assert result.category == "Other"


def test_early_career_detection():
    assert looks_like_early_career("Supply Chain Intern")
    assert looks_like_early_career("Operations Co-op")
    assert looks_like_early_career("Associate Product Manager, New Grad")
    assert not looks_like_early_career("Director of Supply Chain")
    assert not looks_like_early_career("Internal Auditor")
    assert not looks_like_early_career("Early Career Experience Program Manager")


def test_engineering_roles_are_not_kept_from_description():
    assert not is_relevant(
        "Software Engineer Intern",
        "Work on supply chain optimization software.",
        "Other",
    )
    assert not is_relevant(
        "Software Engineer Project Intern - Security",
        "",
        "Project & Program Management",
    )
    assert not is_relevant("Frontend Software Engineer Project Intern - Global CRM", "", "Other")
    assert not is_relevant("Data Analyst Intern", "", "Business Analytics")
    assert is_relevant("Business Analytics Intern", "", "Business Analytics")
    assert not is_relevant("Generative AI Implementation Intern", "", "Other")
    assert is_relevant(
        "Data Science Intern - Tiktok Shop - Supply Chain & Logistics",
        "",
        "Supply Chain",
    )


def test_area_manager_is_operations():
    result = classify_text("Area Manager Intern - Summer 2027")
    assert result.category == "Operations"
