import json, asyncio, edge_tts, os

DATA_FILE = "data/data.json"
AUDIO_DIR = "assets/audio"

async def gen(text, path):
    communicate = edge_tts.Communicate(text, "en-GB-RyanNeural")
    await communicate.save(path)

def main():
    os.makedirs(AUDIO_DIR, exist_ok=True)
    data = json.load(open(DATA_FILE, "r", encoding="utf-8"))["items"]

    for i, item in enumerate(data):
        fn = f"{AUDIO_DIR}/{i}.mp3"
        asyncio.run(gen(item["en_summary"], fn))
        item["audio"] = fn

    json.dump({"items": data}, open(DATA_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
