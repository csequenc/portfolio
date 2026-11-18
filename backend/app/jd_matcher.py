import json
import re
from typing import Any

from .resume_data import RESUME_DATA


MAX_JD_LENGTH = 12000
MAX_SKILLS = 40
MAX_QUALIFICATIONS = 20

SKILL_WEIGHTS = {
    "required": 3.0,
    "preferred": 1.0,
}

MATCH_SCORES = {
    "strong",
    "partial",
    "missing",
}


def _extract_json(content: str) -> dict[str, Any]:
    """Parse a JSON response, including Markdown-wrapped JSON."""
    if not content:
        raise ValueError("The AI returned an empty response.")

    content = content.strip()

    content = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        content,
        flags=re.IGNORECASE,
    ).strip()

    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("The AI returned invalid JSON.") from exc

    if not isinstance(result, dict):
        raise ValueError("The AI response must be a JSON object.")

    return result


def _build_resume_context() -> str:
    """Build the resume context used for semantic comparison."""
    return json.dumps(
        RESUME_DATA,
        ensure_ascii=False,
        indent=2,
    )


def _call_llm(
    client: Any,
    model: str,
    prompt: str,
    max_tokens: int = 3500,
) -> dict[str, Any]:
    """Make one Groq request and parse its JSON response."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0.1,
        max_completion_tokens=max_tokens,
    )

    choice = response.choices[0]

    if choice.finish_reason == "length":
        raise ValueError(
            "The AI response was truncated. Increase the completion-token limit."
        )

    return _extract_json(choice.message.content)


# ---------------------------------------------------------
# STAGE 1: JOB DESCRIPTION REQUIREMENT EXTRACTION
# ---------------------------------------------------------

def extract_requirements(
    job_description: str,
    client: Any,
    model: str,
) -> dict[str, Any]:
    """
    Extract technical skills, education requirements,
    and experience requirements from a job description.
    """
    job_description = job_description.strip()

    if not job_description:
        raise ValueError("Please provide a job description.")

    if len(job_description) > MAX_JD_LENGTH:
        raise ValueError(
            f"Job description exceeds {MAX_JD_LENGTH} characters."
        )

    prompt = f"""
You are a job description requirement extractor.

Extract the actual requirements from the job description.

RULES:

1. Separate technical skills from education and experience.
2. Classify technical skills as required or preferred.
3. Extract individual skills rather than broad sentences.
4. Avoid duplicate skills.
5. Preserve important distinctions between related technologies.
6. Do not invent requirements that are not present in the JD.
7. Identify explicit education and experience requirements.
8. Return valid JSON only.

EXPECTED FORMAT:

{{
    "technical_skills": [
        {{
            "skill": "Python",
            "importance": "required"
        }},
        {{
            "skill": "Docker",
            "importance": "preferred"
        }}
    ],
    "education_requirements": [
        {{
            "requirement": "Bachelor's degree in Computer Science",
            "importance": "required"
        }}
    ],
    "experience_requirements": [
        {{
            "requirement": "Previous internship experience",
            "importance": "preferred"
        }}
    ]
}}

JOB DESCRIPTION:

{job_description}
"""

    result = _call_llm(
        client=client,
        model=model,
        prompt=prompt,
        max_tokens=3500,
    )

    skills = result.get("technical_skills", [])
    education = result.get("education_requirements", [])
    experience = result.get("experience_requirements", [])

    if not isinstance(skills, list):
        raise ValueError("Invalid technical skills extraction.")

    if not isinstance(education, list):
        raise ValueError("Invalid education extraction.")

    if not isinstance(experience, list):
        raise ValueError("Invalid experience extraction.")

    validated_skills = []

    for item in skills[:MAX_SKILLS]:
        if not isinstance(item, dict):
            continue

        skill = item.get("skill")
        importance = item.get("importance")

        if (
            isinstance(skill, str)
            and skill.strip()
            and importance in SKILL_WEIGHTS
        ):
            validated_skills.append({
                "skill": skill.strip(),
                "importance": importance,
            })

    def validate_qualifications(items: list) -> list[dict]:
        validated = []

        for item in items[:MAX_QUALIFICATIONS]:
            if not isinstance(item, dict):
                continue

            requirement = item.get("requirement")
            importance = item.get("importance")

            if (
                isinstance(requirement, str)
                and requirement.strip()
                and importance in ("required", "preferred")
            ):
                validated.append({
                    "requirement": requirement.strip(),
                    "importance": importance,
                })

        return validated

    return {
        "technical_skills": validated_skills,
        "education_requirements": validate_qualifications(education),
        "experience_requirements": validate_qualifications(experience),
    }


# ---------------------------------------------------------
# STAGE 2: INITIAL RESUME COMPARISON
# ---------------------------------------------------------

def compare_resume(
    extracted_requirements: dict[str, Any],
    client: Any,
    model: str,
) -> dict[str, Any]:
    """
    Compare extracted requirements against technical skills,
    education, and project experience documented in the resume.
    """
    resume_context = _build_resume_context()

    requirements_context = json.dumps(
        extracted_requirements,
        ensure_ascii=False,
        indent=2,
    )

    prompt = f"""
You are a strict resume-to-job-description matching analyst.

Compare the extracted job requirements against the candidate's resume.

RULES:

GENERAL MATCHING:

1. Use only information documented in the resume.
2. Recognize semantically equivalent technologies and concepts.
3. Do not require exact keyword matches.
4. Consider both the technical skills section and project contributions.
5. A skill appearing in a project technology list is evidence of exposure.
6. Strong means the resume demonstrates direct, relevant use.
7. Partial means related evidence exists, but the requirement is not
   fully demonstrated.
8. Missing means no relevant evidence is documented.
9. Never invent project experience, technologies, qualifications, or dates.
10. Do not mark a skill as strong merely because it is conceptually related.
11. Explain each match briefly.
12. Identify relevant projects when applicable.
13. Suggest what the candidate could learn or demonstrate to close a gap.
14. Do not assume that missing resume evidence means the candidate
    cannot perform the skill.

EDUCATION AND QUALIFICATION MATCHING:

15. Evaluate education requirements against the actual education details
    in the resume, not merely the degree title or subject.
16. Consider degree level, field of study, and completion status where relevant.
17. Pay attention to expected graduation dates and whether a qualification
    is completed or currently being pursued.
18. If the JD requires a completed degree and the resume shows it is ongoing,
    classify it as partial.
19. If the JD explicitly accepts candidates currently pursuing the degree,
    an ongoing qualification can be strong when other requirements are met.
20. Do not treat an ongoing degree as completed.
21. Do not assume a qualification exists unless it is documented.
22. Explain why the education requirement is strong, partial, or missing.

EXPERIENCE MATCHING:

23. Assess experience requirements using documented work experience
    and relevant project contributions.
24. Do not treat independent projects as industry employment or internships.
25. Do not infer professional experience from technical skills alone.
26. Explain missing experience evidence honestly.

27. Return valid JSON only.

EXPECTED FORMAT:

{{
    "technical_matches": [
        {{
            "skill": "Python",
            "importance": "required",
            "status": "strong",
            "resume_evidence": "Python is listed under programming languages.",
            "relevant_projects": ["MemoryMesh"],
            "gap": null
        }}
    ],
    "education_matches": [
        {{
            "requirement": "Bachelor's degree in Computer Science",
            "importance": "required",
            "status": "partial",
            "resume_evidence": "B.Tech, Computer Science and Engineering, expected May 2029.",
            "explanation": "The field matches, but the degree is still ongoing."
        }}
    ],
    "experience_matches": [
        {{
            "requirement": "Previous internship experience",
            "importance": "preferred",
            "status": "missing",
            "resume_evidence": null,
            "explanation": "No internship is documented in the resume."
        }}
    ],
    "overall_assessment": "A concise assessment of documented alignment."
}}

Allowed status values:
- strong
- partial
- missing

EXTRACTED JOB REQUIREMENTS:

{requirements_context}

CANDIDATE RESUME:

{resume_context}
"""

    result = _call_llm(
        client=client,
        model=model,
        prompt=prompt,
        max_tokens=6000,
    )

    for key in (
        "technical_matches",
        "education_matches",
        "experience_matches",
    ):
        if not isinstance(result.get(key), list):
            raise ValueError(f"Invalid comparison result: {key}")

    return result


# ---------------------------------------------------------
# STAGE 3: EVIDENCE CALIBRATION AND SCORE REVIEW
# ---------------------------------------------------------

def calibrate_technical_assessment(
    extracted_requirements: dict[str, Any],
    technical_matches: list[dict[str, Any]],
    client: Any,
    model: str,
) -> dict[str, Any]:
    """
    Re-evaluate technical matches and generate a holistic score
    using the strength, depth, and breadth of resume evidence.
    """
    requirements_context = json.dumps(
        extracted_requirements.get("technical_skills", []),
        ensure_ascii=False,
        indent=2,
    )

    matches_context = json.dumps(
        technical_matches,
        ensure_ascii=False,
        indent=2,
    )

    resume_context = _build_resume_context()

    prompt = f"""
You are an independent technical hiring evaluator reviewing an initial
resume-to-job-description assessment.

Your task is to CALIBRATE the technical matches and assign one overall
technical alignment score from 0 to 100.

Do not calculate the score by averaging the strong/partial/missing labels.
Do not apply a fixed points-per-skill formula.
Do not assume that many strong labels automatically mean a near-perfect fit.

Evaluate the complete evidence and use your judgment.

CALIBRATION PROCESS:

1. Re-check every technical match against the original resume.
2. Correct any status that is too generous or too harsh.
3. A strong match requires meaningful, relevant evidence of actual use.
4. A technology merely appearing in a skills list may show exposure, but
   should not automatically be treated as deep practical experience.
5. Distinguish implementation, experimentation, evaluation, and basic exposure.
6. Consider how directly each project demonstrates the requirement.
7. Consider the depth and substance of the candidate's contributions.
8. Consider the breadth of evidence across projects.
9. Inspect project overlap: several matched skills may all come from one project.
   Do not mistake repeated evidence from the same project for independent
   demonstrations of capability.
10. Do not automatically penalize a candidate for using one project to
    demonstrate several genuinely related skills. Judge the actual depth
    and relevance of that project.
11. Consider required versus preferred requirements. Missing a preferred
    skill should not carry the same significance as missing a central
    required skill.
12. Consider whether the candidate's projects demonstrate the ability to
    combine skills into working systems, not just list technologies.
13. Do not include education or industry experience in the technical score.
14. Do not infer skills or accomplishments that are absent from the resume.
15. The score should represent overall technical alignment with this JD,
    not hiring probability, general intelligence, or guaranteed job readiness.

SCORE CALIBRATION:

- Assign a score that reflects the overall quality of the evidence.
- A score near 100 should be reserved for exceptionally close alignment:
  nearly all important requirements are supported by convincing evidence,
  with meaningful depth and no substantial technical gaps.
- Strong alignment can still be below 100 when evidence is narrow, shallow,
  repetitive, or missing some meaningful requirements.
- Do not force the score to match a mathematical average of the statuses.
- Do not inflate the score to be encouraging.
- Do not lower it merely because multiple skills are demonstrated in one
  project; judge whether the project genuinely demonstrates those skills.
- Before returning the score, check whether it is consistent with the
  corrected matches and the evidence quality. Revise it if necessary.

Return valid JSON only, using this format:

{{
    "skill_score": 82,
    "score_rationale": "A concise explanation of the overall technical alignment and how project evidence breadth and depth affected the score.",
    "technical_matches": [
        {{
            "skill": "Python",
            "importance": "required",
            "status": "strong",
            "resume_evidence": "Evidence from the resume.",
            "relevant_projects": ["MemoryMesh"],
            "gap": null
        }}
    ]
}}

The score must be an integer from 0 to 100.
Allowed status values are strong, partial, and missing.
Return one match for every extracted technical requirement.
Do not add requirements that were not extracted.

EXTRACTED TECHNICAL REQUIREMENTS:

{requirements_context}

INITIAL TECHNICAL MATCHES:

{matches_context}

ORIGINAL CANDIDATE RESUME:

{resume_context}
"""

    result = _call_llm(
        client=client,
        model=model,
        prompt=prompt,
        max_tokens=6000,
    )

    score = result.get("skill_score")
    matches = result.get("technical_matches")
    rationale = result.get("score_rationale")

    if (
        not isinstance(score, int)
        or isinstance(score, bool)
        or not 0 <= score <= 100
    ):
        raise ValueError("The AI returned an invalid technical alignment score.")

    if not isinstance(matches, list):
        raise ValueError("The AI returned invalid calibrated technical matches.")

    if not isinstance(rationale, str) or not rationale.strip():
        raise ValueError("The AI did not explain its technical score.")

    return {
        "skill_score": score,
        "score_rationale": rationale.strip(),
        "technical_matches": matches,
    }


# ---------------------------------------------------------
# COMPLETE JD ANALYSIS
# ---------------------------------------------------------

def analyze_job_description(
    job_description: str,
    client: Any,
    model: str,
) -> dict[str, Any]:
    """
    Run requirement extraction, initial comparison,
    evidence calibration, and holistic technical scoring.
    """
    extracted = extract_requirements(
        job_description=job_description,
        client=client,
        model=model,
    )

    comparison = compare_resume(
        extracted_requirements=extracted,
        client=client,
        model=model,
    )

    initial_matches = comparison["technical_matches"]

    # Only retain matches for requirements actually extracted.
    extracted_skills = {
        (
            item["skill"].casefold(),
            item["importance"],
        )
        for item in extracted["technical_skills"]
    }

    valid_initial_matches = [
        item
        for item in initial_matches
        if (
            isinstance(item, dict)
            and isinstance(item.get("skill"), str)
            and (
                item["skill"].casefold(),
                item.get("importance"),
            ) in extracted_skills
            and item.get("status") in MATCH_SCORES
        )
    ]

    # Ensure every extracted skill is represented before calibration.
    returned_keys = {
        (item["skill"].casefold(), item["importance"])
        for item in valid_initial_matches
    }

    for skill in extracted["technical_skills"]:
        key = (skill["skill"].casefold(), skill["importance"])

        if key not in returned_keys:
            valid_initial_matches.append({
                "skill": skill["skill"],
                "importance": skill["importance"],
                "status": "missing",
                "resume_evidence": None,
                "relevant_projects": [],
                "gap": "No match was returned for this requirement.",
            })

    # Ask the model to review its own initial assessment and score holistically.
    calibrated = calibrate_technical_assessment(
        extracted_requirements=extracted,
        technical_matches=valid_initial_matches,
        client=client,
        model=model,
    )

    calibrated_matches = calibrated["technical_matches"]

    # Validate calibrated matches and prevent the evaluator from adding
    # requirements that were not extracted from the job description.
    valid_matches = [
        item
        for item in calibrated_matches
        if (
            isinstance(item, dict)
            and isinstance(item.get("skill"), str)
            and (
                item["skill"].casefold(),
                item.get("importance"),
            ) in extracted_skills
            and item.get("importance") in SKILL_WEIGHTS
            and item.get("status") in MATCH_SCORES
        )
    ]

    # The score and calibrated matches must describe the same requirement set.
    # Fail explicitly rather than silently adding missing matches after scoring.
    calibrated_keys = {
        (item["skill"].casefold(), item["importance"])
        for item in valid_matches
    }

    if calibrated_keys != extracted_skills:
        raise ValueError(
            "The calibration step did not return exactly one valid match "
            "for every extracted technical requirement."
        )

    if len(valid_matches) != len(calibrated_keys):
        raise ValueError(
            "The calibration step returned duplicate technical matches."
        )

    return {
        "skill_score": calibrated["skill_score"],
        "score_label": "Technical Skill Match",
        "score_rationale": calibrated["score_rationale"],
        "extracted_requirements": extracted,
        "technical_matches": valid_matches,
        "education_matches": comparison["education_matches"],
        "experience_matches": comparison["experience_matches"],
        "overall_assessment": comparison.get(
            "overall_assessment",
            "",
        ),
    }
