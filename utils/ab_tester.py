"""
A/B Testing simulator for DevPulse draft scorer.
Compares headline variants and code hook effectiveness side-by-side.
"""

def compare_headlines(headlines: list[str], baseline_score: float = 75.0) -> dict:
    """
    Compare multiple headline variants against a baseline score.
    
    Args:
        headlines: List of headline strings to compare
        baseline_score: Baseline performance score (0-100)
    
    Returns:
        Dict with comparison results including variance from baseline
    """
    if not headlines:
        return {"error": "No headlines provided"}
    
    results = []
    for i, headline in enumerate(headlines):
        # Score factors
        length = len(headline)
        word_count = len(headline.split())
        has_action_verb = any(verb in headline.lower() for verb in 
                            ["build", "create", "learn", "master", "implement", "optimize"])
        has_keyword = any(kw in headline.lower() for kw in 
                         ["api", "tutorial", "guide", "python", "rest", "sdk"])
        
        # Calculate variance from baseline
        length_score = 100 if 40 <= length <= 70 else 70
        action_bonus = 15 if has_action_verb else 0
        keyword_bonus = 10 if has_keyword else 0
        
        score = baseline_score + action_bonus + keyword_bonus - (5 if length > 70 else 0)
        score = max(0, min(100, score))  # Clamp 0-100
        
        results.append({
            "headline": headline,
            "index": i + 1,
            "score": round(score, 1),
            "length": length,
            "word_count": word_count,
            "has_action_verb": has_action_verb,
            "has_keyword": has_keyword,
            "variance_from_baseline": round(score - baseline_score, 1)
        })
    
    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "headlines": results,
        "winner": results[0]["headline"] if results else None,
        "best_score": results[0]["score"] if results else 0,
        "average_score": round(sum(r["score"] for r in results) / len(results), 1) if results else 0
    }


def compare_code_hooks(hooks: list[str], language: str = "python") -> dict:
    """
    Compare code hook/snippet effectiveness for engagement.
    
    Args:
        hooks: List of code snippet strings to compare
        language: Programming language (python, javascript, etc.)
    
    Returns:
        Dict with engagement scores for each code hook
    """
    if not hooks:
        return {"error": "No code hooks provided"}
    
    results = []
    for i, hook in enumerate(hooks):
        lines = hook.strip().split('\n')
        code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        
        # Engagement factors
        is_runnable = any(keyword in hook for keyword in ["print(", "console.log(", "puts "])
        has_comments = any(line.strip().startswith('#') or line.strip().startswith('//') 
                          for line in lines)
        is_practical = any(keyword in hook.lower() for keyword in 
                          ["example", "import", "from", "require", "def ", "function"])
        
        # Calculate engagement score
        runnable_bonus = 20 if is_runnable else 10
        comment_bonus = 5 if has_comments else 0
        practical_bonus = 10 if is_practical else 0
        
        engagement_score = 60 + runnable_bonus + comment_bonus + practical_bonus
        engagement_score = max(0, min(100, engagement_score))
        
        results.append({
            "hook": hook[:100] + "..." if len(hook) > 100 else hook,
            "index": i + 1,
            "full_hook": hook,
            "engagement_score": round(engagement_score, 1),
            "code_lines": code_lines,
            "is_runnable": is_runnable,
            "has_comments": has_comments,
            "is_practical": is_practical,
            "language": language
        })
    
    # Sort by engagement_score descending
    results.sort(key=lambda x: x["engagement_score"], reverse=True)
    
    return {
        "hooks": results,
        "winner": results[0]["hook"] if results else None,
        "best_engagement": results[0]["engagement_score"] if results else 0,
        "average_engagement": round(sum(r["engagement_score"] for r in results) / len(results), 1) if results else 0
    }


def ab_test_summary(headlines_results: dict, hooks_results: dict) -> dict:
    """
    Generate A/B test summary combining headline and code hook results.
    
    Args:
        headlines_results: Output from compare_headlines()
        hooks_results: Output from compare_code_hooks()
    
    Returns:
        Combined A/B test summary with recommendations
    """
    return {
        "headline_winner": headlines_results.get("winner", "N/A"),
        "headline_best_score": headlines_results.get("best_score", 0),
        "code_hook_winner": hooks_results.get("winner", "N/A"),
        "code_hook_best_engagement": hooks_results.get("best_engagement", 0),
        "combined_recommendation": {
            "headline": f"Use: {headlines_results.get('winner', 'N/A')}",
            "code_hook": f"Lead with: {hooks_results.get('winner', 'N/A')[:80]}...",
            "overall_score": round(
                (headlines_results.get("best_score", 0) * 0.4 + 
                 hooks_results.get("best_engagement", 0) * 0.6), 1
            )
        }
    }
