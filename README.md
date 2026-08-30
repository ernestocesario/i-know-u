# 👁️ I Know U

<p align="center">
  <img
    src="https://github.com/user-attachments/assets/ef0b088d-3008-4521-ba31-dca161129d81"
    alt="i-know-u_logo"
    width="450"
  />
</p>

<p align="center">
  <i>Every post tells a story you didn't mean to share...</i>
</p>

\
**I Know U** is an AI-powered OSINT (Open Source Intelligence) system designed to look beyond what users intentionally reveal on social media, automatically uncovering hidden narratives, private habits, behavioral patterns, and core values that they unknowingly leave behind.

The project imports publicly available profile data and content, analyzes images and videos with an LLM, stores both structured and semantic representations, and exposes an interface through which an analyst can ask questions about a profile or generate a comprehensive report.

> This repository contains a university project focused on OSINT and Big Data Analytics and Reasoning.

---

## 📌 Overview

Every day, billions of stories and posts are uploaded to social media, creating a vast hidden ocean of unstructured data. **I Know U** tackles this challenge by turning social profiles into queryable insights.

Powered by multimodal artificial intelligence, the system turns the visual and textual content users share, including stories, posts, and highlights, into a detailed psychological profile. By connecting seemingly unrelated pieces of information, I-Know-U builds a comprehensive dossier of the target user, generates analytical reports, and provides an internal chat interface for querying the collected data and uncovering private or otherwise hidden facts.

What appears to be ordinary social media activity becomes a fragmented trail of clues, revealing aspects of a person's life they may never have explicitly shared.

The system is built around five stages:
1. **Data Collection & Structuring:** import profile information and social media content.
2. **Multimodal Content Processing:** analyze media with LLMs and generate descriptions plus structured semantic metadata.
3. **Semantic Hybrid Storage:** persist data across a relational database, the local file system, and a vector database.
4. **Semantic Query & Retrieval:** retrieve relevant context using semantic similarity and optional self-querying filters.
5. **Insight Extraction:** answer natural-language questions or generate a multi-section profile report.

---

## 🎥 Demo

Watch the following video to see i-Know-U in action.

https://github.com/user-attachments/assets/b591da36-97e6-4667-95dd-484836e6189f

---

## ✨ Features

### 🛡️ InstaMine Data Collection
To bypass social media's advanced anti-scraping measures, a dedicated data mining library called **InstaMine** was developed. It uses a modular, provider-based architecture, making the system resilient to bans and API changes since providers can be easily replaced.

### 🤖 Multimodal Content Processing
Social profiles are unstructured data mines. An AI pipeline powered by LLMs converts raw images into semantic narratives and assigns enum-based structured metadata (e.g., social context, activities, environment).

### 🎯 Semantic Filtering for Accurate Retrieval
Since RAG (Retrieval-Augmented Generation) alone can mislead LLMs with irrelevant context, the system employs a **self-querying retrieval strategy**. The LLM first suggests semantic filters based on the user's question, which are applied to select the correct context from the vector database before generating the final answer.

### 📊 Insight Extraction
*   **Simple Querying:** Ask open-ended questions about a user to extract personal facts without hallucinations.
*   **Report Generation:** Compile a comprehensive dossier covering multiple aspects of a user's private life using batch prompting and a map-reduce pattern.

---

## 🏗️ Data Architecture

The project utilizes a highly optimized **Semantic Hybrid Storage** architecture:

### 1. SQLite (Relational Database)
Manages structured relationships and AI-inferred metadata for posts, stories, highlights, and user profiles.
*   **Integrity:** Enforces foreign keys to ensure no analysis data is orphaned.
*   **Efficiency:** Uses native NULLs to save space compared to schema-less NoSQL alternatives.
*   **Re-usability:** Stores raw text descriptions, allowing vector regeneration (e.g., upgrading the embedding model) without reprocessing the original media.

### 2. Local File Storage
Houses the physical files of imported posts, stories, and highlights.
*   **Decoupled Analysis:** Separates acquisition from analysis, allowing infinite reprocessing without hitting rate limits or risking IP bans.
*   **Performance:** Prevents database bloating and query degradation that occurs when storing BLOBs directly in SQL.
*   **Cloud-Ready:** Easily scalable to AWS S3 or Google Cloud Storage by merely updating the file saving logic.

### 3. ChromaDB (Vector Database)
Contains AI-inferred metadata indexed as vectors to enable semantic queries and RAG workflows. 
Content is annotated with multiple semantic categories (Temporal & Environmental, Subject & Activity, Social & Contextual, Emotional & Stylistic) to maximize RAG precision and eliminate vector context noise.

---

## 🛠️ System Architecture

The system is designed as a modular pipeline, allowing for easy extension and maintenance:

### 1. ⛏️ Data Collection and Structuring
To download structured data from social media platforms, a separate project called InstaMine was developed.\
It performs data mining through a modular, provider based architecture that leverages multiple data sources.

This modular provider approach makes the system resilient to bans and API changes, as providers can be replaced or updated without affecting the overall architecture.

### 2. 🖼️ Multimodal Content Processing
The system uses multimodal LLMs to analyze images and videos, generating both textual descriptions and structured semantic metadata.

Each metadata field corresponds to an enum value for categories such as social context, temporal and environmental context, and activities.

### 3. 📀 Semantic Hybrid Storage
Each piece of content is stored in a hybrid environment that combines a relational database for structured data, file storage for the physical media, and a vector database to support semantic querying and Retrieval-Augmented Generation (RAG) workflows.

### 4. 🔍 Semantic Query and Retrieval
The system employs a self-querying retrieval strategy to ensure that the LLM receives only relevant context.

When a user asks a question, the LLM first suggests semantic filters based on the question's content.\
These filters are then applied to select the appropriate context from the vector database before generating the final answer.
>Example:
> 
> **Question:** Does the user usually have a relationship in the summer?\
> **Filters:** `Season = SUMMER`, `SocialContext = COUPLE_ROMANTIC`

### 5. 🌋 Insight Extraction
The system can either answer specific questions or generate a comprehensive report on the target user.

- **Simple Querying:** The system allows asking open-ended questions about a user and extracting personal facts
- **Report Generation:**  The system can generate a comprehensive dossier on a user, covering multiple aspects of their private life, by using a batch of prompts and a map-reduce pattern.


---

## 🧩 Technology Stack

| Technology                    | Purpose                          |
|-------------------------------|----------------------------------|
| **Python 3.13**               | Main programming language        |
| **LLMs and Embedding models** | AI-powered vision and multimodal processing, semantic filtering, and RAG |
| **InstaMine**                 | Custom OSINT data mining library |
| **SQLite**                    | Relational metadata storage      |
| **ChromaDB**                  | Vector storage for RAG           |

---

## ⚙️ Requirements

You need:
* **Python 3.13**
* A valid **Google API key** (for Gemini AI and Embedding models)
* Internet access

---

## 🚀 Installation

> ### ⚠️ Warning
> 
> InstaMine is not yet publicly available, so the project cannot currently be installed.\
> To see the project in action, please refer to the [🎥 Demo](#demo) section.

### 1. Clone the repository
```bash
git clone https://github.com/ernestocesario/i-know-u.git
cd i-know-u
```

### 2. Create and activate a virtual environment

**Linux / macOS**

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

**Windows - Powershell**

```powershell
py -3.13 run.py -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows - Command Prompt (CMD)**
```cmd
py -3.13 run.py -m venv .venv
.venv\Scripts\activate.bat
```

### 3. Install the dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure the environment
Create a `.env` file in the project root by following the `.env.template` file.

### 5. Start the application
```bash
python main.py
```

---

## ⚠️ Limitations and Considerations

### Terms of Service & Ban Risks
Scraping social media platforms directly can violate their Terms of Service (ToS).\
Using **InstaMine** or this system on your personal network without adequate protective measures (such as VPNs, rotating proxies, or isolated environments) exposes your real IP address and personal accounts to severe risks, including permanent IP bans and account suspension. 

### AI Hallucinations & False Information
Despite the implementation of strict semantic filtering and self-querying RAG pipelines, Large Language Models (LLMs) are fundamentally probabilistic.\
The system can, and sometimes will, suffer from hallucinations. It may confidently generate false information, incorrect behavioral inferences, or completely fabricated insights about a user.\
The generated dossiers must be treated as AI-generated estimates, never as absolute truth or factual evidence.

### Data Privacy & Legal Constraints
While the scraped data might be "publicly accessible" on social media, downloading, storing, and systematically analyzing this data on your personal machine to extract private and undisclosed insights raises severe legal and ethical issues.\
Systematic profiling and the extraction of sensitive personal traits (such as religious beliefs, sexual orientation, or medical status) can strictly violate global privacy frameworks, including the **GDPR** in Europe.
> **Attention:** This project is provided strictly for educational and research purposes to demonstrate data leakage. You are solely responsible for the legal consequences of retaining and processing third-party personal data.

---

📚 Resources

- 🎞️ Slides: [project_presentation_slides.pdf](https://github.com/user-attachments/files/31599204/project_presentation_slides.pdf)
- 📐 ER Schema: [ER_schema.pdf](https://github.com/user-attachments/files/31599026/ER_schema.pdf)
- 🧩 File storage schema: [file_storage_schema.pdf](https://github.com/user-attachments/files/31599035/file_storage_schema.pdf)

---

## 👤 Repository

GitHub repository:
[ernestocesario/i-know-u](https://github.com/ernestocesario/i-know-u)
