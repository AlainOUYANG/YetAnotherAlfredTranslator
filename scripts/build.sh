#!/bin/zsh
# 校验 + 测试 + 打包 dist/YetAnotherTranslator-<version>.alfredworkflow
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> plutil lint"
plutil -lint src/info.plist

echo "==> unittest"
/usr/bin/python3 -m unittest discover tests

echo "==> py_compile"
/usr/bin/python3 -m py_compile src/*.py

echo "==> 防密钥泄露检查（info.plist variables 必须为空）"
count=$(/usr/bin/python3 -c "import plistlib; print(len(plistlib.load(open('src/info.plist','rb')).get('variables', {})))")
if [[ "$count" != "0" ]]; then
  echo "ERROR: info.plist 的 variables 非空，可能包含密钥，拒绝打包" >&2
  exit 1
fi

version=$(/usr/bin/python3 -c "import plistlib; print(plistlib.load(open('src/info.plist','rb'))['version'])")
out="dist/YetAnotherTranslator-${version}.alfredworkflow"
mkdir -p dist
rm -f "$out"
(cd src && zip -rq "../$out" . -x '.DS_Store' -x '__pycache__/*' -x '*/__pycache__/*')

echo "==> 打包完成: $out"
unzip -l "$out"
