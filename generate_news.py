import os
import datetime
import time
from google import genai
from google.genai import types

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("🚨 GEMINI_API_KEY environment variable not found!")

MODEL_NAME = "gemini-2.5-flash"  
client = genai.Client(api_key=API_KEY)

base_config = types.GenerateContentConfig(
    temperature=0.2,            
    top_p=0.9,
    top_k=40,
    max_output_tokens=8192,
    tools=[{'google_search': {}}]
)

ist_timezone = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
now = datetime.datetime.now(ist_timezone)

report_id_date = now.strftime("%Y%m%d")
full_date_str = now.strftime("%-d %B %Y")
time_str = now.strftime("%H:%M")

year_folder = now.strftime("%Y")
file_date_str = now.strftime("%Y-%m-%d")

os.makedirs(year_folder, exist_ok=True)

md_filepath = f"{year_folder}/GN-{file_date_str}.md"

# ==============================
# MERGED MAIN PROMPT (Sections 1-9, 11-13)
# ==============================
main_prompt = f"""
Act as a Senior Global Intelligence Analyst and Regional Expert. Provide news for {full_date_str}.
Format strictly as Markdown. Do not include introductory text. 

## SECTION 1 — Global Pulse
(Trending global geopolitics, wars, markets, events, summits - Format strictly as Markdown. 
Do not include introductory text. 
Most important text in concise without missing actual essence
The news consists of daily updates, political, geographical, tech updates, laws, incidents, events, 
visits and all other important news that daily international news paper have.)

## SECTION 2 — Gulf & MENA Region
(Major MENA regional news, Format strictly as Markdown. Do not include introductory text. 
Most important text in concise without missing actual essence.
The news consists of daily updates, political, geographical, tech updates, laws, incidents, events, 
visits and all other important news that daily regional news paper have. - 4-7 lines)

## SECTION 3 — Technology -  3- 6 lines 
(AI tools released today, major tech shifts, major changes in technology)

## SECTION 4 — Global Business & Industry -  4-7 lines 
(Business announcements, CEO statements, M&A, Business, Financial Updates)

## SECTION 5 — Global Security & Terrorism Monitor
(Terror, cyber warfare, espionage, attacks, wars, cyber crimes) 4-7 lines 

## SECTION 6 — Global Economy
(Stock markets, inflation, central banks, commodities) - 4-7 lines 

## SECTION 7 — India National
(Top national developments of last 24 hours in politics, economy, and governance)

## SECTION 8 — Telangana State Updates
(All major breaking news and updates in Telangana)

## SECTION 9 — Andhra Pradesh State Updates
(All major breaking news and updates in Andhra Pradesh)

## SECTION 11 — This Day in History (India)
(All major historical events that happened on this date in Indian history)
Including personalities Birthdays, Death Anniversaries, wars, attacks and More)

## SECTION 12 — Deep Analysis
(One major global or national important news from today explained in depth)

## SECTION 13 — Complete Summary
From all sections at least 2 lines of explanation or bulletins from all 1 to 12 sections for email brefieing and reading. 
I need 12 bulletins with two lines for each section! 
"""

# ==============================
# SEPARATE GOLD PROMPT (Section 10)
# ==============================
gold_prompt = f"""
Verify today's gold rates for Hyderabad from Goodreturns.in for {full_date_str}.
Provide output exactly in this format. Do not add introductory text.
Strictly from the website: https://www.goodreturns.in/gold-rates/hyderabad.html

## SECTION 10 — Gold Rates (Hyderabad Market)
- **24 Carat (10g):** ₹ amount (+/- ₹ difference amount compared to yesterday)
- **22 Carat (10g):** ₹ amount (+/- ₹ difference amount compared to yesterday)
- **Reason for Movement:**
"""

def fetch_clean_content(prompt_name, prompt_text):
    try:
        print(f"⏳ Generating {prompt_name}...")
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt_text,
            config=base_config
        )
        clean_text = response.text.replace("```markdown", "").replace("```html", "").replace("```", "").strip()
        
        # <-- BREATH ADDED HERE -->
        print("   💤 Pausing for 10 seconds to prevent API overload...")
        time.sleep(10)
        
        return clean_text
    except Exception as e:
        print(f"❌ Error in {prompt_name}: {e}")
        return f"Error generating {prompt_name}."

# 1. Fetch Main Report
main_content = fetch_clean_content("Main Intelligence Report", main_prompt)

# 2. Fetch Gold Report
gold_content = fetch_clean_content("Gold Rates (10)", gold_prompt)

# 3. Safely merge Gold into the middle of the Main Report
if "## SECTION 11" in main_content:
    final_content_body = main_content.replace("## SECTION 11", f"{gold_content}\n\n## SECTION 11")
else:
    final_content_body = main_content + "\n\n" + gold_content

# 4. Build Final Document
final_report = f"""# Global Daily Intelligence Briefing

Report ID: GN-{report_id_date}
Full Date: {full_date_str}
Report Time Reference: {time_str} (IST)
Region Coverage: Global | India | MENA | Technology | Economy
Report Generated By: Google Gemini 2.5 Flash 

---

{final_content_body}

-- END MAIN REPORT --
"""

with open(md_filepath, "w", encoding="utf-8") as f:
    f.write(final_report)
print(f"\nFinal Markdown saved flawlessly at: {md_filepath}")

# ==============================
# TELUGU EMAIL TRANSLATION
# ==============================
print("Generating Clean Telugu Email Summary...")
email_summary_path = "email_body.html"

summary_start = final_content_body.find("## SECTION 13")

if summary_start != -1:
    english_summary = final_content_body[summary_start:].strip()
    
    telugu_translation_prompt = f"""
    Translate this news summary into professional Telugu (Vaarthalu style).
    CRITICAL INSTRUCTION: Format the output STRICTLY as HTML list items (<li>).
    Do NOT use Markdown asterisks (*) or hyphens (-).
    Each news point MUST be wrapped in <li> tags. Bold the topic names using <b> tags.
    
    Example format:
    <li><b>ప్రపంచ పరిణామాలు: </b> ... </li>

    English Summary:
    {english_summary}
    """
    
    try:
        telugu_html_list = fetch_clean_content("Telugu Translation", telugu_translation_prompt)
        
        final_html = f"""
        <html>
          <body style="font-family: 'Gautami', Arial, sans-serif; line-height: 1.8; color: #333; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px; background-color: #fcfcfc;">
            <h2 style="color: #d32f2f; border-bottom: 2px solid #d32f2f; padding-bottom: 10px;">ఈరోజు ముఖ్యాంశాలు</h2>
            <p style="color: #444; font-weight: bold; font-size: 14px;">తేదీ: {full_date_str}</p>
            <ul style="padding-left: 20px; font-size: 15px;">
              {telugu_html_list}
            </ul>
            <hr style="border: 0; border-top: 1px solid #ddd; margin: 20px 0;">
            <p style="font-size: 12px; color: #888; text-align: center;">జెమిని తెలుగు వార్తా వాహిని ద్వారా రూపొందించబడింది</p>
          </body>
        </html>
        """
    except Exception as e:
        print(f"Telugu translation failed: {e}")
        final_html = f"<html><body><p>News Briefing for {full_date_str} is ready in GitHub.</p></body></html>"
else:
    final_html = f"<html><body><p>News Briefing for {full_date_str} is ready in GitHub.</p></body></html>"

with open(email_summary_path, "w", encoding="utf-8") as f:
    f.write(final_html)
print("Clean Telugu Email HTML saved successfully!")
