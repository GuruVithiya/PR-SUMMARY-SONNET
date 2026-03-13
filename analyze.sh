#!/bin/bash
set -e

# Fetch target branch for diff comparison
git fetch origin "$CI_MERGE_REQUEST_TARGET_BRANCH_NAME"

# Generate diff
git diff "origin/${CI_MERGE_REQUEST_TARGET_BRANCH_NAME}...HEAD" > diff.txt

# Skip if no changes
if [ ! -s diff.txt ]; then
  echo "No diff found. Skipping analysis."
  exit 0
fi

# Run analysis
PR_TITLE="$CI_MERGE_REQUEST_TITLE" \
PR_DESCRIPTION="$CI_MERGE_REQUEST_DESCRIPTION" \
python main.py --diff-file diff.txt > analysis.json

# Build JSON payload for GitLab API
python -c "
import json
analysis = json.load(open('analysis.json'))
print(json.dumps({'body': analysis['comment']}))
" > comment_payload.json

# Post MR comment
curl --silent --fail \
  --request POST \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  --header "Content-Type: application/json" \
  --data @comment_payload.json \
  "https://gitlab.com/api/v4/projects/${CI_PROJECT_ID}/merge_requests/${CI_MERGE_REQUEST_IID}/notes"

echo "Analysis posted successfully."
