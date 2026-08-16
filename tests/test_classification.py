from board.classification import classify_text, looks_like_early_career, is_relevant


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


def test_area_manager_is_operations():
    result = classify_text("Area Manager Intern - Summer 2027")
    assert result.category == "Operations"
