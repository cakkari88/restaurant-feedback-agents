\# Restaurant Customer Feedback Multi-Agent System



A local, terminal-based capstone demonstrating a six-agent restaurant customer feedback processing system orchestrated with LangGraph, powered by a local Ollama model, and integrated with the Model Context Protocol (MCP).



The system retrieves restaurant reviews, analyzes sentiment, classifies feedback, identifies recurring issues, stores completed analyses in SQLite through MCP, drafts customer replies, and requires human approval before any response can be used.



\*\*The system does not automatically publish or send customer replies.\*\*



\---



\## Architecture



The system uses six specialized agents connected through a sequential LangGraph workflow.



1\. \*\*Feedback Retrieval Agent\*\* — retrieves reviews through the MCP `retrieve\_feedback` tool.

2\. \*\*Feedback Analysis Agent\*\* — produces a short summary and sentiment.

3\. \*\*Classification Agent\*\* — classifies each review into a restaurant feedback category and saves the completed analysis through MCP.

4\. \*\*Recurring-Issue Agent\*\* — counts categories and identifies repeated negative/mixed themes.

5\. \*\*Response Drafting Agent\*\* — drafts a courteous customer reply without promising compensation or inventing actions.

6\. \*\*Management Review Agent\*\* — applies deterministic safety checks and marks every draft as requiring human approval.



\### Workflow



```text

&#x20;                   LangGraph Workflow

&#x20;                           |

&#x20;                           v

&#x20;                   Retrieval Agent

&#x20;                           |

&#x20;                           v

&#x20;                MCP: retrieve\_feedback

&#x20;                           |

&#x20;                           v

&#x20;                    Customer Reviews

&#x20;                           |

&#x20;                           v

&#x20;                    Analysis Agent

&#x20;                           |

&#x20;                           v

&#x20;                 Classification Agent

&#x20;                           |

&#x20;                           v

&#x20;             MCP: save\_feedback\_analysis

&#x20;                           |

&#x20;                           v

&#x20;                      SQLite

&#x20;                           |

&#x20;                           v

&#x20;                Recurring-Issue Agent

&#x20;                           |

&#x20;                           v

&#x20;                Response Drafting Agent

&#x20;                           |

&#x20;                           v

&#x20;                Management Review Agent

&#x20;                           |

&#x20;                           v

&#x20;               HUMAN APPROVAL REQUIRED

```



Historical feedback can be accessed through:



```text

MCP: search\_feedback\_history

MCP: calculate\_feedback\_statistics

```



\---



\## Technologies



\* Python

\* LangChain

\* LangGraph

\* Ollama

\* Gemma 4 (`gemma4:e4b`)

\* Model Context Protocol (MCP)

\* SQLite

\* CSV

\* pytest



\---



\## Requirements



\* Windows 10/11

\* Python 3.10 or 3.11 recommended

\* Ollama installed and running locally

\* Git installed for publishing to GitHub



\---



\## Setup on Windows



Open a terminal in the project folder.



Create the virtual environment:



```powershell

py -3.11 -m venv .venv

```



Activate it:



```powershell

.\\.venv\\Scripts\\Activate.ps1

```



If PowerShell blocks activation:



```powershell

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\\.venv\\Scripts\\Activate.ps1

```



Install the dependencies:



```powershell

python -m pip install -r requirements.txt

```



The project uses the MCP 1.x API because the server uses `FastMCP`.



If necessary:



```powershell

python -m pip install "mcp<2"

```



\---



\## Ollama



Make sure Ollama is installed and running.



Check the available models:



```powershell

ollama list

```



The project uses:



```text

gemma4:e4b

```



If necessary:



```powershell

ollama pull gemma4:e4b

```



Ollama normally runs locally at:



```text

http://localhost:11434

```



\---



\## Environment Configuration



Create a local environment file from the example:



```powershell

Copy-Item .env.example .env

```



Edit `.env` only if your local Ollama configuration differs.



Do not commit `.env` to GitHub.



\---



\# Running the Application



Activate the virtual environment:



```powershell

.\\.venv\\Scripts\\Activate.ps1

```



Run:



```powershell

python main.py

```



The application provides two options:



```text

\[1] Analyze sample CSV reviews

\[2] Analyze one review

```



The first run may take some time because the local Ollama model generates the analysis and response drafts.



\---



\# MCP Integration



The LangGraph workflow is connected to the MCP server through `mcp\_client.py`.



The MCP client launches the local MCP server through the standard input/output transport and calls the server tools as required by the workflow.



The main MCP data flow is:



```text

LangGraph

&#x20;   |

&#x20;   v

MCP Client

&#x20;   |

&#x20;   v

MCP Server

&#x20;   |

&#x20;   +--> retrieve\_feedback

&#x20;   |

&#x20;   +--> save\_feedback\_analysis

&#x20;   |

&#x20;   +--> search\_feedback\_history

&#x20;   |

&#x20;   +--> calculate\_feedback\_statistics

```



The MCP server is implemented in:



```text

restaurant\_server.py

```



The MCP client used by the LangGraph workflow is:



```text

mcp\_client.py

```



The MCP server does not publish reviews online.



\---



\# MCP Tools



The MCP server exposes four tools.



\## `retrieve\_feedback`



Retrieves customer reviews from the local `feedback.csv` dataset.



Example:



```powershell

python -c "from mcp\_client import retrieve\_feedback; print(retrieve\_feedback(3))"

```



\---



\## `save\_feedback\_analysis`



Stores a completed feedback analysis in the local SQLite database.



Stored information includes:



\* feedback ID

\* customer text

\* sentiment

\* category

\* summary

\* creation timestamp



The database file is:



```text

feedback.db

```



\---



\## `search\_feedback\_history`



Searches previously saved analyses by review text, category, sentiment, or summary.



Example:



```powershell

python -c "from mcp\_client import search\_feedback\_history; print(search\_feedback\_history('service', 10))"

```



\---



\## `calculate\_feedback\_statistics`



Calculates aggregate statistics from saved analyses.



Example:



```powershell

python -c "from mcp\_client import calculate\_feedback\_statistics; print(calculate\_feedback\_statistics())"

```



\---



\# Historical Memory



The system uses SQLite as local historical memory.



The workflow saves completed analyses through MCP.



For example, after processing 10 reviews:



```text

total\_saved\_analyses: 10

```



The historical database can then be queried independently of the original CSV retrieval.



\---



\# Six Specialized Agents



\## 1. Feedback Retrieval Agent



Retrieves restaurant feedback through the MCP `retrieve\_feedback` tool.



The agent supports:



\* sample feedback retrieval

\* manual review input



\---



\## 2. Feedback Analysis Agent



Uses the local Ollama model to:



\* summarize each review

\* identify sentiment

\* treat customer review text as untrusted data

\* avoid following instructions embedded inside reviews



Allowed sentiment values are:



```text

positive

negative

mixed

neutral

uncertain

```



\---



\## 3. Classification Agent



Classifies each review into one of the following categories:



```text

food\_quality

service

cleanliness

price

atmosphere

other

uncertain

```



After classification, the completed analysis is saved through:



```text

MCP: save\_feedback\_analysis

```



\---



\## 4. Recurring-Issue Agent



Uses deterministic frequency counting to identify recurring categories and negative/mixed issues.



It reports:



\* number of processed reviews

\* category counts

\* negative/mixed counts by category

\* recurring issues



The current recurring-issue method is a frequency heuristic and does not attempt to establish causal relationships.



\---



\## 5. Response Drafting Agent



Uses the local Ollama model to generate a short and courteous response draft.



The agent is instructed not to:



\* promise refunds

\* promise compensation

\* claim that an action has already happened

\* invent facts

\* repeat personal information



\---



\## 6. Management Review Agent



The final stage acts as a deterministic human-approval gate.



Every response is marked:



```text

needs\_review: true

```



The system produces drafts only.



No customer response is automatically published or sent.



\---



\# Safety



The system includes several safeguards.



\## Untrusted Review Text



Customer reviews are treated as untrusted input.



The analysis and classification prompts explicitly instruct the model not to follow commands contained inside customer feedback.



This helps protect against prompt injection through review content.



\## Output Validation



Sentiment and category values are checked against predefined allow-lists.



Invalid values are replaced with:



```text

uncertain

```



\## Response Restrictions



The response-drafting agent is instructed not to:



\* promise compensation

\* claim refunds have been issued

\* invent actions

\* expose personal information



\## Human Approval



The final management-review stage ensures that generated replies remain drafts.



A human must inspect and approve every response before it can be used.



\---



\# Example Evaluation



The provided 10-review sample produced the following category counts:



| Category     | Count |

| ------------ | ----: |

| Service      |     5 |

| Cleanliness  |     2 |

| Food quality |     2 |

| Price        |     1 |



Negative or mixed feedback:



| Category    | Count |

| ----------- | ----: |

| Service     |     4 |

| Cleanliness |     1 |

| Price       |     1 |



The recurring issue detected in this sample was service-related feedback.



The system successfully saved all 10 completed analyses to SQLite.



Historical search for:



```text

service

```



returned five previously saved service-related analyses.



The observed sentiment counts were:



| Sentiment | Count |

| --------- | ----: |

| Positive  |     4 |

| Negative  |     4 |

| Mixed     |     2 |



These values are based only on the provided sample dataset and should not be interpreted as representative evidence about a real restaurant.



\---



\# Testing



Run the automated tests with:



```powershell

python -m pytest -q

```



The tests should validate deterministic workflow behavior and safety safeguards.



MCP-specific functionality can also be tested directly.



\### Test MCP retrieval



```powershell

python -c "from mcp\_client import retrieve\_feedback; print(retrieve\_feedback(3))"

```



\### Test MCP statistics



```powershell

python -c "from mcp\_client import calculate\_feedback\_statistics; print(calculate\_feedback\_statistics())"

```



\### Test historical search



```powershell

python -c "from mcp\_client import search\_feedback\_history; print(search\_feedback\_history('service', 10))"

```



End-to-end testing should record:



\* model name

\* test set size

\* date

\* expected results

\* actual results

\* examples of failures

\* model settings



Do not invent evaluation scores.



\---



\# Evaluation Plan



A larger labeled test set can be used to evaluate:



\### Sentiment accuracy



```text

correct sentiment labels / total labeled reviews

```



\### Category accuracy



```text

correct category labels / total labeled reviews

```



\### Recurring-issue performance



Where labeled recurring themes are available, precision and recall can be measured.



\### Response quality



Generated replies can be evaluated using a rubric covering:



\* factuality

\* relevance

\* politeness

\* unsupported claims

\* safety



\### Workflow performance



Additional measurements can include:



\* workflow completion rate

\* MCP tool success rate

\* safety test outcomes

\* human-review compliance



\---



\# Limitations



\* The sample dataset is small and synthetic.

\* LLM-generated sentiment, summaries, classifications, and replies may contain errors.

\* The recurring-issue detector is based on simple category-frequency counting.

\* It does not perform advanced semantic clustering.

\* SQLite storage is local and is not encrypted in this sample.

\* The system does not automatically publish customer responses.

\* Human review remains necessary before generated replies are used.

\* The deterministic phrase checks are illustrative and cannot detect every unsafe response.

\* Evaluation results from the sample dataset should not be generalized to a real restaurant.



\---



\# Project Files



```text

restaurant\_feedback\_agents/

│

├── agents.py

├── graph.py

├── main.py

├── mcp\_client.py

├── restaurant\_server.py

├── feedback.csv

├── feedback.db              # generated locally; not committed

├── requirements.txt

├── test\_system.py

├── README.md

├── REPORT\_TEMPLATE.md

├── .env.example

└── .gitignore

```



\---



\# GitHub



Before publishing, check that the following are not committed:



```text

.env

feedback.db

.venv/

\_\_pycache\_\_/

\*.pyc

```



Initialize the repository:



```powershell

git init

```



Review the files:



```powershell

git add .

git status

```



Create the first commit:



```powershell

git commit -m "Build restaurant feedback multi-agent capstone"

```



Set the main branch:



```powershell

git branch -M main

```



Add the GitHub repository:



```powershell

git remote add origin https://github.com/YOUR-USERNAME/restaurant-feedback-agents.git

```



Push:



```powershell

git push -u origin main

```



Replace `YOUR-USERNAME` with your actual GitHub username.



Only include the real GitHub URL in the final report after the push succeeds.



\---



\# Human-in-the-Loop Principle



The system is designed as a decision-support tool rather than an autonomous customer-communication system.



The workflow ends with:



```text

AI-generated draft

&#x20;      |

&#x20;      v

Human review

&#x20;      |

&#x20;      v

Human approval

&#x20;      |

&#x20;      v

Potential use of response

```



No reply is automatically published or sent by the system.



