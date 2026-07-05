# Mini Agent

> 单文件、零框架依赖的本地 AI Agent，专为 4B 小模型设计。

**463 行 Python + 232 行 JS，一个文件即全部。**

---

## 功能

| 模块 | 说明 |
|------|------|
| 🧠 **AI 对话** | 连接 LM Studio 本地模型，两阶段规划（先思考再执行） |
| 🌐 **联网搜索** | DuckDuckGo 实时搜索，自动用搜索结果回答问题 |
| 💻 **Shell 执行** | 在终端执行命令，黑名单拦截危险操作 + 用户确认 |
| 💬 **多会话** | 左侧标签页管理，新建/切换/重命名/删除会话 |
| 📝 **Markdown** | 表格、代码块、粗体斜体、列表完整渲染 |
| 🔒 **安全机制** | 13 条黑名单正则 + PATH 劫持防护 + 用户确认弹窗 |
| 📊 **Token 计数** | 右上角实时显示累计 Token 消耗 |
| 🧩 **上下文管理** | Token 预算控制（8000）+ 自动摘要压缩（>16 条触发） |
| 🖥️ **自动平台检测** | 启动时识别 macOS/Windows/Linux，注入 System Prompt |

---

## 架构

```
┌─────────────────────────────────────────────┐
│              浏览器 Web UI                   │
│   聊天界面 · 多会话 · Markdown · Token 计数   │
└──────────────────┬──────────────────────────┘
                   │ HTTP
┌──────────────────▼──────────────────────────┐
│           mini_agent.py (Python)            │
│                                             │
│  /api/lm        → LM Studio 代理            │
│  /api/search    → DuckDuckGo 搜索            │
│  /api/shell/*   → Shell 执行 + 安全校验      │
│  /api/sessions  → 会话持久化 (JSON 文件)     │
└──────────────────┬──────────────────────────┘
                   │
      ┌────────────┼────────────┐
      ▼            ▼            ▼
  LM Studio    DuckDuckGo    终端 Shell
  (localhost    (ddgs)      (subprocess)
   :1234)
```

---

## 快速开始

### 前置条件

- Python 3.12+
- [LM Studio](https://lmstudio.ai/)（运行中，加载模型）
- macOS / Windows / Linux

### 安装

```bash
# 1. 克隆仓库
git clone https://github.com/LoadingVirus/mini-agent.git
cd mini-agent

# 2. 安装依赖
pip install ddgs --break-system-packages

# 3. 启动 LM Studio，加载模型（如 Gemma 4 E4B），端口 1234

# 4. 启动 Mini Agent
python3 mini_agent.py
```

打开浏览器访问 **http://localhost:8765**

### 依赖

| 包 | 版本 | 用途 |
|----|------|------|
| `ddgs` | ≥9.0 | DuckDuckGo 搜索 |

其余全部为 Python 标准库。

---

## 配置

修改 `mini_agent.py` 顶部常量：

```python
HOST, PORT = "localhost", 8765        # 服务地址
LM_STUDIO = "http://localhost:1234/v1" # LM Studio API
```

---

## 文件结构

```
mini-agent/
├── mini_agent.py      # 主程序（Python + 内嵌 HTML/JS）
├── README.md          # 项目说明
├── requirements.md    # 依赖文档
└── .gitignore         # 排除规则
```

---

## 安全模型

### Shell 黑名单（13 条正则）

| 模式 | 风险 |
|------|------|
| `rm\b` | 删除文件 |
| `sudo\b` | 提权操作 |
| `>\s*/dev/` | 写入块设备 |
| `mkfs\.` | 格式化 |
| `dd\s+if=` | 磁盘直接读写 |
| `chmod\s+(-R\s+)?777` | 开放所有权限 |
| `:\(\)\s*\{` | Fork 炸弹 |
| `\|\s*(ba)?sh\b` | 管道到 Shell |
| `curl.*\|\s*(ba)?sh` | curl 管道 |
| `>\s*/etc/` | 修改系统配置 |
| `shutdown\|reboot\|halt` | 关机/重启 |
| `killall\s+-9` | 强制终止进程 |
| 非系统路径 | PATH 劫持 |

常规命令直接执行，命中黑名单弹窗确认。

---

## 设计理念

专为 **4B 参数小模型**（Gemma 4 E4B）优化：

- System Prompt < 500 tokens
- 工具 ≤ 2 个（web_search + run_shell）
- 两阶段规划：先列出步骤，再带工具执行
- 防死循环：搜索计数上限 + `max_turns` 兜底

---

## License

MIT