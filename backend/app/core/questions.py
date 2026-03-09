"""
SAGE Questions Registry — single source of truth for all AI governance questions.
Maps to the AI Review submission form. Suggestions[] drive scoring + agent follow-ups.
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
    panel: str               # "system" | "user" | "tech"
    field: str               # camelCase field name
    label: str
    mandatory: bool
    weight: float
    q: str                   # Question text shown to user
    suggestions: List[str]   # Drives scoring
    hints: List[str]
    is_conditional_trigger: bool = False
    conditional_on: Optional[ConditionalOn] = None


QUESTIONS: List[Question] = [
    # ── SYSTEM INFORMATION PANEL ──────────────────────────────────────────────
    Question("AI-Q2", "system", "systemTitle", "System Title", True, 0.05,
        "What is the title of the System?",
        ["Provide a clear and descriptive title for the AI system"],
        ["Clear system name", "Reflects purpose"]),

    Question("AI-Q3", "system", "solutionOverview", "Solution Overview", True, 0.08,
        "Provide an overview of the solution.",
        ["Provide a concise description of what the system does, its purpose, and how it works",
         "Describe the key capabilities and functions of the solution"],
        ["What the system does", "How it works", "Key capabilities"]),

    Question("AI-Q4", "system", "valueProposition", "Value Proposition", True, 0.07,
        "What is the value proposition for this solution?",
        ["Describe the business value, benefits, and impact this solution provides",
         "Explain the problem it solves and the value it delivers to the organization"],
        ["Business value", "Benefits", "Problem solved", "Impact"]),

    Question("AI-Q5", "system", "sponsorOrg", "Sponsor Organization", True, 0.04,
        "Which organization will sponsor the System?",
        ["Identify the sponsoring organization or business unit responsible for the system"],
        ["Organization name", "Business unit"]),

    Question("AI-Q6", "system", "vendorProduct", "Vendor Product", False, 0.02,
        "Are you planning to implement a vendor product as part or all of this system? (Yes / No)",
        ["Indicate whether a vendor product will be used as part of or for the entire system"],
        ["Yes or No"],
        is_conditional_trigger=True),

    Question("AI-Q7", "system", "vendorNames", "Vendor Names", False, 0.03,
        "Which vendor(s) are you planning to use?",
        ["List all vendor names that will supply products or services for this system"],
        ["Vendor names"],
        conditional_on=ConditionalOn("AI-Q6", ["yes"])),

    Question("AI-Q8", "system", "productNames", "Product Names", False, 0.03,
        "What product(s) from the vendor(s) will you use?",
        ["List the specific product names from each vendor"],
        ["Product names", "Product versions if known"],
        conditional_on=ConditionalOn("AI-Q6", ["yes"])),

    # ── USER INFORMATION PANEL ────────────────────────────────────────────────
    Question("AI-Q9", "user", "userDescription", "User Description", True, 0.08,
        "Briefly describe the users of the system, what they will be using it for, and what problem it will solve for them.",
        ["Describe who the users are, their roles, what they will use the system for, and the problem it solves for them",
         "Identify the target user groups and their needs"],
        ["Who are the users", "What they use it for", "Problem it solves"]),

    Question("AI-Q10", "user", "deploymentLocation", "Deployment Location", True, 0.04,
        "Where will you deploy your System? (Select all that apply)",
        ["Identify all deployment locations and environments for the system (e.g., cloud, on-premises, hybrid, specific regions)"],
        ["Cloud", "On-premises", "Hybrid", "Specific regions"]),

    Question("AI-Q11", "user", "audience", "System Audience", True, 0.04,
        "Who is the audience of this system? (Select all that apply)",
        ["Identify all audiences for the system (e.g., internal employees, external customers, partners, patients, HCPs)"],
        ["Internal employees", "External customers", "Partners", "Other audiences"]),

    # ── TECHNICAL INFORMATION PANEL ───────────────────────────────────────────
    Question("AI-Q12", "tech", "additionalTechInfo", "Additional Technical Info", False, 0.02,
        "Do you have any additional technical information to provide? (Yes / No)",
        ["Indicate whether additional technical details are available at this time"],
        ["Yes or No"],
        is_conditional_trigger=True),

    Question("AI-Q13", "tech", "systemMaturity", "System Maturity", True, 0.04,
        "What is the maturity of the System?",
        ["Describe the maturity level of the system (e.g., Concept/Ideation, Development, Pilot, Production, Retired)"],
        ["Concept/Ideation", "Development", "Pilot", "Production"]),

    Question("AI-Q14", "tech", "dataProcessed", "Data Processed", True, 0.06,
        "Does the System process any of the following data? (Select all that apply: Personal Information, Confidential Information, Patient Data, Employee Data, etc.)",
        ["Identify all types of data the system processes including Personal Information (PI), Confidential Information (CI), patient data, employee data, or other sensitive data",
         "If the AI use case processes Personal Information, a Privacy Review is required per the global Respecting Privacy procedure"],
        ["Personal Information", "Confidential Information", "Patient data", "Employee data", "Public data"]),

    Question("AI-Q15", "tech", "dataClassification", "Data Classification", True, 0.05,
        "What is the highest data classification for processed data? Note: If data classification increases during implementation, a new review cycle will be required.",
        ["Identify the highest data classification level (e.g., Public, Internal, Confidential, Restricted)"],
        ["Public", "Internal", "Confidential", "Restricted"]),

    Question("AI-Q16", "tech", "dataForTraining", "Data Used for Training", False, 0.04,
        "Is any of this data used for training the model? (Yes / No / Not Sure)",
        ["Indicate whether any of the processed data is used for training the AI/ML model"],
        ["Yes", "No", "Not Sure"]),

    Question("AI-Q17", "tech", "dataNeeded", "Data Needed", True, 0.05,
        "Describe the Data Needed.",
        ["Describe all data sources, types, and volumes needed by the system",
         "Explain how data flows into and out of the system"],
        ["Data sources", "Data types", "Data volumes", "Data flow"]),

    Question("AI-Q18", "tech", "aiFunctionality", "AI Functionality", True, 0.06,
        "Does the AI Functionality of the system do any of the following? (Select all that apply: generate content, make predictions, classify data, recommend actions, automate decisions, etc.)",
        ["Describe all AI functionalities of the system such as content generation, predictions, classification, recommendations, decision automation, or other AI capabilities"],
        ["Content generation", "Predictions", "Classification", "Recommendations", "Decision automation"]),

    Question("AI-Q19", "tech", "humanReview", "Human Review of Output", True, 0.05,
        "Is the AI System output reviewed by a human before it is used? (Yes – 100% of the output / Yes – a sampling / No)",
        ["Describe the extent of human review of AI system outputs before they are used",
         "If sampling, describe the sampling methodology"],
        ["Yes – 100%", "Yes – a sampling", "No"],
        is_conditional_trigger=True),

    Question("AI-Q20", "tech", "aiPlatforms", "AI Platforms & Technologies", True, 0.05,
        "Which AI platforms/technologies will be used? Include AI platforms/technology, Models, and Open Source Models.",
        ["List all AI platforms, technologies, models (proprietary and open source) that will be used",
         "Specify model names and versions where known"],
        ["AI platforms", "Proprietary models", "Open source models", "Technology stack"]),

    Question("AI-Q21", "tech", "continuousLearning", "Continuous Learning", False, 0.03,
        "Does the AI/ML use continuous learning? (Yes / No)",
        ["Indicate whether the AI/ML system uses continuous learning (model updates automatically from new data)"],
        ["Yes or No", "How the model is updated"]),

    Question("AI-Q22", "tech", "privacyRequestId", "Privacy Request Identifier", False, 0.02,
        "What is the Privacy Request Identifier?",
        ["Provide the Privacy Request Identifier if a privacy review has been initiated"],
        ["Privacy Request ID"]),

    Question("AI-Q23", "tech", "saeReviewNumber", "SAE Review Number", False, 0.02,
        "What is the SAE review number?",
        ["Provide the SAE (Security Architecture Evaluation) review number if available"],
        ["SAE review number"]),

    Question("AI-Q24", "tech", "wwtpReview", "WwTP Review", False, 0.02,
        "What is the WwTP review status or number?",
        ["Provide the WwTP (Ways We Trust People) review number or status if available"],
        ["WwTP review number or status"]),
]

Q_MAP: dict[str, Question] = {q.id: q for q in QUESTIONS}

PANELS = {
    "system": {"label": "System Info",    "accent": "#00e5a0", "icon": "⬡", "desc": "System details, value proposition, and vendor information."},
    "user":   {"label": "User Info",      "accent": "#7c8fff", "icon": "◎", "desc": "Users, deployment, and audience."},
    "tech":   {"label": "Technical Info",  "accent": "#ff9d4d", "icon": "◈", "desc": "Technical details, data, AI functionality, and compliance."},
}


def get_active_question_ids(raw_answers: dict) -> set:
    """
    Returns active question IDs based on conditional logic.
    raw_answers must be keyed by question ID e.g. {"AI-Q6": "Yes"}.
    Exactly mirrors getActiveQIds() from the React frontend.
    """
    active = {q.id for q in QUESTIONS}

    def txt(qid: str) -> str:
        return str(raw_answers.get(qid, "")).lower()

    def has_kw(qid: str, kws: list) -> bool:
        return any(k.lower() in txt(qid) for k in kws)

    # AI-Q6 (Vendor Product) → AI-Q7 (Vendor Names), AI-Q8 (Product Names)
    ai6_done = "AI-Q6" in raw_answers
    ai6_yes  = has_kw("AI-Q6", ["yes"])
    if not ai6_done or not ai6_yes:
        active.discard("AI-Q7")
        active.discard("AI-Q8")

    return active
