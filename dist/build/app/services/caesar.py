"""Caesar cipher: encode and constant-time compare."""
import secrets
import string


def caesar_encode(text: str, rotation: int) -> str:
    """Encode A-Z and a-z by shifting by rotation (1-25)."""
    out = []
    for c in text:
        if "A" <= c <= "Z":
            out.append(chr((ord(c) - ord("A") + rotation) % 26 + ord("A")))
        elif "a" <= c <= "z":
            out.append(chr((ord(c) - ord("a") + rotation) % 26 + ord("a")))
        else:
            out.append(c)
    return "".join(out)


def constant_time_compare(a: str, b: str) -> bool:
    return secrets.compare_digest(a.encode("utf-8"), b.encode("utf-8"))
