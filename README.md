# Yet Another Translator

Alfred 5 中英互译 Workflow，翻译引擎为有道智云。

特点：

- **零依赖**：只用 macOS 系统自带的 `/usr/bin/python3` 标准库，不捆绑任何二进制，Intel / Apple Silicon 通用
- **密钥安全**：appKey/secret 通过 Alfred 的 Configure Workflow 面板配置，只存在本机，不随 Workflow 分发
- **自动识别方向**：查询含任意中文字符即中→英，否则自动→中（含标点、数字的中文句子也能正确判向）
- **词典信息**：单词查询展示美/英音标、词典释义、词形变化、网络释义
- **发音**：⌘回车本地发音（macOS `say`）、⌥回车在线发音（有道语音，带缓存，失败自动回退本地）
- **省配额**：输入防抖 + 结果缓存 24 小时（可关）
- **代码翻译友好**：驼峰/下划线命名自动拆词（`getHTTPServer` → `get HTTP Server`，缩略词不拆碎）

## 安装

1. 从 `dist/` 双击 `YetAnotherTranslator-*.alfredworkflow` 安装（或运行 `scripts/install.sh`）
2. 注册有道智云并创建应用（免费，新用户有体验金）：
   1. 注册账号：https://ai.youdao.com/
   2. 控制台创建「文本翻译」服务
   3. 创建应用（接入方式选 API），绑定文本翻译服务，得到「应用 ID」和「应用密钥」
3. 在 Alfred 中打开本 Workflow 的 **Configure Workflow** 面板，填入应用 ID 和密钥
4. （可选）双击画布左侧的 Hotkey 节点设置热键（建议双击 ⌥），用于翻译当前选中文本。Alfred 导出的 Workflow 不含热键键位，安装后需自行设置

## 用法

| 操作 | 效果 |
|---|---|
| `yd hello` / `yd 你好` | 翻译（触发词可在配置面板改） |
| 回车 | 复制该条结果到剪贴板并关闭 Alfred |
| ⌘回车 | 本地发音（音色可配置） |
| ⌥回车 | 在线发音（有道语音） |
| ⇧ | Quick Look 预览有道词典页 |
| ⌘L | 大字号查看完整译文（长文本） |
| 热键 | 翻译当前选中的文本 |

未配置密钥时，触发后会给出注册页和配置面板的引导条目。

## 开发

```bash
# 单测（纯 stdlib，无网络依赖）
/usr/bin/python3 -m unittest discover tests

# 命令行调试（不装进 Alfred）
cd src && youdao_app_key=xxx youdao_app_secret=yyy alfred_workflow_cache=/tmp/yat \
  /usr/bin/python3 translate.py "hello world" | /usr/bin/python3 -m json.tool

# 打包 / 打包并安装
scripts/build.sh
scripts/install.sh
```

结构：`src/` 为打包内容（`translate.py` Script Filter 入口、`youdao.py` API 客户端（v3 sha256 签名）、`util.py` 检测与缓存、`speak.sh` 发音、`info.plist` 节点图与配置面板）；`tests/` 单测；`scripts/` 构建脚本。
