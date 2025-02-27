"""
Testing the body_analysis module
"""
# pylint: disable=redefined-outer-name


from jobtrendx.body_analysis import _get_sections


def test_get_sections_de() -> None:
    """test if detect de sections correctly"""
    sections_de = {
        "job_title": "Beliebter Job",
        "company": "Wer wir sind.",
        "requirements": "Das bringst du mit",
        "benefits": "Das bieten wir dir"
        }

    body_text = """Beliebter Job
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
    sections: dict[str, str] = _get_sections(body_text, sections_de)
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

    body_text = """Top Match
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

    sections: dict[str, str] = _get_sections(body_text, sections_en)

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
