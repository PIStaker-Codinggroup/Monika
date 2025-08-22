import asyncio
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("monika")

class HumanLikeMemory:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        os.makedirs(self.folder_path, exist_ok=True)
        self.facts = {}
        self.load()

    def _sanitize_filename(self, key):
        # Replace spaces and special chars for safe filenames
        return "".join(c if c.isalnum() or c in "-_." else "_" for c in key)

    def learn(self, key, value):
        self.facts[key] = value
        filename = os.path.join(self.folder_path, self._sanitize_filename(key) + ".txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(value)

    def recall(self, key):
        return self.facts.get(key, "I don't remember that yet.")

    def update(self, key, value):
        if key in self.facts:
            self.learn(key, value)
            return True
        return False

    def all_facts(self):
        return self.facts.copy()

    def load(self):
        for fname in os.listdir(self.folder_path):
            if fname.endswith(".txt"):
                key = fname[:-4].replace("_", " ")
                with open(os.path.join(self.folder_path, fname), "r", encoding="utf-8") as f:
                    value = f.read().strip()
                    self.facts[key] = value

class HumanLikeAI:
    def __init__(self, memory):
        self.memory = memory

    async def handle(self, text):
        text = text.strip()
        if text.lower().startswith("learn"):
            # Format: learn <key>: <value>
            try:
                _, rest = text.split(" ", 1)
                key, value = rest.split(":", 1)
                key, value = key.strip(), value.strip()
                self.memory.learn(key, value)
                return f"I've learned that {key} is {value}."
            except Exception:
                return "To teach me, say: learn <key>: <value>"
        elif text.lower().startswith("recall"):
            # Format: recall <key>
            try:
                _, key = text.split(" ", 1)
                key = key.strip()
                value = self.memory.recall(key)
                return f"{key}: {value}"
            except Exception:
                return "To recall, say: recall <key>"
        elif text.lower().startswith("update"):
            # Format: update <key>: <value>
            try:
                _, rest = text.split(" ", 1)
                key, value = rest.split(":", 1)
                key, value = key.strip(), value.strip()
                if self.memory.update(key, value):
                    return f"I've updated {key} to {value}."
                else:
                    return f"I don't know {key} yet. Teach me first."
            except Exception:
                return "To update, say: update <key>: <value>"
        elif text.lower() == "facts":
            facts = self.memory.all_facts()
            if facts:
                return "\n".join([f"{k}: {v}" for k, v in facts.items()])
            else:
                return "I don't know anything yet."
        else:
            return "You can teach me with 'learn', ask me with 'recall', update with 'update', or list all with 'facts'."

async def main():
    memory = HumanLikeMemory("knowledge")
    ai = HumanLikeAI(memory)
    logger.info("Human-like AI started. Type your commands below.")
    while True:
        text = input("> ")
        reply = await ai.handle(text)
        print(reply)

if __name__ == "__main__":
    asyncio.run(main())
