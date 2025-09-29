[中文版本](README.md) | **English**

# Automated Information Collection System (CUDA & HPC Resource Aggregator)

The Automated Information Collection System is designed to batch discover, filter, and organize high-quality learning resources related to CUDA and high-performance computing (HPC). The project fetches candidate links from DuckDuckGo search results and trending repositories on GitHub, applies multi-dimensional scoring and classification strategies, and exports the final results as structured Excel/CSV files for convenient study and sharing.

## ✨ Key Features
- **Multi-source search**: Leverages both DuckDuckGo and the GitHub API, supporting extended keywords in Chinese and English.
- **Automatic categorization**: Identifies books, courses, blogs, codebases, documentation, and more based on titles, descriptions, and URL patterns.
- **Quality assessment**: Combines metrics such as GitHub stars, last update time, official site domains, and description completeness to generate a quality score from 1 to 5.
- **Recommendation snippets**: Produces readable recommendation sentences for high-quality resources that highlight their strengths.
- **Data export**: Outputs categorized Excel files (one sheet per type) plus UTF-8 encoded CSV backups for direct sharing or downstream processing.
- **Flexible configuration**: Customize keywords, filters, output paths, and more via `config/config.yaml`.

## 📁 Project Structure
```
Automated Information Collection/
├─ config/                # YAML configuration files
├─ resources/             # Generated Excel/CSV resources (created by the program)
├─ src/
│  ├─ collector.py        # Search and collection logic
│  ├─ parsers.py          # Resource parsing, classification, and scoring
│  ├─ storage.py          # Excel/CSV writing and statistics
│  └─ main.py             # CLI entry point and orchestration
├─ main.py                # Example entry (delegates to src.main)
├─ pyproject.toml         # Project dependencies
├─ uv.lock                # uv lock file
└─ README.md
```

## 🚀 Getting Started
### Requirements
- Python 3.12 or newer
- Works on Windows, Linux, or macOS (default output supports Chinese content)
- When accessing the GitHub API, mind rate limits; a stable network connection is recommended

### Install Dependencies
> We recommend managing dependencies with [uv](https://github.com/astral-sh/uv), though built-in `pip` works as well.

**Using uv:**
```
uv sync
```

**Using pip:**
```
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

## ⚙️ Configuration
The default configuration lives in `config/config.yaml` and can be customized as needed:
- `search.keywords_zh / keywords_en`: Lists of Chinese and English keywords you can freely extend.
- `search.sources`: Enable or disable DuckDuckGo and GitHub searches, and set maximum result counts.
- `filters.min_quality_score`: Minimum quality score to keep when exporting results.
- `output.excel_file / csv_backup`: Output filenames and whether to create a CSV backup.
- `advanced.enable_proxy / proxy_url`: Enable proxy access when required.

If you don't need custom settings, the defaults work out of the box. To use a custom configuration file, pass `--config path/to/your.yaml` in the CLI.

## 🧪 Usage
Run the following commands from the project root:

- **Search and generate resources:**
  ```
  uv run python -m src.main search
  ```
  Or with your local Python environment:
  ```
  python -m src.main search
  ```
  You can append extra English keywords with `--keywords`, for example:
  ```
  python -m src.main search --keywords "GPU acceleration" "parallel training"
  ```

- **View Excel statistics:**
  ```
  python -m src.main stats
  ```

- **Attempt incremental updates (under development):**
  ```
  python -m src.main update --file cuda_hpc_resources.xlsx
  ```
  > Incremental merge logic is still evolving. The command loads the existing data and reruns a full search—watch for future updates.

All commands support `--config` to specify a custom configuration file, for example:
```
python -m src.main search --config config/custom.yaml
```

## 📊 Output
By default, the following files are generated under `resources/`:
- `cuda_hpc_resources.xlsx`:
  - `All Resources`: Complete result set (includes quality scores, recommendation notes, search keywords, etc.).
  - `Books / Courses / Blogs / Code / Docs`: Separate sheets generated only when the category contains data.
  - `Statistics`: Summary metrics such as counts, language distribution, source distribution, and score statistics.
  - `Top20 Resources`: The 20 highest-scoring resources in descending order.
- `cuda_hpc_resources.csv`: UTF-8 (with BOM) encoded backup ready for Excel or notebooks.

## 🔧 Development Notes
- ✅ Automatic deduplication, scoring, and recommendation generation are already implemented.
- 🚧 Enhancements planned for incremental updates, proxy support, and more data sources (e.g., ArXiv, Kaggle Datasets).
- 🧪 Contributions are welcome—add new tests or extend the scoring strategy with more dimensions (e.g., leveraging language models).

## 📄 License
This project is distributed under the MIT License. See the `LICENSE` file in the repository root for full terms.

## ❓ FAQ
- **GitHub API rate limited?** Unauthenticated requests have strict limits. Export your personal token as `GITHUB_TOKEN` and extend the code as needed.
- **Empty search results?** Check your network environment or reduce the number of keywords. You can also increase `max_results` in the config.
- **Excel won't open?** Ensure `openpyxl` is installed and confirm the program completes without exceptions.

---

If you run into any issues, feel free to open an issue or submit a PR to help improve the automated resource gathering workflow.
