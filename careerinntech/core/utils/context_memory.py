def update_user_context(memory, message):
    msg = message.lower()

    # Branch
    if "ece" in msg:
        memory.branch = "ECE"
    elif "cse" in msg:
        memory.branch = "CSE"

    # Education level
    if "1st year" in msg or "first year" in msg:
        memory.education_level = "1st Year BTech"
    elif "2nd year" in msg or "second year" in msg:
        memory.education_level = "2nd Year BTech"
    elif "3rd year" in msg:
        memory.education_level = "3rd Year BTech"

    # Career goal
    if "ai engineer" in msg or "artificial intelligence" in msg:
        memory.career_goal = "AI Engineer"
    elif "data scientist" in msg:
        memory.career_goal = "Data Scientist"
    elif "software developer" in msg:
        memory.career_goal = "Software Developer"

    # Skills
    for skill in ["python", "ml", "django", "dsa", "react"]:
        if skill in msg:
            existing = memory.skills or ""
            if skill.capitalize() not in existing:
                memory.skills = (existing + ", " + skill.capitalize()).strip(", ")

    # Weak areas
    if "weak" in msg or "struggling" in msg:
        memory.weak_areas = message[:200]

    memory.save()
