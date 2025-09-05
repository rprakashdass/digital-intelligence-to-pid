import re
from typing import Optional
from backend.models import InstrumentTag

# Regex to parse ISA-style tags. Examples: FIC-101, PSHH-12, T-23A
# - Group 1: Loop letters (e.g., FIC, P, T)
# - Group 2: Loop number (e.g., 101, 12, 23)
# - Group 3: Modifiers (e.g., HH, A) - optional
ISA_TAG_REGEX = re.compile(r'^([A-Z]{1,4})(?:-)?(\d{1,5})([A-Z]{1,4})?$')

def parse_isa_tag(text: str) -> InstrumentTag:
    """
    Parses a string to identify and structure an ISA-style instrument tag.
    """
    match = ISA_TAG_REGEX.match(text.strip().upper())

    if not match:
        return InstrumentTag(rawTag=text, isParsed=False)

    groups = match.groups()
    loop_letters = groups[0]
    loop_no = int(groups[1])
    modifiers_str = groups[2]
    
    modifiers = list(modifiers_str) if modifiers_str else []

    return InstrumentTag(
        rawTag=text,
        loopLetters=loop_letters,
        loopNo=loop_no,
        modifiers=modifiers,
        isParsed=True
    )
