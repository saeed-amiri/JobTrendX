"""
Testing the payload_analysis module
"""
# pylint: disable=redefined-outer-name

import pandas as pd

from jobtrendx.payload_analysis import _get_sections, _split_by_lang, \
    _split_double_newline


def test_get_sections_de() -> None:
    """test if detect de sections correctly"""
    sections_de = {
        "job_title": "Beliebter Job",
        "company": "Wer wir sind.",
        "requirements": "Das bringst du mit",
        "benefits": "Das bieten wir dir"
        }

    payload_text = """Beliebter Job
        Data Scientist (m/w/d) Schwerpunkt KI

        PreZero Service Deutschland GmbH & Co. KG
        Wesseling bei Köln 
        10,001+ Mitarbeiter
        Feste Anstellung
        Vollzeit, Homeoffice möglich
        66.000 - 90.000 €/Jahr (geschätzt für Vollzeit)

        Wer wir sind.
        PreZero ist ein innovatives Unternehmen...

        Das bringst du mit
        Du bringst ein abgeschlossenes Studium im Bereich Informatik...

        Das bieten wir dir
        Als Teil der Schwarz Gruppe...
        """
    sections: dict[str, str] = _get_sections(payload_text, sections_de)
    assert sections["job_title"] == (
        'Data Scientist (m/w/d) Schwerpunkt KI\n\n        PreZero Service '
        'Deutschland GmbH & Co. KG\n        Wesseling bei Köln \n        '
        '10,001+ Mitarbeiter\n        Feste Anstellung\n        Vollzeit, '
        'Homeoffice möglich\n        66.000 - 90.000 €/Jahr (geschätzt für '
        'Vollzeit)\n')
    assert sections["company"] == \
        'PreZero ist ein innovatives Unternehmen...\n'
    assert sections["requirements"] == \
        'Du bringst ein abgeschlossenes Studium im Bereich Informatik...\n'
    assert sections["benefits"] == 'Als Teil der Schwarz Gruppe...\n'


def test_get_sections_en() -> None:
    """
    Test if the function correctly detects and extracts sections in English.
    """
    sections_en = {
        "job_title": "Top Match",
        "company": "Who we are",
        "requirements": "Your knowledge/experience",
        "benefits": "We offer"
    }

    payload_text = """Top Match
        Data Scientist (m/f/d) AI Specialist

        Lloyds Bank - Bank of Scotland
        Berlin
        251-500 employees
        Permanent position
        Full-time, Part-time, Remote possible
        Estimated Salary: $80,000 - $110,000 per year

        Who we are
        Lloyds Bank GmbH and its brands Bank of Scotland and Lloyds Bank
        have won over 1 million satisfied customers in recent years...

        Your knowledge/experience
        Educated to a degree level in Computer Science, Data Science...

        We offer
        An inclusive and diverse work environment...
    """

    sections: dict[str, str] = _get_sections(payload_text, sections_en)

    assert sections['job_title'] == (
        'Data Scientist (m/f/d) AI Specialist\n\n        Lloyds Bank - '
        'Bank of Scotland\n        Berlin\n        251-500 '
        'employees\n        Permanent position\n        Full-time, '
        'Part-time, Remote possible\n        Estimated Salary: '
        '$80,000 - $110,000 per year\n')
    assert sections['company'] == (
        'Lloyds Bank GmbH and its brands Bank of Scotland and Lloyds '
        'Bank\n        have won over 1 million satisfied customers in '
        'recent years...\n')
    assert sections['requirements'] == \
        'Educated to a degree level in Computer Science, Data Science...\n'
    assert sections['benefits'] == \
        'An inclusive and diverse work environment...\n'


def test_split_by_lang() -> None:
    """Test the _split_by_lang function. (Copilt)"""
    data = {
        "file_path": ["file1", "file2", "file3", "file4"],
        "eml_lang": ["en", "de", "en", "de"],
        "payload": ["payload1", "payload2", "payload3", "payload4"]
    }
    df = pd.DataFrame(data)

    expected_en = pd.DataFrame({
        "file_path": ["file1", "file3"],
        "eml_lang": ["en", "en"],
        "payload": ["payload1", "payload3"]
    })

    expected_de = pd.DataFrame({
        "file_path": ["file2", "file4"],
        "eml_lang": ["de", "de"],
        "payload": ["payload2", "payload4"]
    })

    result = _split_by_lang(df)

    assert "en" in result
    assert "de" in result
    pd.testing.assert_frame_equal(
        result["en"].reset_index(drop=True), expected_en)
    pd.testing.assert_frame_equal(
        result["de"].reset_index(drop=True), expected_de)


def test_split_double_newline() -> None:
    """Test the _split_double_newline function."""
    data = {
        "payload": [
            "Hello\n\nWorld",              # Simple case
            "Hello\n\n\n\nWorld",          # Multiple newlines
            "Only one line",               # No double newlines
            "\n\n\n\n",                    # Only newlines
            "Line1\n\nLine2\n\n\n\nLine3"  # Mixed spacing
        ]
    }
    df = pd.DataFrame(data)

    result = _split_double_newline(df)

    # Check resulting splits
    # 1) "Hello\n\nWorld" -> ["Hello", "World"]
    assert result.iloc[0] == ["Hello", "World"]

    # 2) "Hello\n\n\n\nWorld" -> ["Hello", "World"]
    #    Extra newlines in the middle should still split into just two items
    assert result.iloc[1] == ["Hello", "World"]

    # 3) "Only one line" -> ["Only one line"]
    #    No double newline => only one item
    assert result.iloc[2] == ["Only one line"]

    # 4) "\n\n\n\n" -> []
    #    Empty (only newlines), everything should be filtered out
    assert result.iloc[3] == []

    # 5) "Line1\n\nLine2\n\n\n\nLine3" -> ["Line1", "Line2", "Line3"]
    assert result.iloc[4] == ["Line1", "Line2", "Line3"]
