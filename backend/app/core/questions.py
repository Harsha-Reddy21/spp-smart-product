"""
SAGE Questions Registry — single source of truth for all 22 AI governance questions.
Suggestions[] mirrors sage_ai_suggestions.csv and drives scoring + agent follow-ups.
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ConditionalOn:
    qid: str
    kws: List[str]


@dataclass
class Question:
    id: str
    panel: str               # "user" | "system" | "tech"
    field: str               # camelCase field name
    label: str
    mandatory: bool
    weight: float
    q: str                   # Question text shown to user
    suggestions: List[str]   # From sage_ai_suggestions.csv — drives scoring
    hints: List[str]
    is_conditional_trigger: bool = False
    conditional_on: Optional[ConditionalOn] = None


QUESTIONS: List[Question] = [
    # ── USER PANEL ────────────────────────────────────────────────────────────
    Question("AI-Q1", "user", "systemName", "AI System Name", False, 0.03,
        "What is the name of your AI system?",
        ["Provide a concise name that clearly reflects the system's domain and purpose"],
        ["Clear descriptive name", "Reflects domain/purpose"]),

    Question("AI-Q2", "user", "ownerName", "Business Owner", False, 0.03,
        "Who is the business owner responsible for this AI system?",
        ["Identify the business owner by full name, their business unit, department, and the team involved"],
        ["Full name", "Business unit", "Department", "Team"]),

    Question("AI-Q3", "user", "contactEmail", "Contact Email", False, 0.02,
        "What is the primary contact email for this submission?",
        ["Provide a valid business email address as the point of contact for follow-ups"],
        ["Valid business email"]),

    # ── SYSTEM PANEL ─────────────────────────────────────────────────────────
    Question("AI-Q4", "system", "problemStatement", "Problem Statement", False, 0.06,
        "What problem or business opportunity does your AI system address?",
        ["Provide a concise 2-3 sentence description of the AI solution covering what it does, its intended business purpose, target users, and whether it is new or enhances existing capability",
         "Identify the business process or workflow that the AI solution supports"],
        ["Articulate the pain point", "Quantify business impact", "Who is affected", "Current vs desired state"]),

    Question("AI-Q5", "system", "aiSolution", "AI Solution", False, 0.06,
        "Describe your AI solution — how it works and what it does.",
        ["Provide a concise 2-3 sentence description of the AI solution covering what it does, its intended business purpose, target users, and whether it is new or enhances existing capability",
         "Explain how the AI solution integrates with existing systems"],
        ["Plain-language description", "Core AI/ML capabilities", "Inputs and outputs"]),

    Question("AI-Q6", "system", "valueProposition", "Value Proposition", True, 0.12,
        "What is the expected business value and impact of this AI system?",
        ["Provide a concise 2-3 sentence description of the AI solution covering what it does, its intended business purpose, target users, and whether it is new or enhances existing capability",
         "Specify the deployment model (SaaS vendor-hosted, self-hosted, or hybrid) and indicate if alternative hosting options are available"],
        ["Quantify ROI or cost savings", "Impact on users", "Short and long-term benefits", "Specific KPIs"]),

    Question("AI-Q7", "system", "targetUsers", "Target Users", True, 0.08,
        "Who are the primary users or beneficiaries of this AI system?",
        ["Provide a concise 2-3 sentence description of the AI solution covering what it does, its intended business purpose, target users, and whether it is new or enhances existing capability",
         "Identify the key stakeholders for the AI solution"],
        ["Internal vs external users", "User roles", "Estimated number affected", "Key stakeholders"]),

    Question("AI-Q13", "system", "explainability", "Explainability", False, 0.04,
        "How explainable is your AI system's decision-making?",
        ["Describe how decisions made by the AI are explained to end users",
         "Identify any explainability tools used (e.g. SHAP, LIME)"],
        ["How decisions are explained", "Explainability tools", "User-facing explanations"]),

    Question("AI-Q14", "system", "humanOversight", "Human Oversight", False, 0.04,
        "What human oversight and control mechanisms are in place?",
        ["Describe human-in-the-loop processes, override capabilities, escalation paths, and monitoring"],
        ["Human-in-the-loop", "Override capabilities", "Escalation paths"]),

    Question("AI-Q15", "system", "usesPersonalData", "Uses Personal Data", False, 0.02,
        "Does this AI system use, process, or generate personal data? (Yes / No)",
        ["Confirm whether the use case processes any Personal Information (PI), Confidential Information (CI), or only uses public/non-sensitive data (green/yellow classification)"],
        ["Yes or No", "Personal data includes names, emails, IDs, location, behaviour"],
        is_conditional_trigger=True),

    Question("AI-Q16", "system", "riskAssessment", "Risk Assessment", False, 0.05,
        "What are the key risks associated with this AI system?",
        ["Identify model failure modes, bias risks, adversarial attack vectors, and regulatory/reputational risks"],
        ["Model failure modes", "Bias risks", "Regulatory risks"]),

    Question("AI-Q17", "system", "riskMitigation", "Risk Mitigation", True, 0.10,
        "What specific controls and mitigations manage AI risks?",
        ["Describe bias detection and mitigation measures",
         "Explain model drift monitoring and retraining approach",
         "Detail fallback mechanisms and human review triggers"],
        ["Bias detection", "Model drift monitoring", "Fallback mechanisms", "Human review triggers"]),

    Question("AI-Q18", "system", "testingValidation", "Testing & Validation", False, 0.04,
        "How has this AI system been tested and validated?",
        ["Describe evaluation datasets, fairness and bias testing, performance metrics, and user acceptance testing"],
        ["Evaluation datasets", "Fairness testing", "Performance metrics", "UAT"]),

    Question("AI-Q20", "system", "personalDataDetails", "Personal Data Details", True, 0.06,
        "Describe what personal data is processed and the legal basis.",
        ["Confirm the data classification level and whether the use case processes any Personal Information (PI), Confidential Information (CI), or only uses public/non-sensitive data (green/yellow classification)"],
        ["Categories of personal data", "Legal basis (GDPR)", "Data minimization", "Retention and deletion"],
        conditional_on=ConditionalOn("AI-Q15", ["yes"])),

    # ── TECH PANEL ───────────────────────────────────────────────────────────
    Question("AI-Q8", "tech", "technicalApproach", "Technical Approach", False, 0.05,
        "What AI/ML techniques, models, or frameworks does your system use?",
        ["Identify the data sources used by the AI solution",
         "Provide a concise description of the AI/ML models, algorithms, and technology stack deployed"],
        ["Models or algorithms", "Training data", "Technology stack", "Deployment"]),

    Question("AI-Q9", "tech", "dataDescription", "Data Description", False, 0.05,
        "What data does this AI system use? Describe sources, types, and volumes.",
        ["Identify the data sources used by the AI solution",
         "Describe data types (structured/unstructured), volume, and update frequency"],
        ["All data sources", "Data types", "Volume and update frequency", "Data quality"]),

    Question("AI-Q10", "tech", "integrations", "Integrations", False, 0.03,
        "What systems or APIs does this AI system integrate with?",
        ["Explain how the AI solution integrates with existing systems",
         "Identify upstream and downstream system dependencies and integration methods"],
        ["Upstream and downstream dependencies", "Integration method", "Cloud platforms"]),

    Question("AI-Q11", "tech", "scalability", "Scalability", False, 0.03,
        "How does your system handle scale and performance requirements?",
        ["Describe the expected load, scaling approach, latency, throughput, and failover strategy"],
        ["Expected load", "Scaling approach", "Latency and throughput", "Failover"]),

    Question("AI-Q12", "tech", "dataPrivacy", "Data Privacy & Security", True, 0.10,
        "How does your AI system handle data privacy, security, and compliance?",
        ["Provide a concise 2-3 sentence description of the AI solution covering what it does, its intended business purpose, target users, and whether it is new or enhances existing capability",
         "Identify the regulatory requirements applicable to the AI solution"],
        ["PII handling and anonymization", "Encryption", "Regulatory compliance (GDPR, HIPAA)", "Access controls", "Audit logging"]),

    Question("AI-Q19", "tech", "deploymentPlan", "Deployment Plan", False, 0.03,
        "What is your deployment plan and rollout strategy?",
        ["Describe the phased rollout approach, pilot testing plan, rollback strategy, and expected go-live timeline"],
        ["Phased rollout", "Pilot testing", "Rollback plan", "Go-live timeline"]),

    Question("AI-Q22", "tech", "dataAuditApproach", "Data Audit Approach", True, 0.04,
        "How do you audit data usage? All data or sampling? (No / Yes - all data / Yes - a sampling)",
        ["Verify whether any AI functionality impacts patient safety, product quality, or assists in manufacturing/testing of products",
         "Verify whether the use case has any impact on patients or customers"],
        ["Audit logging approach", "Events and accesses tracked", "Audit retention period"],
        conditional_on=ConditionalOn("AI-Q15", ["yes"]),
        is_conditional_trigger=True),

    Question("AI-Q23", "tech", "samplingRationale", "Sampling Rationale", True, 0.05,
        "Why is full data audit not performed? Justify the approach.",
        ["Verify whether any AI functionality impacts patient safety, product quality, or assists in manufacturing/testing",
         "Verify whether the use case has any impact on patients or customers"],
        ["Technical or business constraints", "Sampling methodology", "Risk mitigation", "Compensating controls"],
        conditional_on=ConditionalOn("AI-Q22", ["no", "yes - a sampling"])),
]

Q_MAP: dict[str, Question] = {q.id: q for q in QUESTIONS}

PANELS = {
    "user":   {"label": "User Info",   "accent": "#7c8fff", "icon": "◎", "desc": "Ownership and contact details."},
    "system": {"label": "System Info", "accent": "#00e5a0", "icon": "⬡", "desc": "Business context, value, governance and risk."},
    "tech":   {"label": "Tech Info",   "accent": "#ff9d4d", "icon": "◈", "desc": "Architecture, data, privacy and deployment."},
}


def get_active_question_ids(raw_answers: dict) -> set:
    """
    Returns active question IDs based on conditional logic.
    raw_answers must be keyed by question ID e.g. {"AI-Q15": "Yes"}.
    Exactly mirrors getActiveQIds() from the React frontend.
    """
    active = {q.id for q in QUESTIONS}

    def txt(qid: str) -> str:
        return str(raw_answers.get(qid, "")).lower()

    def has_kw(qid: str, kws: list) -> bool:
        return any(k.lower() in txt(qid) for k in kws)

    ai15_done = "AI-Q15" in raw_answers
    ai15_yes  = has_kw("AI-Q15", ["yes"])

    if not ai15_done or not ai15_yes:
        active.discard("AI-Q20")
        active.discard("AI-Q22")
        active.discard("AI-Q23")
    elif "AI-Q22" in raw_answers and not has_kw("AI-Q22", ["no", "yes - a sampling"]):
        active.discard("AI-Q23")

    return active
