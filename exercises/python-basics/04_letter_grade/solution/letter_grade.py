def letter_grade(score: float) -> str:
    """Return "A", "B", "C", "D" or "F" for a score from 0 to 100.

    90 and up is A, 80 and up is B, 70 and up is C, 60 and up is D, below 60 is F.
    Scores below 0 or above 100 return "Invalid score".
    """
    if score < 0 or score > 100:
        return "Invalid score"
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"
