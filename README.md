# 🏋️ AI Gym Equipment Recommender (RAG-Based)

## 📌 Original Project (Modules 1–3)
**Original Project Name:** Gym Equipment Recommender (Rule-Based)

The original version of this project was a simple rule-based system that recommended gym equipment based on predefined categories like muscle group or workout type. It relied on static mappings (e.g., chest → bench press equipment) and returned fixed outputs without adapting to user queries or context. While functional, it lacked flexibility, personalization, and any real use of AI.

---

## 🚀 Title & Summary

**AI Gym Equipment Recommender using Retrieval-Augmented Generation (RAG)**

This project is an AI-powered assistant that recommends gym equipment based on a user’s query. Instead of relying on hardcoded rules, it retrieves relevant information from a dataset and uses a language model to generate context-aware, human-like recommendations. This approach makes the system more flexible, scalable, and closer to real-world AI applications.

---

## 🧠 Architecture Overview

The system follows a simplified Retrieval-Augmented Generation (RAG) pipeline:

1. **User Query**  
   The user provides a natural language query (e.g., “best equipment for leg workouts at home”).

2. **Retriever (RAG)**  
   The system searches a structured dataset (CSV) using embeddings to find the most relevant equipment entries.

3. **Generator (LLM)**  
   The retrieved data is passed into a language model, which generates a recommendation using that information.

4. **Evaluator (Basic Testing Layer)**  
   The output is checked to ensure it references valid equipment and is not empty or irrelevant.

5. **Final Output**  
   The user receives a clear, explained recommendation.

Additionally, a human (developer/tester) evaluates outputs and improves the dataset or prompts over time.

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ai-gym-recommender.git
cd ai-gym-recommender