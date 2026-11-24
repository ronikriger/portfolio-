#!/bin/sh
# Publish the ocf-site branch to https://www.ocf.berkeley.edu/~rkriger/
# Run it on OCF (for example in the browser terminal at https://ssh.ocf.berkeley.edu/):
#   curl -fsSL https://raw.githubusercontent.com/ronikriger/portfolio-/ocf-site/deploy.sh | sh
set -eu
SITE="${RK_SITE:-$HOME/public_html}"
URL="${RK_URL:-https://www.ocf.berkeley.edu/~rkriger/}"
TARBALL="https://github.com/ronikriger/portfolio-/archive/refs/heads/ocf-site.tar.gz"
BACKUP="$HOME/site-backups/$(date +%Y%m%d-%H%M%S)"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

echo "1/4  Downloading the site from GitHub"
curl -fsSL "$TARBALL" | tar -xz -C "$TMP" --strip-components=1
[ -f "$TMP/public/index.html" ] || { echo "The download looks wrong, so nothing was changed."; exit 1; }

echo "2/4  Backing up the current site to $BACKUP"
mkdir -p "$BACKUP"
cp -a "$SITE/." "$BACKUP/"

echo "3/4  Installing"
cp -R "$TMP/public/." "$SITE/"
if [ -f "$TMP/tools/obsolete.txt" ]; then
  while IFS= read -r f; do [ -n "$f" ] && rm -f "$SITE/$f"; done < "$TMP/tools/obsolete.txt"
fi
chmod -R a+rX "$SITE/"

echo "4/4  Checking the live site"
status() { curl -s -o /dev/null -w '%{http_code}' "$URL" || echo 000; }
code=$(status)
if [ "$code" != "200" ]; then
  echo "     It answered $code with the full server settings. Trying the basic ones."
  cp "$TMP/tools/htaccess-basic" "$SITE/.htaccess"; chmod 644 "$SITE/.htaccess"
  code=$(status)
fi
if [ "$code" != "200" ]; then
  echo "     Still $code. Removing the server settings file."
  rm -f "$SITE/.htaccess"
  code=$(status)
fi
if [ "$code" = "200" ]; then
  echo "Done: $URL is live."
else
  echo "The site answered $code. Your previous site is saved in $BACKUP"
  echo "To restore it: cp -a \"$BACKUP/.\" \"$SITE/\""
  exit 1
fi
