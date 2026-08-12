#!/bin/zsh
# 发音：speak.sh <local|online> <text>
# 依赖 Alfred 传入的环境变量：speak_lang、speak_url、voice_en、voice_zh、alfred_workflow_cache
mode="$1"
text="$2"
[[ -z "$text" ]] && exit 0

say_local() {
  if [[ "$speak_lang" == "zh" ]]; then
    voice="${voice_zh:-Tingting}"
  else
    voice="${voice_en:-Samantha}"
  fi
  say -v "$voice" "$text"
}

if [[ "$mode" == "local" ]]; then
  say_local
  exit $?
fi

# online：优先 API 返回的发音 URL，为空回退有道 dictvoice；下载失败回退本地 say
url="$speak_url"
if [[ -z "$url" ]]; then
  encoded=$(/usr/bin/python3 -c "import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1]))" "$text")
  url="https://dict.youdao.com/dictvoice?type=2&audio=${encoded}"
fi

cache_dir="${alfred_workflow_cache:-${TMPDIR:-/tmp}}"
mkdir -p "$cache_dir"
file="$cache_dir/voice-$(md5 -q -s "$url").mp3"

if [[ ! -s "$file" ]]; then
  curl -sL --noproxy '*' -m 10 -o "$file" "$url" || rm -f "$file"
  # 下载到空文件或 HTML 错误页时清掉，避免 afplay 播放坏文件
  [[ -s "$file" ]] || rm -f "$file"
fi

if [[ -s "$file" ]]; then
  afplay "$file"
else
  say_local
fi
