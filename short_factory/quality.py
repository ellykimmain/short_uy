import re


def score_brief(brief: dict, duration: int) -> dict:
    hook = str(brief.get("hook", ""))
    narration = str(brief.get("narration", ""))
    title = str(brief.get("title", ""))
    visual = str(brief.get("visual_prompt", ""))

    hook_score = 100
    if len(hook) < 18:
        hook_score -= 15
    if len(hook) > 110:
        hook_score -= 10
    if not re.search(r"\?|\bwhy\b|\bwhat\b|\bif\b|\bdon't\b|\bnever\b", hook, re.I):
        hook_score -= 10

    target_words = max(25, int(duration * 2.2))
    word_count = len(narration.split())
    pacing_score = max(45, 100 - abs(word_count - target_words) * 2)
    visual_score = 100 if len(visual) >= 80 else 75 if len(visual) >= 35 else 55
    title_score = 100 if 20 <= len(title) <= 90 else 80
    loop_score = 100 if re.search(r"\b(reset|again|return|notice|listen|breathe|repeat)\b", narration, re.I) else 75

    overall = round(hook_score * 0.30 + pacing_score * 0.20 + visual_score * 0.20 + title_score * 0.10 + loop_score * 0.20)
    return {
        "hook": max(0, hook_score),
        "pacing": max(0, min(100, pacing_score)),
        "visual": visual_score,
        "title": title_score,
        "loop": loop_score,
        "overall": overall,
        "pass": overall >= 78,
    }
