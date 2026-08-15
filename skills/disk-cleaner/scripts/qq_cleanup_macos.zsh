#!/bin/zsh
set -u

readonly EFFECTIVE_HOME=${QQ_CLEANUP_HOME:-$HOME}
typeset -a QQ_ROOTS TARGET_DIRS
QQ_ROOTS=(
  "$EFFECTIVE_HOME/Library/Containers/com.tencent.qq/Data/Library/Application Support/QQ"
  "$EFFECTIVE_HOME/Library/Application Support/QQ-NT"
)

usage() {
  cat <<'EOF'
Usage:
  qq_cleanup_macos.zsh audit
  qq_cleanup_macos.zsh clean --older-than-days N --categories Pic,Emoji [--execute]

clean is a preview unless --execute is supplied.
Only Pic and Emoji are accepted cleanup categories.
EOF
}

fail() {
  print -u2 -- "error: $1"
  exit ${2:-1}
}

require_macos() {
  [[ $(uname -s) == Darwin ]] || fail "this script supports macOS only"
}

safe_root() {
  local root=$1
  [[ -d "$root" && ! -L "$root" ]] || return 1
  [[ "$root" == "$EFFECTIVE_HOME/Library/"* ]] || return 1
}

allowed_category_dir() {
  local root=$1 dir=$2 category=$3 rel
  [[ "$dir" == "$root/"* && -d "$dir" && ! -L "$dir" ]] || return 1
  rel=${dir#"$root/"}

  case "$category" in
    Pic|Emoji)
      [[ "$rel" == nt_qq_*/nt_data/"$category" ]] || \
        [[ "$category" == Emoji && "$rel" == global/nt_data/Emoji ]]
      ;;
    nt_db)
      [[ "$rel" == nt_qq_*/nt_db ]]
      ;;
    Cache|'Code Cache'|GPUCache)
      [[ "$rel" == "$category" || "$rel" == Partitions/*/"$category" ]]
      ;;
    nt_temp|log)
      [[ "$rel" == nt_qq_*/nt_data/"$category" ]]
      ;;
    *) return 1 ;;
  esac
}

discover_dirs() {
  local root=$1 category=$2 dir
  find "$root" -xdev -maxdepth 5 -type d -name "$category" -print0 2>/dev/null |
    while IFS= read -r -d '' dir; do
      allowed_category_dir "$root" "$dir" "$category" && print -r -- "$dir"
    done
}

audit() {
  local root category dir kib found=0
  print -- $'Category\tSize(KiB)\tPath'

  for root in "${QQ_ROOTS[@]}"; do
    [[ -e "$root" ]] || continue
    safe_root "$root" || fail "unsafe QQ root: $root"
    (( found += 1 ))

    for category in Pic Emoji nt_db Cache 'Code Cache' GPUCache nt_temp log; do
      while IFS= read -r dir; do
        [[ -n "$dir" ]] || continue
        kib=$(du -sk "$dir" 2>/dev/null | awk '{print $1}') || fail "cannot measure: $dir"
        print -r -- "${category}"$'\t'"${kib:-0}"$'\t'"$dir"
      done < <(discover_dirs "$root" "$category")
    done
  done

  (( found > 0 )) || fail "no recognized QQ storage found" 2
}

parse_clean_args() {
  local arg
  CLEAN_DAYS=''
  CLEAN_CATEGORIES=''
  CLEAN_EXECUTE=0
  shift

  while (( $# > 0 )); do
    arg=$1
    case "$arg" in
      --older-than-days)
        (( $# >= 2 )) || fail "--older-than-days needs a value"
        CLEAN_DAYS=$2
        shift 2
        ;;
      --categories)
        (( $# >= 2 )) || fail "--categories needs a value"
        CLEAN_CATEGORIES=$2
        shift 2
        ;;
      --execute)
        CLEAN_EXECUTE=1
        shift
        ;;
      *) fail "unknown option: $arg" ;;
    esac
  done

  [[ "$CLEAN_DAYS" == <-> && "$CLEAN_DAYS" -gt 0 ]] || fail "days must be a positive integer"
  [[ -n "$CLEAN_CATEGORIES" ]] || fail "categories are required"
}

collect_targets() {
  local list_file=$1 cutoff=$2 root category dir
  : > "$list_file" || return 1
  TARGET_DIRS=()

  for root in "${QQ_ROOTS[@]}"; do
    [[ -e "$root" ]] || continue
    safe_root "$root" || return 1
    for category in ${(s:,:)CLEAN_CATEGORIES}; do
      while IFS= read -r dir; do
        [[ -n "$dir" ]] || continue
        TARGET_DIRS+=("$dir")
        find "$dir" -xdev -type f ! -newermt "$cutoff" -print0 2>/dev/null >> "$list_file" || return 1
      done < <(discover_dirs "$root" "$category")
    done
  done
}

path_is_targeted() {
  local file=$1 dir
  [[ -f "$file" && ! -L "$file" ]] || return 1
  for dir in "${TARGET_DIRS[@]}"; do
    [[ "$file" == "$dir/"* ]] && return 0
  done
  return 1
}

qq_is_stopped() {
  command -v pgrep >/dev/null 2>&1 || return 2
  pgrep -x QQ >/dev/null 2>&1
  case $? in
    0) return 1 ;;
    1) return 0 ;;
    *) return 2 ;;
  esac
}

clean() {
  local cutoff list_file file count blocks bytes deleted=0 failed=0 residual
  parse_clean_args "$@"

  local category
  for category in ${(s:,:)CLEAN_CATEGORIES}; do
    [[ "$category" == Pic || "$category" == Emoji ]] || fail "only Pic and Emoji may be cleaned"
  done

  cutoff=$(date -v-"${CLEAN_DAYS}"d '+%Y-%m-%d %H:%M:%S' 2>/dev/null) || fail "cannot calculate cutoff"
  list_file=$(mktemp "${TMPDIR:-/tmp}/qq-cleanup.XXXXXX") || fail "cannot create temporary list"
  CLEAN_LIST_FILE=$list_file
  trap 'rm -f -- "$CLEAN_LIST_FILE"' EXIT INT TERM
  collect_targets "$list_file" "$cutoff" || fail "cannot collect safe targets"

  count=$(tr -cd '\000' < "$list_file" | wc -c | tr -d ' ')
  if [[ -s "$list_file" ]]; then
    blocks=$(xargs -0 stat -f '%b' < "$list_file" 2>/dev/null | awk '{s+=$1} END {print s+0}') || fail "cannot measure targets"
  else
    blocks=0
  fi
  bytes=$(( blocks * 512 ))

  print -- "mode=$([[ $CLEAN_EXECUTE -eq 1 ]] && print execute || print preview)"
  print -- "cutoff=$cutoff"
  print -- "categories=$CLEAN_CATEGORIES"
  print -- "files=$count"
  print -- "estimated_bytes=$bytes"

  if (( CLEAN_EXECUTE == 0 )); then
    print -- "No files changed. Re-run with --execute only after approval and after quitting QQ."
    return 0
  fi

  qq_is_stopped
  case $? in
    0) ;;
    1) fail "QQ is running; quit QQ before cleanup" ;;
    *) fail "cannot determine whether QQ is running" ;;
  esac

  while IFS= read -r -d '' file; do
    if path_is_targeted "$file" && rm -f -- "$file"; then
      (( deleted += 1 ))
    else
      (( failed += 1 ))
    fi
  done < "$list_file"

  collect_targets "$list_file" "$cutoff" || fail "cleanup finished but verification failed"
  residual=$(tr -cd '\000' < "$list_file" | wc -c | tr -d ' ')
  print -- "deleted_files=$deleted"
  print -- "failed_files=$failed"
  print -- "residual_files=$residual"
  df -h /System/Volumes/Data 2>/dev/null | tail -n 1 || true

  (( failed == 0 && residual == 0 ))
}

main() {
  require_macos
  case ${1:-} in
    audit) audit ;;
    clean) clean "$@" ;;
    -h|--help|help|'') usage ;;
    *) usage; exit 64 ;;
  esac
}

main "$@"
