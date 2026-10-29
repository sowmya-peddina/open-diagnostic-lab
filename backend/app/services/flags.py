from __future__ import annotations


def compute_flag(
    value_text: str,
    reference_min: float | None,
    reference_max: float | None,
) -> tuple[float | None, str]:
    """Parse numeric value when possible and return (numeric, flag)."""
    numeric: float | None = None
    text = (value_text or "").strip()
    if text:
        try:
            numeric = float(text.replace(",", ""))
        except ValueError:
            numeric = None

    flag = ""
    if numeric is not None:
        if reference_max is not None and numeric > reference_max:
            flag = "H"
        elif reference_min is not None and numeric < reference_min:
            flag = "L"
    return numeric, flag
