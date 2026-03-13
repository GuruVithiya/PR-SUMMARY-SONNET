import argparse
import json
import os
import sys

from diff_collector import collect_and_validate
from prompt_builder import build_messages
from system_prompt import SYSTEM_PROMPT
from inference_wrapper import call_claude
from response_parser import parse_response, format_comment


def main():
    parser = argparse.ArgumentParser(description="Analyze a git diff with Claude Sonnet.")
    parser.add_argument("--diff-file", help="Path to file containing the git diff")
    args = parser.parse_args()

    # Read diff from file or stdin
    if args.diff_file:
        with open(args.diff_file, "r", encoding="utf-8", errors="replace") as f:
            raw_diff = f.read()
    else:
        raw_diff = sys.stdin.read()

    # PR metadata from environment
    pr_title = os.environ.get("PR_TITLE", "")
    pr_description = os.environ.get("PR_DESCRIPTION", "")

    # Pipeline
    diff = collect_and_validate(raw_diff)
    messages = build_messages(diff, pr_title, pr_description)
    raw_response = call_claude(SYSTEM_PROMPT, messages)
    analysis = parse_response(raw_response)

    output = analysis.model_dump()
    output["comment"] = format_comment(analysis)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
