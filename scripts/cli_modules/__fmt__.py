"""
Auxiliary func to format text for outputing to console.
"""

def info(msg: str) -> str:
    return "INFO: " + msg

def bad_input(msg: str) -> str:
    return "BAD INPUT: " + msg

def error(msg: str) -> str:
    return "ERROR: " + msg