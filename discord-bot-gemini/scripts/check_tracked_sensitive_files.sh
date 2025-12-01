#!/usr/bin/env bash
echo "Checking for tracked sensitive files (e.g., .env) in git index..."
TRACKED=$(git ls-files | grep -E "(^|/)\.env$|\.pem$|\.key$" || true)
if [ -z "$TRACKED" ]; then
  echo "No tracked sensitive files found."
else
  echo "Tracked sensitive files found:" && echo "$TRACKED"
fi

echo "Done."
