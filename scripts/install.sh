#!/bin/zsh
# 构建并安装进 Alfred（同 bundleid 覆盖升级，保留用户已填配置）
set -euo pipefail
cd "$(dirname "$0")/.."
scripts/build.sh
open dist/YetAnotherTranslator-*.alfredworkflow
