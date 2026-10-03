# tkk---TechLearn

An interview-preparation library for senior data, AI, and quality-engineering roles. The repository is organized as four independent learning tracks, combining concept handbooks, interview question banks, SQL exercises, Python labs, and one small DataOps sample project.

## At a glance

| Track | Audience | Learning units | Main formats |
| --- | --- | ---: | --- |
| [Data Analyst](01-tkk---DA_Engineer/README.md) | Senior / Lead Data Analysts | 16 chapters | SQL and Python exercises |
| [Data Engineer](02-tkk---DataEngineer/README.md) | Senior / Staff Data Engineers | 22 handbooks | Markdown, Python, Databricks notebooks, runnable labs |
| [AI Engineer](03-tkk---AI_Engineer/README.md) | Senior / Staff AI and ML Engineers | 16 chapters | Python and SQL labs |
| [QA / Full-Stack Testing](04-tkk---QA_FullStack_Q%26A/README.md) | Senior Test Engineers, Test Architects, and Quality Engineers | 15 guides | Markdown interview guides |

Together, the tracks provide **69 chapters and handbooks**. They can be studied independently; the suggested sequence below is a roadmap, not a prerequisite imposed by the repository.

## Choose a track

### 1. Data Analyst

Start here for product analytics, experimentation, and analytics-engineering interviews. The 16 chapters cover:

- Advanced SQL, Pandas, statistics, A/B testing, and PySpark
- Data modeling, product metrics, cohort/retention analysis, and case studies
- Causal inference, dbt, BI/semantic layers, forecasting, cloud platforms, and analytics system design
- Senior behavioral and leadership preparation

Open the [Data Analyst track](01-tkk---DA_Engineer/README.md) or begin with [advanced SQL](01-tkk---DA_Engineer/Chapter_01_Advanced_SQL/01_window_functions.sql).

### 2. Data Engineer

This is the broadest track: 22 handbooks spanning foundations through production data systems.

- Python, PySpark/SQL, Git, DSA, cloud, Kafka, Airflow, dbt, and system design
- Behavioral interviewing, advanced DSA, production troubleshooting, AWS optimization, and ML data pipelines
- Data modeling, warehouse-grade SQL, lakehouse table formats, governance, DataOps, and distributed-systems fundamentals

The later handbooks include local practice programs and a [sample DataOps pipeline project](02-tkk---DataEngineer/21_DataOps_and_Infrastructure_Handbook/sample_pipeline_project) with Docker, Compose, Terraform, pytest tests, and a GitHub Actions workflow.

Open the [Data Engineer track](02-tkk---DataEngineer/README.md) or start with [Python fundamentals](02-tkk---DataEngineer/01_Python_Interview_Handbook/01_Basics.py).

### 3. AI Engineer

This 16-chapter track progresses from Python and core ML to production LLM systems.

- Python, ML fundamentals, neural networks, LLMs/GenAI, ML system design, MLOps, SQL for AI, and DSA
- LLM inference optimization, advanced RAG, agents and tool use, evaluation/observability, fine-tuning/alignment, safety, and distributed training
- Senior behavioral and negotiation practice

Chapters 09-16 are CPU-friendly runnable labs; they use only `numpy` where a third-party package is needed. Open the [AI Engineer track](03-tkk---AI_Engineer/README.md) or begin with [Python for AI](03-tkk---AI_Engineer/Chapter_01_Python_for_AI/01_python_for_ai.py).

### 4. QA / Full-Stack Testing

The QA track is a 15-guide interview library for senior quality-engineering and test-architecture roles:

- ETL, data warehouse, BI, big-data, and data-quality testing
- Python/Pandas and PySpark test automation; advanced SQL
- Web automation, Selenium, and Playwright
- AI, ML, AI-agent, and LLM testing

Open the [QA / Full-Stack Testing track](04-tkk---QA_FullStack_Q%26A/README.md) and follow its recommended study order.

## Recommended paths

| Goal | Suggested route |
| --- | --- |
| Product or business analytics | Complete the Data Analyst track; focus on SQL, metrics, experimentation, causal inference, and case studies. |
| Platform, batch, or streaming data engineering | Use the Data Analyst track for SQL/Python foundations if needed, then follow the Data Engineer handbooks in numerical order. |
| Applied ML, LLM applications, or ML infrastructure | Ensure you are comfortable with Python, SQL, and data systems, then follow the AI Engineer chapters in order. |
| Data, web, or AI quality engineering | Follow the QA guides in order; start with ETL/DWH/BI testing before automation and AI-focused testing. |

## Getting started

Clone the repository and work inside the folder for your selected track:

```bash
git clone https://github.com/techie-krishna-kayaking/tkk---TechLearn.git
cd tkk---TechLearn
```

The repository does not have one global runtime or application to launch. Install only the dependencies for the exercises you intend to run.

### Data Analyst exercises

```bash
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r 01-tkk---DA_Engineer/requirements.txt
```

Run Python files with `python <path-to-file>`. Run the `.sql` exercises in Databricks SQL or a compatible SQL environment as indicated in the lesson.

### Data Engineer practice labs

```bash
python -m venv .venv
# Activate the environment, then:
python -m pip install -r 02-tkk---DataEngineer/requirements_practice.txt
python 02-tkk---DataEngineer/18_Advanced_SQL_Handbook/02_Practice_Advanced_SQL.py
```

The real Delta Lake demo in handbook 19 additionally requires Java plus the optional `pyspark` and `delta-spark` packages documented in `requirements_practice.txt`.

To run the DataOps sample project's tests:

```bash
cd 02-tkk---DataEngineer/21_DataOps_and_Infrastructure_Handbook/sample_pipeline_project
python -m pip install -r requirements.txt
pytest -q
```

### AI Engineer runnable labs

```bash
python -m venv .venv
# Activate the environment, then:
python -m pip install -r 03-tkk---AI_Engineer/requirements_labs.txt
python 03-tkk---AI_Engineer/Chapter_10_Advanced_RAG/01_advanced_rag.py
```

The specialist labs are designed to run locally on CPU and do not require API keys or network access.

### QA / Full-Stack Testing guides

No package installation is needed to read the QA guides. Work through the Markdown files in the [track README](04-tkk---QA_FullStack_Q%26A/README.md), then implement the exercises in the tooling appropriate to your environment.

## Repository layout

```text
tkk---TechLearn/
|- 01-tkk---DA_Engineer/       # 16 Data Analyst chapters
|- 02-tkk---DataEngineer/      # 22 Data Engineer handbooks + DataOps sample project
|- 03-tkk---AI_Engineer/       # 16 AI Engineer chapters
|- 04-tkk---QA_FullStack_Q&A/  # 15 QA and test-architecture guides
`- README.md
```

## How to study effectively

1. Follow the modules in order unless you already have the stated prerequisite skills.
2. Run and modify the Python/SQL examples instead of only reading them.
3. Use the question banks to practise concise, trade-off-aware interview explanations.
4. For system-design and behavioral material, rehearse your answer aloud and connect it to measurable work you have done.
5. Treat compensation and role-level references in individual track documents as aspirational context, not guarantees.

## Notes for contributors

- Keep material within its track and preserve the numeric order of chapters and handbooks.
- Add any new dependency to the requirements file belonging to that track rather than creating a global dependency list.
- Do not commit virtual environments, build outputs, generated datasets, model files, or logs; the repository's `.gitignore` covers these common artifacts.

## License

No license file is currently included. Contact the repository owner before reusing the material outside the intended learning context.
