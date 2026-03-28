import os
from datetime import datetime, timezone

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def get_api_key():
    key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if not key:
        try:
            from .db import get_db
            conn = get_db()
            from .db import get_setting
            key = get_setting(conn, "gemini_api_key", "")
            conn.close()
        except Exception:
            pass
    return key


def configure_gemini(api_key=None):
    if not GEMINI_AVAILABLE:
        return {'success': False, 'error': 'google-generativeai package not installed'}
    
    key = api_key or get_api_key()
    if not key:
        return {'success': False, 'error': 'No Gemini API key configured. Set GEMINI_API_KEY environment variable or add in Settings.'}
    
    genai.configure(api_key=key)
    return {'success': True}


def get_model(model_name='gemini-2.0-flash'):
    if not GEMINI_AVAILABLE:
        return None
    return genai.GenerativeModel(model_name)


def generate_article(topic, sources, category='general', style='informative', word_count=800):
    config_result = configure_gemini()
    if not config_result['success']:
        return config_result
    
    sources_text = "\n".join([
        f"- {s.get('publisher', 'Source')}: {s.get('url', '')}"
        for s in sources
    ]) if sources else "No specific sources provided."
    
    prompt = f"""You are a Nigerian content writer creating articles for a news/blog site.

TOPIC: {topic}
CATEGORY: {category}
STYLE: {style}
TARGET WORD COUNT: {word_count}

SOURCES:
{sources_text}

Write a comprehensive article about this topic for a Nigerian audience. Structure it as follows:

## What happened
Summarize the key facts. Keep it factual and brief.

## What it means for Nigerians
Explain practical impact on daily life, costs, eligibility, or timelines. Be specific to Nigeria.

## What to do next
Provide clear next steps, official links (if relevant), and deadlines.

## FAQs
1. Who is affected?
2. What are the key dates?
3. Where is the official source?

## Sources
List the sources provided above.

IMPORTANT:
- Write in clear, accessible English
- Include relevant Nigerian context (naira prices, Nigerian institutions, etc.)
- Be factual, not sensational
- Do not fabricate facts or quotes
- Use proper formatting with markdown headings"""

    try:
        model = get_model()
        response = model.generate_content(prompt)
        
        return {
            'success': True,
            'content': response.text,
            'topic': topic,
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def improve_content(content, instructions='Improve clarity and flow'):
    config_result = configure_gemini()
    if not config_result['success']:
        return config_result
    
    prompt = f"""You are an editor improving an article. Here is the current content:

---
{content}
---

Instructions: {instructions}

Improve the content while:
- Keeping the same structure and format
- Preserving all factual information
- Maintaining the Nigerian audience focus
- Not adding fabricated facts

Return the improved content only, no explanations."""

    try:
        model = get_model()
        response = model.generate_content(prompt)
        
        return {
            'success': True,
            'content': response.text,
            'improved_at': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def generate_headline(topic, angle='news'):
    config_result = configure_gemini()
    if not config_result['success']:
        return config_result
    
    prompt = f"""Generate 5 compelling headlines for this topic for a Nigerian audience.

Topic: {topic}
Angle: {angle}

Return only the headlines, one per line, numbered 1-5."""

    try:
        model = get_model()
        response = model.generate_content(prompt)
        
        headlines = [
            line.strip()
            for line in response.text.strip().split('\n')
            if line.strip() and line.strip()[0].isdigit()
        ]
        headlines = [h.split('.', 1)[-1].strip() if '.' in h[:3] else h for h in headlines]
        
        return {
            'success': True,
            'headlines': headlines,
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def generate_excerpt(content, max_length=160):
    config_result = configure_gemini()
    if not config_result['success']:
        return config_result
    
    prompt = f"""Write a compelling excerpt/summary for this article in {max_length} characters or less.

Article:
{content[:2000]}

Return only the excerpt, no explanations."""

    try:
        model = get_model()
        response = model.generate_content(prompt)
        
        excerpt = response.text.strip()[:max_length]
        
        return {
            'success': True,
            'excerpt': excerpt,
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def generate_faqs(topic, context=''):
    config_result = configure_gemini()
    if not config_result['success']:
        return config_result
    
    prompt = f"""Generate 5 FAQs about this topic for a Nigerian audience.

Topic: {topic}
Context: {context or 'General information'}

Return as a numbered list with questions and answers in this format:
1. Q: [question]
   A: [answer]

Keep answers concise (1-2 sentences)."""

    try:
        model = get_model()
        response = model.generate_content(prompt)
        
        return {
            'success': True,
            'faqs': response.text,
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def test_connection():
    config_result = configure_gemini()
    if not config_result['success']:
        return config_result
    
    try:
        model = get_model()
        response = model.generate_content("Say 'Connection successful' if you can read this.")
        
        return {
            'success': True,
            'response': response.text,
            'tested_at': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
