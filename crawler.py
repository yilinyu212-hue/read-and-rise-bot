import os, feedparser, google.generativeai as genai
from notion_client import Client

# 1. Load Secrets from GitHub Actions
notion = Client(auth=os.environ["NOTION_TOKEN"])
DATABASE_ID = os.environ["DATABASE_ID"]
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Use the latest flash model for speed and efficiency
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. RSS Sources (Top English Publications)
RSS_FEEDS = {
    "Economist": "https://www.economist.com/briefing/rss.xml",
    "The Atlantic": "https://www.theatlantic.com/feed/all/",
    "NYT": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "HBR": "https://hbr.org/rss/topic/leadership"
}

def analyze_and_push():
    for source_name, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        if not feed.entries: continue
        
        # Get the latest article from each source
        entry = feed.entries[0]
        
        # AI Prompt for Curation
        prompt = f"You are the curator for Read & Rise. Summarize the core idea of this article in Chinese (under 150 words) and determine the English difficulty level (A1-C2). Article Title: {entry.title}, Link: {entry.link}"
        
        try:
            response = model.generate_content(prompt)
            summary_text = response.text
        except Exception as e:
            summary_text = f"AI summary failed: {str(e)}"
        
        # 3. Create a page in your English Notion Database
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": entry.title}}]},
                "Source": {"select": {"name": source_name}},
                "Link": {"url": entry.link},
                "AI Summary": {"rich_text": [{"text": {"content": summary_text}}]},
                "Status": {"select": {"name": "To Read"}}
            }
        )
        print(f"✅ Successfully synced: {entry.title}")

if __name__ == "__main__":
    analyze_and_push()
