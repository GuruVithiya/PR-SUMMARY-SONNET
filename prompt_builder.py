from user_template import build_user_message


def build_messages(diff: str, pr_title: str = "", pr_description: str = "") -> list:
    user_message = build_user_message(diff, pr_title, pr_description)
    return [{"role": "user", "content": user_message}]
