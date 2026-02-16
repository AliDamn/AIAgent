
AIAgent

> Автономный бизнес-аналитик агент на стеке LangChain + CrewAI.

---

Стек
* **Engine:** OpenAI GPT-4o
* **Frameworks:** LangChain, CrewAI
* **Env:** Python 3.10+

Быстрый старт
bash
git clone git@github.com:AliDamn/AIAgent.git
cd AIAgent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

Конфигурация

Создайте `.env`:

env
OPENAI_API_KEY=sk-...
# Дополнительно для CrewAI (опционально)
SERPER_API_KEY=your_serper_key 

Запуск

bash
python main.py

