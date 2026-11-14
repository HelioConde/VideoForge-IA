#!/usr/bin/env bash
# Archive every *actual* PNG, including candidates that fail human/technical QA.
# If the generation succeeded but produced no PNG, this step MUST fail.
set -euo pipefail
if [[ $# -ne 6 ]]; then
  echo "::error::Usage: arquivar-pngs-se-existirem.sh channel video_id source run_id producer prior_job_status" >&2
  exit 2
fi
CH="$1"
VID="$2"
SOURCE="$3"
RUN="$4"
PRODUCER="$5"
PRIOR_STATUS="$6"
case "$PRIOR_STATUS" in
  success|failure|cancelled) ;;
  *) echo "::error::Invalid status for image archiving" >&2; exit 2;;
esac

if [[ -d "$SOURCE" ]] && find "$SOURCE" -type f -name '*.png' -print -quit | grep -q .; then
  if [[ -z "$CH" || -z "$VID" ]]; then
    echo "::error::Image exists but channel/video provenance missing. Refusing orphaned PNG." >&2
    exit 2
  fi
  bash scripts/persistir-imagens-gh.sh "$CH" "$VID" "$SOURCE" "$RUN" "$PRODUCER"
  echo "PNG_ORIGINAL_PRESERVED_EVEN_IF_VISUAL_QA_FAILED $CH/$VID $RUN"
  exit 0
fi

if [[ "$PRIOR_STATUS" == success ]]; then
  echo "::error::Job succeeded but no original PNG was found: $SOURCE" >&2
  exit 2
fi
echo "No PNG generated; previous job status=$PRIOR_STATUS. No empty archive created."
exit 0
