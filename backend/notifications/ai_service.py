"""
AI service: classifies notifications and infers user mode in a single LLM call.
Uses Groq (llama-3.3-70b-versatile). Falls back to rule-based if Groq fails.
"""
import json
import os

from django.conf import settings


CLASSIFICATION_PROMPT = """You are an intelligent notification assistant embedded in a smart notification management system.

Given the following context about a user and an incoming notification, perform two tasks in ONE response:

1. CLASSIFY the notification:
   - priority: low | medium | high
   - category: social | work | urgent

2. INFER the user's current mode from their behaviour:
   - focus   → deep work (coding, writing, designing — productivity app active, focus block scheduled)
   - work    → general office activity (emails, browsing, meetings prep)
   - meeting → currently on a call or in a scheduled meeting block
   - relax   → leisure apps, breaks, watching videos, idle
   - sleep   → inactive for extended time or late-night hours (after 23:00 / before 06:00)

Guidelines:
- Weight the active app heavily: vscode/figma = focus, zoom/meet = meeting, youtube/netflix = relax
- Weight the schedule block: if a "meeting" block is active → meeting mode takes priority
- If the user has ignored 3+ notifications in 30 min → they are likely in focus/meeting, not relax
- Time of day matters: "late_night" or "early_morning" → lean toward sleep

USER CONTEXT:
- Name: {name}
- Role: {role}
- Persona: {persona_description}
- Current app: {app_name} (category: {app_category})
- Active schedule block: {block_type} — "{block_title}"
- Time of day: {time_of_day}
- Recent notification actions (last 5): {last_interactions}
- Ignored notifications in last 30 min: {recent_ignored_count}

INCOMING NOTIFICATION:
- Source: {source_app}
- Message: "{message}"

Respond ONLY with valid JSON — no markdown, no explanation outside the JSON:
{{
  "priority": "low|medium|high",
  "category": "social|work|urgent",
  "inferred_mode": "focus|work|meeting|relax|sleep",
  "ai_reason": "one or two sentences explaining priority, category, and mode inference"
}}"""


def _get_time_of_day(hour: int) -> str:
    if 6 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    elif 21 <= hour < 24:
        return "late_night"
    else:
        return "early_morning"


def build_prompt(context: dict) -> str:
    return CLASSIFICATION_PROMPT.format(**context)


def call_groq(prompt: str) -> dict:
    from openai import OpenAI
    client = OpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
    )
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=300,
    )
    raw = response.choices[0].message.content.strip()
    return json.loads(raw)



def classify_and_infer(context: dict) -> dict:
    """
    Main entry point. Returns:
      { priority, category, inferred_mode, ai_reason }
    Falls back gracefully if both AI providers fail.
    """
    prompt = build_prompt(context)

    if getattr(settings, 'GROQ_API_KEY', ''):
        try:
            return call_groq(prompt)
        except Exception as e:
            print(f"[AI] Groq failed: {e}")

    # Rule-based fallback
    return _rule_based_fallback(context)


def _rule_based_fallback(context: dict) -> dict:
    app_cat = context.get('app_category', 'productivity')
    block_type = context.get('block_type', 'free')
    time_of_day = context.get('time_of_day', 'afternoon')
    source = context.get('source_app', 'slack')
    ignored = context.get('recent_ignored_count', 0)

    # Infer mode
    if block_type == 'meeting':
        mode = 'meeting'
    elif time_of_day in ('late_night', 'early_morning'):
        mode = 'sleep'
    elif app_cat == 'leisure':
        mode = 'relax'
    elif app_cat == 'productivity' or ignored >= 3:
        mode = 'focus'
    else:
        mode = 'work'

    # Classify priority
    if source in ('github', 'calendar'):
        priority = 'high'
        category = 'urgent'
    elif source in ('slack', 'gmail'):
        priority = 'medium'
        category = 'work'
    else:
        priority = 'low'
        category = 'social'

    return {
        'priority': priority,
        'category': category,
        'inferred_mode': mode,
        'ai_reason': 'Rule-based fallback: AI providers unavailable.',
    }


def apply_decision_rules(inferred_mode: str, priority: str) -> dict:
    """
    Pure rule table — no AI. Returns { decision, delay_minutes }.
    """
    rules = {
        # (mode, priority) → (decision, delay_minutes)
        ('focus',   'low'):    ('block', 0),
        ('focus',   'medium'): ('delay', 30),
        ('focus',   'high'):   ('send',  0),
        ('meeting', 'low'):    ('block', 0),
        ('meeting', 'medium'): ('block', 0),
        ('meeting', 'high'):   ('delay', 15),
        ('work',    'low'):    ('delay', 10),
        ('work',    'medium'): ('send',  0),
        ('work',    'high'):   ('send',  0),
        ('relax',   'low'):    ('send',  0),
        ('relax',   'medium'): ('send',  0),
        ('relax',   'high'):   ('send',  0),
        ('sleep',   'low'):    ('block', 0),
        ('sleep',   'medium'): ('block', 0),
        ('sleep',   'high'):   ('delay', 480),  # delay until morning (~8h)
    }
    decision, delay_minutes = rules.get((inferred_mode, priority), ('send', 0))
    return {'decision': decision, 'delay_minutes': delay_minutes}
