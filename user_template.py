def build_user_message(diff: str, pr_title: str = "", pr_description: str = "") -> str:
    parts = []

    if pr_title:
        parts.append(f"PR Title: {pr_title}")

    if pr_description:
        parts.append(f"PR Description:\n{pr_description}")

    parts.append(f"Git Diff:\n{diff}")

    return "\n\n".join(parts)
