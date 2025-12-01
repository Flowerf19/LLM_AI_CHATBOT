#!/usr/bin/env bash
echo "Detection of tracked sensitive files and removal from git index (local)."

FILES=(.env)
for f in "${FILES[@]}"; do
  if git ls-files --error-unmatch "$f" > /dev/null 2>&1; then
    echo "Removing tracked file from git index: $f"
    git rm --cached "$f"
    git commit -m "chore: remove sensitive file $f from repo index"
  else
    echo "$f not tracked by git"
  fi
done

echo "Done. Consider rotating any exposed keys and running BFG or git-filter-repo if you want to purge them from the entire history."
