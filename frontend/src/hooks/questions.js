/**
 * Client-side question registry and scoring.
 * Mirrors backend app/core/questions.py and app/services/scoring.py exactly.
 * Used for instant UI updates without waiting for API round-trips.
 */

export const QUESTIONS = [
  // ── SYSTEM INFORMATION PANEL ──────────────────────────────────────────────
  { id:"AI-Q2",  panel:"system", field:"systemTitle",         label:"System Title",            mandatory:true,  weight:0.05,
    q:"What is the title of the System?",
    suggestions:["Provide a clear and descriptive title for the AI system"],
    hints:["Clear system name","Reflects purpose"] },
  { id:"AI-Q3",  panel:"system", field:"solutionOverview",    label:"Solution Overview",       mandatory:true,  weight:0.08,
    q:"Provide an overview of the solution.",
    suggestions:["Provide a concise description of what the system does, its purpose, and how it works","Describe the key capabilities and functions of the solution"],
    hints:["What the system does","How it works","Key capabilities"] },
  { id:"AI-Q4",  panel:"system", field:"valueProposition",    label:"Value Proposition",       mandatory:true,  weight:0.07,
    q:"What is the value proposition for this solution?",
    suggestions:["Describe the business value, benefits, and impact this solution provides","Explain the problem it solves and the value it delivers to the organization"],
    hints:["Business value","Benefits","Problem solved","Impact"] },
  { id:"AI-Q5",  panel:"system", field:"sponsorOrg",          label:"Sponsor Organization",    mandatory:true,  weight:0.04,
    q:"Which organization will sponsor the System?",
    suggestions:["Identify the sponsoring organization or business unit responsible for the system"],
    hints:["Organization name","Business unit"] },
  { id:"AI-Q6",  panel:"system", field:"vendorProduct",       label:"Vendor Product",          mandatory:false, weight:0.02,
    q:"Are you planning to implement a vendor product as part or all of this system? (Yes / No)",
    suggestions:["Indicate whether a vendor product will be used as part of or for the entire system"],
    hints:["Yes or No"],
    isConditionalTrigger:true },
  { id:"AI-Q7",  panel:"system", field:"vendorNames",         label:"Vendor Names",            mandatory:false, weight:0.03,
    q:"Which vendor(s) are you planning to use?",
    suggestions:["List all vendor names that will supply products or services for this system"],
    hints:["Vendor names"],
    conditionalOn:{qid:"AI-Q6",kws:["yes"]} },
  { id:"AI-Q8",  panel:"system", field:"productNames",        label:"Product Names",           mandatory:false, weight:0.03,
    q:"What product(s) from the vendor(s) will you use?",
    suggestions:["List the specific product names from each vendor"],
    hints:["Product names","Product versions if known"],
    conditionalOn:{qid:"AI-Q6",kws:["yes"]} },

  // ── USER INFORMATION PANEL ────────────────────────────────────────────────
  { id:"AI-Q9",  panel:"user",   field:"userDescription",     label:"User Description",        mandatory:true,  weight:0.08,
    q:"Briefly describe the users of the system, what they will be using it for, and what problem it will solve for them.",
    suggestions:["Describe who the users are, their roles, what they will use the system for, and the problem it solves for them","Identify the target user groups and their needs"],
    hints:["Who are the users","What they use it for","Problem it solves"] },
  { id:"AI-Q10", panel:"user",   field:"deploymentLocation",  label:"Deployment Location",     mandatory:true,  weight:0.04,
    q:"Where will you deploy your System? (Select all that apply)",
    suggestions:["Identify all deployment locations and environments for the system (e.g., cloud, on-premises, hybrid, specific regions)"],
    hints:["Cloud","On-premises","Hybrid","Specific regions"] },
  { id:"AI-Q11", panel:"user",   field:"audience",            label:"System Audience",         mandatory:true,  weight:0.04,
    q:"Who is the audience of this system? (Select all that apply)",
    suggestions:["Identify all audiences for the system (e.g., internal employees, external customers, partners, patients, HCPs)"],
    hints:["Internal employees","External customers","Partners","Other audiences"] },

  // ── TECHNICAL INFORMATION PANEL ───────────────────────────────────────────
  { id:"AI-Q12", panel:"tech",   field:"additionalTechInfo",  label:"Additional Technical Info",mandatory:false, weight:0.02,
    q:"Do you have any additional technical information to provide? (Yes / No)",
    suggestions:["Indicate whether additional technical details are available at this time"],
    hints:["Yes or No"],
    isConditionalTrigger:true },
  { id:"AI-Q13", panel:"tech",   field:"systemMaturity",      label:"System Maturity",         mandatory:true,  weight:0.04,
    q:"What is the maturity of the System?",
    suggestions:["Describe the maturity level of the system (e.g., Concept/Ideation, Development, Pilot, Production, Retired)"],
    hints:["Concept/Ideation","Development","Pilot","Production"] },
  { id:"AI-Q14", panel:"tech",   field:"dataProcessed",       label:"Data Processed",          mandatory:true,  weight:0.06,
    q:"Does the System process any of the following data? (Select all that apply: Personal Information, Confidential Information, Patient Data, Employee Data, etc.)",
    suggestions:["Identify all types of data the system processes including Personal Information (PI), Confidential Information (CI), patient data, employee data, or other sensitive data","If the AI use case processes Personal Information, a Privacy Review is required per the global Respecting Privacy procedure"],
    hints:["Personal Information","Confidential Information","Patient data","Employee data","Public data"] },
  { id:"AI-Q15", panel:"tech",   field:"dataClassification",  label:"Data Classification",     mandatory:true,  weight:0.05,
    q:"What is the highest data classification for processed data? Note: If data classification increases during implementation, a new review cycle will be required.",
    suggestions:["Identify the highest data classification level (e.g., Public, Internal, Confidential, Restricted)"],
    hints:["Public","Internal","Confidential","Restricted"] },
  { id:"AI-Q16", panel:"tech",   field:"dataForTraining",     label:"Data Used for Training",  mandatory:false, weight:0.04,
    q:"Is any of this data used for training the model? (Yes / No / Not Sure)",
    suggestions:["Indicate whether any of the processed data is used for training the AI/ML model"],
    hints:["Yes","No","Not Sure"] },
  { id:"AI-Q17", panel:"tech",   field:"dataNeeded",          label:"Data Needed",             mandatory:true,  weight:0.05,
    q:"Describe the Data Needed.",
    suggestions:["Describe all data sources, types, and volumes needed by the system","Explain how data flows into and out of the system"],
    hints:["Data sources","Data types","Data volumes","Data flow"] },
  { id:"AI-Q18", panel:"tech",   field:"aiFunctionality",     label:"AI Functionality",        mandatory:true,  weight:0.06,
    q:"Does the AI Functionality of the system do any of the following? (Select all that apply: generate content, make predictions, classify data, recommend actions, automate decisions, etc.)",
    suggestions:["Describe all AI functionalities of the system such as content generation, predictions, classification, recommendations, decision automation, or other AI capabilities"],
    hints:["Content generation","Predictions","Classification","Recommendations","Decision automation"] },
  { id:"AI-Q19", panel:"tech",   field:"humanReview",         label:"Human Review of Output",  mandatory:true,  weight:0.05,
    q:"Is the AI System output reviewed by a human before it is used? (Yes – 100% of the output / Yes – a sampling / No)",
    suggestions:["Describe the extent of human review of AI system outputs before they are used","If sampling, describe the sampling methodology"],
    hints:["Yes – 100%","Yes – a sampling","No"],
    isConditionalTrigger:true },
  { id:"AI-Q20", panel:"tech",   field:"aiPlatforms",         label:"AI Platforms & Technologies",mandatory:true, weight:0.05,
    q:"Which AI platforms/technologies will be used? Include AI platforms/technology, Models, and Open Source Models.",
    suggestions:["List all AI platforms, technologies, models (proprietary and open source) that will be used","Specify model names and versions where known"],
    hints:["AI platforms","Proprietary models","Open source models","Technology stack"] },
  { id:"AI-Q21", panel:"tech",   field:"continuousLearning",  label:"Continuous Learning",     mandatory:false, weight:0.03,
    q:"Does the AI/ML use continuous learning? (Yes / No)",
    suggestions:["Indicate whether the AI/ML system uses continuous learning (model updates automatically from new data)"],
    hints:["Yes or No","How the model is updated"] },
  { id:"AI-Q22", panel:"tech",   field:"privacyRequestId",    label:"Privacy Request Identifier",mandatory:false, weight:0.02,
    q:"What is the Privacy Request Identifier?",
    suggestions:["Provide the Privacy Request Identifier if a privacy review has been initiated"],
    hints:["Privacy Request ID"] },
  { id:"AI-Q23", panel:"tech",   field:"saeReviewNumber",     label:"SAE Review Number",       mandatory:false, weight:0.02,
    q:"What is the SAE review number?",
    suggestions:["Provide the SAE (Security Architecture Evaluation) review number if available"],
    hints:["SAE review number"] },
  { id:"AI-Q24", panel:"tech",   field:"wwtpReview",          label:"WwTP Review",             mandatory:false, weight:0.02,
    q:"What is the WwTP review status or number?",
    suggestions:["Provide the WwTP (Ways We Trust People) review number or status if available"],
    hints:["WwTP review number or status"] },
];

export const Q_MAP = Object.fromEntries(QUESTIONS.map(q => [q.id, q]));

export const PANELS = {
  system: { label:"System Info",    accent:"#00e5a0", icon:"⬡", desc:"System details, value proposition, and vendor information." },
  user:   { label:"User Info",      accent:"#7c8fff", icon:"◎", desc:"Users, deployment, and audience." },
  tech:   { label:"Technical Info",  accent:"#ff9d4d", icon:"◈", desc:"Technical details, data, AI functionality, and compliance." },
};

// Mirrors get_active_question_ids() from backend exactly
export function getActiveQIds(rawAnswers) {
  const active = new Set(QUESTIONS.map(q => q.id));
  const txt = qid => String(rawAnswers[qid] ?? "").toLowerCase();
  const has = (qid, kws) => kws.some(k => txt(qid).includes(k.toLowerCase()));

  // AI-Q6 (Vendor Product) → AI-Q7 (Vendor Names), AI-Q8 (Product Names)
  const ai6done = "AI-Q6" in rawAnswers;
  const ai6yes  = has("AI-Q6", ["yes"]);
  if (!ai6done || !ai6yes) {
    active.delete("AI-Q7"); active.delete("AI-Q8");
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
