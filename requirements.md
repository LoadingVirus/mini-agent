# Requirements

| 包 | 版本 | 用途 |
|----|------|------|
| [ddgs](https://github.com/deedy5/ddgs) | ≥9.0 | DuckDuckGo 搜索引擎封装 |
| [LM Studio](https://lmstudio.ai/) | — | 本地 LLM 推理服务（需单独安装） |

## 安装

```bash
pip install ddgs --break-system-packages
```

> `--break-system-packages` 仅在使用 Homebrew Python 时需要，绕过 PEP 668 限制。使用 venv 或 conda 可省略。

## Python 版本

Python 3.12+（使用了 `subprocess.run` 新特性，需 OpenSSL 3.x 支持 TLS 1.3）