#!/bin/sh
set -eu

: "${GITHUB_RUN_ID:?Run this script in GitHub Actions}"
export COMPOSE_PROJECT_NAME="tp3-gh-${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT:-1}"

compose() {
  docker compose -f docker-compose.yml -f docker-compose.ci.yml "$@"
}

mkdir -p reports

cleanup() {
  result=$?
  trap - EXIT
  set +e
  compose ps -a > reports/compose-ps.txt 2>&1
  compose logs --no-color > reports/compose.log 2>&1
  for filename in zap-report.html zap-report.json zap-summary.json zap-summary.md; do
    compose cp "zap:/zap/wrk/$filename" "reports/$filename" >/dev/null 2>&1
  done
  compose down --volumes --remove-orphans
  exit "$result"
}
trap cleanup EXIT

compose config --quiet
compose build app
compose up -d db

ready=0
for attempt in $(seq 1 60); do
  if compose exec -T db mongo --quiet --username username --password password --authenticationDatabase admin --eval 'quit(db.adminCommand({ping: 1}).ok ? 0 : 1)' >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 2
done
if [ "$ready" -ne 1 ]; then
  echo 'MongoDB did not become ready.' >&2
  exit 3
fi

compose up -d app zap
ready=0
for attempt in $(seq 1 60); do
  if compose exec -T app python -c 'import urllib.request; assert urllib.request.urlopen("http://127.0.0.1:5000", timeout=3).status == 200' >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 2
done
if [ "$ready" -ne 1 ]; then
  echo 'TIWAP did not become ready.' >&2
  exit 3
fi

compose exec -T zap mkdir -p /zap/wrk
set +e
compose exec -T zap zap-baseline.py -t http://app:5000 -m 2 -r zap-report.html -J zap-report.json > reports/zap-console.log 2>&1
scan_status=$?
set -e
cat reports/zap-console.log
printf '%s\n' "$scan_status" > reports/zap-exit-code.txt
compose cp zap:/zap/wrk/zap-report.html reports/zap-report.html
compose cp zap:/zap/wrk/zap-report.json reports/zap-report.json
test -s reports/zap-report.html
test -s reports/zap-report.json
if ! compose exec -T zap python3 - < ci/validate-report.py; then
  echo 'ZAP did not produce valid reports.' >&2
  exit 3
fi
compose cp zap:/zap/wrk/zap-summary.json reports/zap-summary.json
compose cp zap:/zap/wrk/zap-summary.md reports/zap-summary.md
exit "$scan_status"
