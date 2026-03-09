/**
 * Client-side question registry and scoring.
 * Mirrors backend app/core/questions.py and app/services/scoring.py exactly.
 * Used for instant UI updates without waiting for API round-trips.
 */

export const QUESTIONS = [
  { id:"AI-Q1",  panel:"user",   field:"systemName",          label:"AI System Name",          mandatory:false, weight:0.03,
    q:"What is the name of your AI system?",
    suggestions:["Provide a concise name that clearly reflects the system's domain and purpose"],
    hints:["Clear descriptive name","Reflects domain/purpose"] },
  { id:"AI-Q2",  panel:"user",   field:"ownerName",           label:"Business Owner",          mandatory:false, weight:0.03,
    q:"Who is the business owner responsible for this AI system?",
    suggestions:["Identify the business owner by full name, their business unit, department, and the team involved"],
    hints:["Full name","Business unit","Department","Team"] },
  { id:"AI-Q3",  panel:"user",   field:"contactEmail",        label:"Contact Email",           mandatory:false, weight:0.02,
    q:"What is the primary contact email for this submission?",
    suggestions:["Provide a valid business email address as the point of contact for follow-ups"],
    hints:["Valid business email"] },
  { id:"AI-Q4",  panel:"system", field:"problemStatement",    label:"Problem Statement",       mandatory:false, weight:0.06,
    q:"What problem or business opportunity does your AI system address?",
    suggestions:["Provide a concise 2-3 sentence description of the AI solution covering what it does, its intended business purpose, target users, and whether it is new or enhances existing capability","Identify the business process or workflow that the AI solution supports"],
    hints:["Articulate the pain point","Quantify business impact","Who is affected","Current vs desired state"] },
  { id:"AI-Q5",  panel:"system", field:"aiSolution",          label:"AI Solution",             mandatory:false, weight:0.06,
    q:"Describe your AI solution — how it works and what it does.",
    suggestions:["Provide a concise 2-3 sentence description of the AI solution covering what it does, its intended business purpose, target users, and whether it is new or enhances existing capability","Explain how the AI solution integrates with existing systems"],
    hints:["Plain-language description","Core AI/ML capabilities","Inputs and outputs"] },
  { id:"AI-Q6",  panel:"system", field:"valueProposition",    label:"Value Proposition",       mandatory:true,  weight:0.12,
    q:"What is the expected business value and impact of this AI system?",
    suggestions:["Provide a concise 2-3 sentence description of the AI solution covering what it does, its intended business purpose, target users, and whether it is new or enhances existing capability","Specify the deployment model (SaaS vendor-hosted, self-hosted, or hybrid) and indicate if alternative hosting options are available"],
    hints:["Quantify ROI or cost savings","Impact on users","Short and long-term benefits","Specific KPIs"] },
  { id:"AI-Q7",  panel:"system", field:"targetUsers",         label:"Target Users",            mandatory:true,  weight:0.08,
    q:"Who are the primary users or beneficiaries of this AI system?",
    suggestions:["Provide a concise 2-3 sentence description of the AI solution covering what it does, its intended business purpose, target users, and whether it is new or enhances existing capability","Identify the key stakeholders for the AI solution"],
    hints:["Internal vs external users","User roles","Estimated number affected","Key stakeholders"] },
  { id:"AI-Q13", panel:"system", field:"explainability",      label:"Explainability",          mandatory:false, weight:0.04,
    q:"How explainable is your AI system's decision-making?",
    suggestions:["Describe how decisions made by the AI are explained to end users","Identify any explainability tools used (e.g. SHAP, LIME)"],
    hints:["How decisions are explained","Explainability tools","User-facing explanations"] },
  { id:"AI-Q14", panel:"system", field:"humanOversight",      label:"Human Oversight",         mandatory:false, weight:0.04,
    q:"What human oversight and control mechanisms are in place?",
    suggestions:["Describe human-in-the-loop processes, override capabilities, escalation paths, and monitoring"],
    hints:["Human-in-the-loop","Override capabilities","Escalation paths"] },
  { id:"AI-Q15", panel:"system", field:"usesPersonalData",    label:"Uses Personal Data",      mandatory:false, weight:0.02,
    q:"Does this AI system use, process, or generate personal data? (Yes / No)",
    suggestions:["Confirm whether the use case processes any Personal Information (PI), Confidential Information (CI), or only uses public/non-sensitive data (green/yellow classification)"],
    hints:["Yes or No","Personal data includes names, emails, IDs, location, behaviour"],
    isConditionalTrigger:true },
  { id:"AI-Q16", panel:"system", field:"riskAssessment",      label:"Risk Assessment",         mandatory:false, weight:0.05,
    q:"What are the key risks associated with this AI system?",
    suggestions:["Identify model failure modes, bias risks, adversarial attack vectors, and regulatory/reputational risks"],
    hints:["Model failure modes","Bias risks","Regulatory risks"] },
  { id:"AI-Q17", panel:"system", field:"riskMitigation",      label:"Risk Mitigation",         mandatory:true,  weight:0.10,
    q:"What specific controls and mitigations manage AI risks?",
    suggestions:["Describe bias detection and mitigation measures","Explain model drift monitoring and retraining approach","Detail fallback mechanisms and human review triggers"],
    hints:["Bias detection","Model drift monitoring","Fallback mechanisms","Human review triggers"] },
  { id:"AI-Q18", panel:"system", field:"testingValidation",   label:"Testing & Validation",    mandatory:false, weight:0.04,
    q:"How has this AI system been tested and validated?",
    suggestions:["Describe evaluation datasets, fairness and bias testing, performance metrics, and user acceptance testing"],
    hints:["Evaluation datasets","Fairness testing","Performance metrics","UAT"] },
  { id:"AI-Q20", panel:"system", field:"personalDataDetails", label:"Personal Data Details",   mandatory:true,  weight:0.06,
    q:"Describe what personal data is processed and the legal basis.",
    suggestions:["Confirm the data classification level and whether the use case processes any Personal Information (PI), Confidential Information (CI), or only uses public/non-sensitive data (green/yellow classification)"],
    hints:["Categories of personal data","Legal basis (GDPR)","Data minimization","Retention and deletion"],
    conditionalOn:{qid:"AI-Q15",kws:["yes"]} },
  { id:"AI-Q8",  panel:"tech",   field:"technicalApproach",   label:"Technical Approach",      mandatory:false, weight:0.05,
    q:"What AI/ML techniques, models, or frameworks does your system use?",
    suggestions:["Identify the data sources used by the AI solution","Provide a concise description of the AI/ML models, algorithms, and technology stack deployed"],
    hints:["Models or algorithms","Training data","Technology stack","Deployment"] },
  { id:"AI-Q9",  panel:"tech",   field:"dataDescription",     label:"Data Description",        mandatory:false, weight:0.05,
    q:"What data does this AI system use? Describe sources, types, and volumes.",
    suggestions:["Identify the data sources used by the AI solution","Describe data types (structured/unstructured), volume, and update frequency"],
    hints:["All data sources","Data types","Volume and update frequency","Data quality"] },
  { id:"AI-Q10", panel:"tech",   field:"integrations",        label:"Integrations",            mandatory:false, weight:0.03,
    q:"What systems or APIs does this AI system integrate with?",
    suggestions:["Explain how the AI solution integrates with existing systems","Identify upstream and downstream system dependencies and integration methods"],
    hints:["Upstream and downstream dependencies","Integration method","Cloud platforms"] },
  { id:"AI-Q11", panel:"tech",   field:"scalability",         label:"Scalability",             mandatory:false, weight:0.03,
    q:"How does your system handle scale and performance requirements?",
    suggestions:["Describe the expected load, scaling approach, latency, throughput, and failover strategy"],
    hints:["Expected load","Scaling approach","Latency and throughput","Failover"] },
  { id:"AI-Q12", panel:"tech",   field:"dataPrivacy",         label:"Data Privacy & Security", mandatory:true,  weight:0.10,
    q:"How does your AI system handle data privacy, security, and compliance?",
    suggestions:["Provide a concise 2-3 sentence description of the AI solution covering what it does, its intended business purpose, target users, and whether it is new or enhances existing capability","Identify the regulatory requirements applicable to the AI solution"],
    hints:["PII handling and anonymization","Encryption","Regulatory compliance (GDPR, HIPAA)","Access controls","Audit logging"] },
  { id:"AI-Q19", panel:"tech",   field:"deploymentPlan",      label:"Deployment Plan",         mandatory:false, weight:0.03,
    q:"What is your deployment plan and rollout strategy?",
    suggestions:["Describe the phased rollout approach, pilot testing plan, rollback strategy, and expected go-live timeline"],
    hints:["Phased rollout","Pilot testing","Rollback plan","Go-live timeline"] },
  { id:"AI-Q22", panel:"tech",   field:"dataAuditApproach",   label:"Data Audit Approach",     mandatory:true,  weight:0.04,
    q:"How do you audit data usage? All data or sampling? (No / Yes - all data / Yes - a sampling)",
    suggestions:["Verify whether any AI functionality impacts patient safety, product quality, or assists in manufacturing/testing of products","Verify whether the use case has any impact on patients or customers"],
    hints:["Audit logging approach","Events and accesses tracked","Audit retention period"],
    conditionalOn:{qid:"AI-Q15",kws:["yes"]}, isConditionalTrigger:true },
  { id:"AI-Q23", panel:"tech",   field:"samplingRationale",   label:"Sampling Rationale",      mandatory:true,  weight:0.05,
    q:"Why is full data audit not performed? Justify the approach.",
    suggestions:["Verify whether any AI functionality impacts patient safety, product quality, or assists in manufacturing/testing","Verify whether the use case has any impact on patients or customers"],
    hints:["Technical or business constraints","Sampling methodology","Risk mitigation","Compensating controls"],
    conditionalOn:{qid:"AI-Q22",kws:["no","yes - a sampling"]} },
];

export const Q_MAP = Object.fromEntries(QUESTIONS.map(q => [q.id, q]));

export const PANELS = {
  user:   { label:"User Info",   accent:"#7c8fff", icon:"◎", desc:"Ownership and contact details." },
  system: { label:"System Info", accent:"#00e5a0", icon:"⬡", desc:"Business context, value, governance and risk." },
  tech:   { label:"Tech Info",   accent:"#ff9d4d", icon:"◈", desc:"Architecture, data, privacy and deployment." },
};

// Mirrors get_active_question_ids() from backend exactly
export function getActiveQIds(rawAnswers) {
  const active = new Set(QUESTIONS.map(q => q.id));
  const txt = qid => String(rawAnswers[qid] ?? "").toLowerCase();
  const has = (qid, kws) => kws.some(k => txt(qid).includes(k.toLowerCase()));

  const ai15done = "AI-Q15" in rawAnswers;
  const ai15yes  = has("AI-Q15", ["yes"]);

  if (!ai15done || !ai15yes) {
    active.delete("AI-Q20"); active.delete("AI-Q22"); active.delete("AI-Q23");
  } else if ("AI-Q22" in rawAnswers && !has("AI-Q22", ["no","yes - a sampling"])) {
    active.delete("AI-Q23");
  }
  return active;
}

// Mirrors aggregate_approval() from backend exactly
const MAND_THRESHOLD = 0.6, STATIC_PENALTY = 0.15, DEFAULT_MAND_C = 0.3;

export function aggregateApproval(confScores, activeQIds) {
  const mandatory = new Set(QUESTIONS.filter(q => q.mandatory && activeQIds.has(q.id)).map(q => q.id));
  const normC = {}; const inc = []; let totW = 0;
  for (const q of QUESTIONS) {
    if (!activeQIds.has(q.id)) continue;
    const raw = confScores[q.id];
    const c = raw == null ? (mandatory.has(q.id) ? DEFAULT_MAND_C : null) : Math.min(1, Math.max(0, raw));
    if (c == null) continue;
    normC[q.id] = c;
    if (q.weight > 0) { inc.push(q.id); totW += q.weight; }
  }
  if (!inc.length || !totW) return 0;
  const base = inc.reduce((s, id) => s + (Q_MAP[id].weight / totW) * normC[id], 0);
  let pen = 1.0;
  for (const id of mandatory)
    if ((normC[id] ?? DEFAULT_MAND_C) < MAND_THRESHOLD) pen *= (1 - STATIC_PENALTY);
  return Math.min(1, base * pen);
}

export function panelConf(panel, confScores, activeQIds) {
  const qs = QUESTIONS.filter(q => q.panel === panel && activeQIds.has(q.id) && confScores[q.id] != null);
  if (!qs.length) return null;
  const totW = qs.reduce((s, q) => s + q.weight, 0);
  return totW ? qs.reduce((s, q) => s + (q.weight / totW) * confScores[q.id], 0) : null;
}

export const scoreColor = s => s==null?"#1e2e44":s>=0.8?"#00e5a0":s>=0.6?"#7c8fff":s>=0.4?"#f5c542":"#ff4d6d";
export const scoreLabel = s => s==null?"—":s>=0.8?"Strong":s>=0.6?"Good":s>=0.4?"Fair":"Weak";
export const scorePct   = s => s==null?"—":`${Math.round(s*100)}%`;
