**中文** | [English](README-EN.md)

# 自动化信息收集系统（FlashAttention & 深度推理加速资源）

自动化信息收集系统用于批量发现、筛选和整理 FlashAttention、DeepSeek Flash MLA、DeepGEMM、Deep EP 等深度学习推理加速相关的高质量资源。项目会从 DuckDuckGo 搜索结果与 GitHub 热门仓库中抓取候选链接，结合多维度评分与分类策略，最终将结果导出为结构化的 Excel/CSV 文件，方便学习与分享。

## ✨ 功能特性
- **多源搜索**：同时使用 DuckDuckGo 与 GitHub API，支持中英文关键词扩展。
- **自动分类**：根据标题、描述和链接特征识别网站、博客、代码、论坛、课程笔记/讲座、公开书籍、考试、技术/白皮书等类型。
- **质量评估**：结合 GitHub 星标、更新时间、官网来源、描述完整度等指标生成 1~5 分的质量评分。
- **推荐理由**：为高质量资源生成可读性较高的推荐语句，突出资源亮点。
- **数据导出**：支持按类型分 Sheet 的 Excel 文件及 UTF-8 编码的 CSV 备份，可直接分享或二次加工。
- **灵活配置**：通过 `config/config.yaml` 自定义关键词、过滤条件、输出路径等参数。

## 📁 目录结构
```
Automated Information Collection/
├─ config/                # YAML 配置文件
├─ resources/             # 导出的 Excel / CSV 资源（默认由程序生成）
├─ src/
│  ├─ collector.py        # 搜索与采集逻辑
│  ├─ parsers.py          # 资源解析、分类与评分
│  ├─ storage.py          # Excel / CSV 写入与统计
│  └─ main.py             # 命令行入口 & 业务编排
├─ main.py                # 示例入口（调用 src.main）
├─ pyproject.toml         # 项目依赖声明
├─ uv.lock                # uv 锁定文件
└─ README.md
```

## 🚀 快速开始
### 环境要求
- Python 3.12 及以上版本
- Windows / Linux / macOS 均可运行（默认输出支持中文）
- 访问 GitHub API 时需注意速率限制，建议登录网络环境稳定的网络

### 安装依赖
> 推荐使用 [uv](https://github.com/astral-sh/uv) 管理依赖，也可使用内置 `pip`。

**使用 uv：**
```cmd
uv sync
```

**使用 pip：**
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

## ⚙️ 配置说明
默认配置位于 `config/config.yaml`，可根据需要修改：
- `search.keywords_zh / keywords_en`：中英文关键字列表，可自由增删。
- `search.sources`：控制 DuckDuckGo 与 GitHub 搜索是否启用，以及最大结果数。
- `filters.min_quality_score`：导出前保留的最低质量分。
- `output.excel_file / csv_backup`：输出文件名称与是否生成 CSV 备份。
- `advanced.enable_proxy / proxy_url`：如需代理访问，可在此处开启。

如无自定义需求，保持默认即可直接运行；需使用自定义配置时，可在命令行传入 `--config path/to/your.yaml`。

## 🧪 使用方法
进入项目根目录后执行命令：

- **搜索并生成资源：**
  ```cmd
  uv run python -m src.main search
  ```
  或使用本地 Python 环境：
  ```cmd
  python -m src.main search
  ```
  可通过 `--keywords` 追加额外英文关键词，例如：
  ```cmd
  python -m src.main search --keywords "flash attention" "inference acceleration"
  ```

- **查看 Excel 统计信息：**
  ```cmd
  python -m src.main stats
  ```

- **尝试增量更新（开发中）：**
  ```cmd
  python -m src.main update --file flash_attention_resources.xlsx
  ```
  > 当前增量合并逻辑尚在完善阶段，命令会加载旧数据后执行完整搜索，请关注后续版本更新。

所有命令均支持 `--config` 指定配置文件路径，例如：
```cmd
python -m src.main search --config config/custom.yaml
```

## 📊 输出结果
默认在 `resources/` 目录生成以下文件：
- `flash_attention_resources.xlsx`：
  - `所有资源`：完整结果集合（含质量分、推荐理由、搜索关键词等字段）。
  - `网站 / 博客 / 代码 / 论坛 / 课程笔记讲座 / 公开书籍 / 考试 / 技术白皮书`：按类型拆分的 Sheet，仅在该类别存在数据时生成。
  - `统计信息`：数量、语言分布、来源分布、评分统计等汇总指标。
  - `Top20资源`：按质量分倒序的前 20 个资源。
- `flash_attention_resources.csv`：UTF-8（含 BOM）编码的备份文件，可在 Excel/Notebook 中直接打开。

## 🔧 开发与扩展建议
- ✅ 已实现自动去重、评分、推荐语生成逻辑。
- 🚧 计划增强增量更新、代理支持与更多数据源（如 ArXiv、Kaggle Dataset）。
- 🧪 欢迎补充测试样例或将评分策略扩展到更多维度（如使用自然语言模型进行算分）。

## 📄 许可证
项目采用 MIT License 发布，具体条款见根目录下的 `LICENSE` 文件。

## ❓ 常见问题
- **GitHub API 速率受限？** 未配置令牌的公共请求有严格限流，可在环境变量 `GITHUB_TOKEN` 中设置个人令牌并在代码中拓展支持。
- **搜索结果为空？** 请检查网络环境或减少关键词数量；也可通过修改配置提升 `max_results`。
- **Excel 打不开？** 请确认已安装 `openpyxl`，并确保程序运行时无异常中断。

---

若在使用过程中遇到问题，欢迎提交 Issue 或直接补充 PR，共同完善自动化资源收集流程。