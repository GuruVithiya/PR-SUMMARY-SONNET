import re

MAX_DIFF_SIZE = 50_000

SECRET_PATTERNS = [
    r'(?i)(password|passwd|secret|api[_-]?key|auth[_-]?token|access[_-]?token)["\s]*[:=]["\s]*\S+',
    r'AKIA[0-9A-Z]{16}',
    r'(?i)aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*\S+',
    r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]+?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    r'ghp_[A-Za-z0-9]{36}',
    r'glpat-[A-Za-z0-9\-]{20}',
]


def collect_and_validate(diff: str) -> str:
    if not diff or not diff.strip():
        raise ValueError("Missing required field: diff")

    for pattern in SECRET_PATTERNS:
        diff = re.sub(pattern, "[REDACTED]", diff)

    if len(diff) > MAX_DIFF_SIZE:
        diff = diff[:MAX_DIFF_SIZE] + "\n\n... [diff truncated at 50,000 characters]"

    return diff
