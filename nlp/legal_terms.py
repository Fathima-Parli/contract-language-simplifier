"""
Legal Terms Glossary and Highlighter
Provides plain-English definitions of common legal/contract terms
and identifies them in text for highlighting.
"""

import re

# Comprehensive legal terms glossary
LEGAL_GLOSSARY = {
    "hereinafter": "From this point forward in this document; used to introduce a shorter name for a person or thing.",
    "hereinabove": "Previously mentioned in this document.",
    "herein": "In this document or agreement.",
    "hereof": "Of this document or agreement.",
    "hereunder": "Under the terms of this document.",
    "hereby": "By this statement or document.",
    "hereto": "To this document or agreement.",
    "hereafter": "After this point in the document or in the future.",
    "thereof": "Of that thing previously mentioned.",
    "therein": "In that place or document.",
    "thereby": "By means of that action.",
    "thereto": "To that thing or place.",
    "thereunder": "Under that agreement or law.",
    "indemnify": "To protect someone from financial loss or legal responsibility; to compensate for harm or loss.",
    "indemnification": "The act of protecting someone from financial loss or legal liability.",
    "indemnity": "Protection or compensation for losses or damages.",
    "liability": "Legal responsibility for something, especially the obligation to pay debts or damages.",
    "liabilities": "Legal or financial obligations; debts that must be paid.",
    "liable": "Legally responsible for something.",
    "notwithstanding": "Despite what has just been said; in spite of.",
    "pursuant to": "In accordance with; following the requirements of.",
    "in accordance with": "Following the rules or requirements of something.",
    "in witness whereof": "This phrase indicates the signing of the document as proof of agreement.",
    "force majeure": "Unexpected events outside anyone's control (like natural disasters) that prevent fulfilling a contract.",
    "breach": "A violation or breaking of a law, contract, or obligation.",
    "breach of contract": "When one party fails to fulfill their obligations under a contract.",
    "remedy": "A solution or compensation for a legal wrong or breach.",
    "remedies": "Solutions or compensations available for a legal wrong.",
    "arbitration": "A way to resolve disputes outside of court, using a neutral third party (arbitrator) to make a decision.",
    "jurisdiction": "The official authority of a court to make legal decisions within a certain area or over specific cases.",
    "covenant": "A binding promise or agreement, often in a contract.",
    "covenants": "Binding promises or agreements in a contract.",
    "warranty": "A promise or guarantee that something will work or be as described.",
    "warranties": "Promises or guarantees that things will work or be as described.",
    "representation": "A statement of fact made to encourage someone to enter a contract.",
    "representations": "Statements of fact made to encourage someone to enter a contract.",
    "indemnitor": "The party who agrees to protect another from losses or liability.",
    "indemnitee": "The party who is protected from losses or liability.",
    "counterpart": "Each signed copy of a contract; all counterparts together make one complete agreement.",
    "severability": "A clause meaning that if one part of the contract is found to be invalid, the rest still stands.",
    "waiver": "Voluntarily giving up a right or claim that you are legally entitled to.",
    "waivers": "Acts of voluntarily giving up rights or claims.",
    "indemnified party": "The person or company being protected from losses or liability.",
    "liquidated damages": "A specific amount of money agreed upon in advance to be paid if the contract is broken.",
    "consequential damages": "Losses that result indirectly from a breach, beyond the direct loss.",
    "punitive damages": "Money awarded as punishment for especially bad behavior, beyond actual losses.",
    "compensatory damages": "Money paid to cover actual losses suffered.",
    "statute of limitations": "The deadline by which legal action must be started.",
    "governing law": "Which state's or country's laws apply to interpret and enforce the contract.",
    "good faith": "Acting honestly and fairly, without trying to deceive or take unfair advantage.",
    "due diligence": "Careful research and investigation done before signing a contract or making a decision.",
    "force": "Compel someone to do something by using authority or threats.",
    "obligee": "The party who is owed an obligation under a contract.",
    "obligor": "The party who owes an obligation under a contract.",
    "party of the first part": "The first person or company named in a contract (often the seller or employer).",
    "party of the second part": "The second person or company named in a contract (often the buyer or employee).",
    "witnesseth": "An old-fashioned word meaning 'this agreement states that'.",
    "whereas": "Given that; considering that (used to introduce background facts in a contract).",
    "now therefore": "Because of the above reasons, the parties agree to the following.",
    "in consideration of": "In exchange for something of value (the reason both parties enter the contract).",
    "mutual covenants": "Promises made by both sides of the agreement.",
    "assigns": "People or companies to whom rights or duties are transferred.",
    "successors": "People or companies that follow after and take on the rights and responsibilities.",
    "in perpetuity": "Forever; with no end date.",
    "at law": "According to legal rules rather than moral considerations.",
    "in equity": "Based on fairness and justice, rather than strict legal rules.",
    "indemnify and hold harmless": "To protect someone from any future claims, losses, or lawsuits.",
    "hold harmless": "To protect someone from being blamed or sued for something.",
    "cure period": "A set time given to fix (cure) a problem before being in breach of contract.",
    "default": "Failure to meet legal obligations or repay a debt.",
    "in default": "Having failed to meet an obligation, especially payment.",
    "termination for cause": "Ending a contract because one party has done something wrong.",
    "termination for convenience": "Ending a contract without needing a specific reason.",
    "pro rata": "Proportionally; divided equally based on time or usage.",
    "bona fide": "In good faith; genuine and honest.",
    "ab initio": "From the beginning (Latin).",
    "inter alia": "Among other things (Latin).",
    "mutatis mutandis": "With the necessary changes made (Latin).",
    "ipso facto": "By that very fact or act itself (Latin).",
    "pari passu": "At an equal rate or on equal terms (Latin).",
    "pro forma": "As a matter of form; standard procedure.",
    "without prejudice": "Without affecting any existing legal rights or claims.",
    "time is of the essence": "Deadlines in this contract are absolutely critical and must be met.",
    "entire agreement": "This contract is the complete and final agreement, replacing all previous discussions.",
    "merger clause": "A statement that the written contract is the complete agreement, replacing all prior discussions.",
    "integration clause": "Same as merger clause — the written contract is the complete and final agreement.",
    "confidentiality": "The obligation to keep information private and not share it with others.",
    "non-disclosure": "An agreement not to share certain private information with others.",
    "intellectual property": "Creative works, inventions, or designs that are legally owned (patents, copyrights, trademarks).",
    "assignment": "Transferring rights or obligations under a contract to someone else.",
    "subcontract": "Hiring another company or person to do part of the work you've agreed to do.",
    "work product": "Anything created by an employee or contractor as part of their job.",
    "work for hire": "Creative work done as part of employment, owned by the employer rather than the creator.",
    "lien": "A legal claim on property as security for a debt.",
    "encumbrance": "A claim or restriction on property, such as a lien or mortgage.",
    "collateral": "Property pledged as security for repayment of a loan.",
    "escrow": "Money or property held by a neutral third party until conditions are met.",
    "promissory note": "A written promise to pay a specific amount of money by a specific date.",
    "due and payable": "Owed and required to be paid at this time.",
    "accrued": "Accumulated or built up over time, even if not yet paid.",
}

def find_legal_terms(text):
    """
    Scan input text for known legal terms and return a list of found terms
    with their definitions.

    Args:
        text (str): Input text to scan

    Returns:
        list: List of dicts with {term, definition} for each found term,
              sorted by position of first occurrence.
    """
    if not text or not text.strip():
        return []

    text_lower = text.lower()
    found = {}  # term_lower -> {term, definition, first_pos}

    for term, definition in LEGAL_GLOSSARY.items():
        # Build regex to find whole-word matches (case-insensitive)
        pattern = r'\b' + re.escape(term) + r'\b'
        match = re.search(pattern, text_lower)
        if match:
            found[term] = {
                "term": term,
                "display_term": term.title(),
                "definition": definition,
                "first_pos": match.start()
            }

    # Sort by position of first occurrence in the text
    sorted_terms = sorted(found.values(), key=lambda x: x['first_pos'])

    # Remove internal 'first_pos' before returning
    return [{"term": item["term"], "display_term": item["display_term"], "definition": item["definition"]}
            for item in sorted_terms]


def highlight_text_html(text):
    """
    Return HTML version of the text with legal terms wrapped in
    <span class="legal-term" data-definition="..."> tags.

    Args:
        text (str): Plain text to process

    Returns:
        str: HTML string with terms highlighted
    """
    if not text or not text.strip():
        return text

    # Build list of (start, end, term, definition) for all matches
    matches = []
    text_lower = text.lower()

    for term, definition in LEGAL_GLOSSARY.items():
        pattern = r'\b' + re.escape(term) + r'\b'
        for m in re.finditer(pattern, text_lower):
            # Escape definition for HTML attribute
            safe_def = definition.replace('"', '&quot;').replace("'", '&#39;')
            matches.append((m.start(), m.end(), term, safe_def))

    if not matches:
        import html
        return html.escape(text).replace('\n', '<br>')

    # Sort matches by start pos; handle overlaps by keeping the first match
    matches.sort(key=lambda x: x[0])
    non_overlapping = []
    last_end = 0
    for start, end, term, safe_def in matches:
        if start >= last_end:
            non_overlapping.append((start, end, term, safe_def))
            last_end = end

    # Build HTML
    import html as html_module
    result = []
    last_idx = 0
    for start, end, term, safe_def in non_overlapping:
        # Add text before the match (escaped)
        result.append(html_module.escape(text[last_idx:start]).replace('\n', '<br>'))
        # Add highlighted term
        original_word = text[start:end]
        result.append(
            f'<span class="legal-term" data-definition="{safe_def}" tabindex="0">'
            f'{html_module.escape(original_word)}'
            f'</span>'
        )
        last_idx = end

    # Add remaining text
    result.append(html_module.escape(text[last_idx:]).replace('\n', '<br>'))
    return ''.join(result)
