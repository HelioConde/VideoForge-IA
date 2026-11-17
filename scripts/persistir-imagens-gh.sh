#!/usr/bin/env bash
# Save PNGs created by VideoForge Actions to per-channel Git history.
# Strict mode: never silently "succeed" if the PNG was not preserved.
set -euo pipefail
if [[ $# -ne 5 ]]; then
  echo "::error::Usage: persistir-imagens-gh.sh channel video_id output_dir run_id producer" >&2
  exit 2
fi
CHANNEL="$1"
VIDEO_ID="$2"
OUTPUT_DIR="$3"
RUN_ID="$4"
PRODUCER="$5"

# Python verifies exact output channel/video, PNG bytes, SHA and JSON safety.
python -m videoforge.persist_generated_assets \
  --channel "$CHANNEL" --video-id "$VIDEO_ID" \
  --input "$OUTPUT_DIR" --run-id "$RUN_ID" --producer "$PRODUCER"

# P0 Bíblia Visual: commit atômico entre a imagem original e o registro.
# Qualquer falha no SHA/JSON/status bloqueia o push do PNG, nunca finge sucesso.
python -m videoforge.visual_bible --channel "$CHANNEL"
# Keep the EP01 progress checkpoint synchronized with the real SHA archive
# during each successful image push, not from stale prose or user guesses.
if [[ "$CHANNEL" == "alchemy-lab" && "$VIDEO_ID" == "mmorpg-conquiste-a-princesa-ep01" ]]; then
  python -m videoforge.ep01_image_inventory --write
fi
DEST="canal/$CHANNEL/videos/$VIDEO_ID/assets/geracoes/$PRODUCER/$RUN_ID"
BIBLE_DIR="canal/$CHANNEL/biblia-visual"
git config user.name 'videoforge-assets[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add -f -- "$DEST"
git add -A -- "$BIBLE_DIR"
if [[ "$CHANNEL" == "alchemy-lab" && "$VIDEO_ID" == "mmorpg-conquiste-a-princesa-ep01" ]]; then
  git add -f -- "canal/$CHANNEL/videos/$VIDEO_ID/CHECKPOINT-IMAGENS-EP01-AUTO.json"
fi
if git diff --cached --quiet; then
  echo "GITHUB_IMAGE_ARCHIVE_ALREADY_IDENTICAL $DEST"
  exit 0
fi
git commit -m "assets($CHANNEL): PNG SHA + registro Bib Visual $PRODUCER run-$RUN_ID"
for attempt in 1 2 3; do
  if git push origin HEAD:main; then
    echo "GITHUB_IMAGE_ARCHIVE_AND_BIBLE_REGISTRY_COMMITTED $DEST $BIBLE_DIR"
    exit 0
  fi
  if [[ "$attempt" -lt 3 ]]; then
    git fetch origin main
    if ! git rebase origin/main; then
      git rebase --abort || true
      echo "::error::Concurrent asset conflict. Manual repair required; image remains in Actions artifact." >&2
      exit 1
    fi
  fi
done
echo "::error::PNG generated but permanent GitHub archive push failed" >&2
exit 1
