import { useState, useEffect, useRef, useCallback } from "react";
import Block from "./components/Block";
import { chat, scoreQuestion, submitEvaluation, resetSession } from "./api/index";
import {
  QUESTIONS, Q_MAP, PANELS,
  getActiveQIds, aggregateApproval, panelConf,
  scoreColor, scoreLabel, scorePct,
} from "./hooks/questions";

// ─── CSS ──────────────────────────────────────────────────────────────────────
const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
::-webkit-scrollbar{width:3px}::-webkit-scrollbar-thumb{background:#1a2540;border-radius:2px}
textarea,button{outline:none;font-family:inherit}
@keyframes fadeUp{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:none}}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0.1}}
@keyframes pulse{0%,100%{opacity:0.7}50%{opacity:1}}
@keyframes slideIn{from{opacity:0;transform:translateX(-6px)}to{opacity:1;transform:none}}
`;

const S = {
  root:        { fontFamily:"'DM Sans',sans-serif", background:"#070e1c", color:"#c0cfea", height:"100vh", display:"flex", flexDirection:"column", overflow:"hidden" },
  bgGrid:      { position:"fixed", inset:0, backgroundImage:"linear-gradient(rgba(80,100,180,0.02) 1px,transparent 1px),linear-gradient(90deg,rgba(80,100,180,0.02) 1px,transparent 1px)", backgroundSize:"40px 40px", pointerEvents:"none" },
  header:      { display:"flex", alignItems:"center", gap:20, padding:"11px 22px", borderBottom:"1px solid rgba(80,100,180,0.1)", background:"rgba(7,14,28,0.97)", flexShrink:0, zIndex:10 },
  brand:       { display:"flex", alignItems:"baseline", gap:4, flexShrink:0 },
  brandS:      { fontFamily:"'Space Mono',monospace", fontSize:22, fontWeight:700, color:"#00e5a0", animation:"pulse 3s infinite" },
  brandRest:   { fontFamily:"'Space Mono',monospace", fontSize:22, fontWeight:700, color:"#c0cfea" },
  brandSub:    { fontSize:9, color:"#2a3a58", letterSpacing:"0.14em", textTransform:"uppercase", marginLeft:8 },
  progWrap:    { flex:1, maxWidth:360, display:"flex", flexDirection:"column", gap:5 },
  progTrack:   { height:2, background:"#101b30", borderRadius:1, overflow:"hidden" },
  progFill:    { height:"100%", background:"linear-gradient(90deg,#00e5a0,#7c8fff)", borderRadius:1, transition:"width 0.6s ease" },
  badge:       { display:"flex", flexDirection:"column", alignItems:"center", border:"1px solid", borderRadius:8, padding:"6px 16px", flexShrink:0, transition:"border-color 0.4s" },
  btnRow:      { display:"flex", alignItems:"center", gap:8, flexShrink:0 },
  submitBtn:   { background:"linear-gradient(135deg,#00e5a0,#7c8fff)", border:"none", borderRadius:8, color:"#070e1c", fontFamily:"'Space Mono',monospace", fontSize:10, fontWeight:700, padding:"8px 16px", cursor:"pointer", letterSpacing:"0.08em" },
  newChatBtn:  { background:"none", border:"1px solid rgba(80,100,180,0.22)", borderRadius:8, color:"#3a4a68", fontFamily:"'Space Mono',monospace", fontSize:10, padding:"8px 14px", cursor:"pointer", letterSpacing:"0.08em" },
  body:        { display:"flex", flex:1, overflow:"hidden" },
  chatCol:     { width:"42%", minWidth:320, display:"flex", flexDirection:"column", borderRight:"1px solid rgba(80,100,180,0.08)", background:"rgba(8,13,26,0.85)" },
  statusBar:   { display:"flex", alignItems:"center", justifyContent:"space-between", padding:"7px 14px", borderBottom:"1px solid rgba(80,100,180,0.08)", background:"rgba(8,12,24,0.9)", flexShrink:0 },
  msgs:        { flex:1, overflowY:"auto", padding:"13px 15px", display:"flex", flexDirection:"column", gap:9 },
  avatar:      { width:24, height:24, borderRadius:"50%", background:"linear-gradient(135deg,#00e5a0,#7c8fff)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:10, fontWeight:700, color:"#070e1c", flexShrink:0, fontFamily:"'Space Mono',monospace" },
  aBubble:     { background:"rgba(16,24,44,0.95)", border:"1px solid rgba(80,100,180,0.12)", color:"#c0cfea", borderBottomLeftRadius:3 },
  uBubble:     { background:"rgba(0,229,160,0.07)", border:"1px solid rgba(0,229,160,0.18)", color:"#daf5ee", borderBottomRightRadius:3 },
  nudge:       { background:"rgba(245,197,66,0.06)", border:"1px solid rgba(245,197,66,0.18)", color:"#f5c542", fontSize:11, fontStyle:"italic", borderRadius:8, maxWidth:"90%" },
  multiTag:    { background:"rgba(124,143,255,0.07)", border:"1px solid rgba(124,143,255,0.18)", borderRadius:8, padding:"8px 12px", fontSize:11, color:"#7c8fff", animation:"slideIn 0.25s ease", maxWidth:"90%", lineHeight:1.7 },
  ta:          { flex:1, background:"rgba(16,24,44,0.9)", border:"1px solid rgba(80,100,180,0.15)", borderRadius:9, padding:"9px 12px", color:"#c0cfea", fontSize:13, resize:"none", lineHeight:1.5 },
  sendBtn:     { width:36, height:36, borderRadius:"50%", background:"linear-gradient(135deg,#00e5a0,#7c8fff)", border:"none", color:"#070e1c", fontSize:16, fontWeight:700, cursor:"pointer", flexShrink:0, transition:"opacity 0.2s" },
  // Reset dialog
  overlay:     { position:"fixed", inset:0, background:"rgba(7,14,28,0.88)", display:"flex", alignItems:"center", justifyContent:"center", zIndex:200, backdropFilter:"blur(4px)" },
  dlgCard:     { background:"#0d1628", border:"1px solid rgba(80,100,180,0.2)", borderRadius:14, padding:"28px 32px", maxWidth:360, width:"90%", display:"flex", flexDirection:"column", gap:16 },
  dlgTitle:    { fontFamily:"'Space Mono',monospace", fontSize:14, fontWeight:700, color:"#c0cfea" },
  dlgBody:     { fontSize:13, color:"#4a5e80", lineHeight:1.65 },
  dlgBtnRow:   { display:"flex", gap:10, justifyContent:"flex-end" },
  dlgCancel:   { background:"none", border:"1px solid rgba(80,100,180,0.2)", borderRadius:7, color:"#3a4a68", fontFamily:"'Space Mono',monospace", fontSize:10, padding:"8px 16px", cursor:"pointer" },
  dlgConfirm:  { background:"linear-gradient(135deg,#ff4d6d,#c0306a)", border:"none", borderRadius:7, color:"#fff", fontFamily:"'Space Mono',monospace", fontSize:10, fontWeight:700, padding:"8px 16px", cursor:"pointer" },
};

const INIT_MSG = {
  role:"assistant", id:0,
  content:"Hello! I'm SAGE — your AI Governance & Evaluation assistant.\n\nI'll guide you through registering your AI system. The three blocks on the right fill in automatically as we talk, and every answer is scored in real-time.\n\nYou can answer multiple questions at once — for example:\n\"My system is called SmartAI, owned by Jane Smith in IT, and we don't process personal data.\"\nI'll extract all of it automatically.\n\nLet's begin — what is the name of your AI system?",
};

export default function App() {
  const [msgs,       setMsgs]       = useState([INIT_MSG]);
  const [input,      setInput]      = useState("");
  const [busy,       setBusy]       = useState(false);
  const [status,     setStatus]     = useState("");
  const [rawAnswers, setRawAnswers] = useState({});
  const [blocks,     setBlocks]     = useState({ user:"", system:"", tech:"" });
  const [conf,       setConf]       = useState({});
  const [pendingQId, setPendingQId] = useState("AI-Q1");
  const [activeQIds, setActiveQIds] = useState(() => getActiveQIds({}));
  const [rescoring,  setRescoring]  = useState(false);
  const [submitted,  setSubmitted]  = useState(false);
  const [showReset,  setShowReset]  = useState(false);
  const endRef = useRef(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior:"smooth" }); }, [msgs]);

  const totalScore = aggregateApproval(conf, activeQIds);
  const answered   = Object.keys(rawAnswers).length;
  const progress   = activeQIds.size ? (answered / activeQIds.size) * 100 : 0;

  // ── NEW CHAT SESSION ───────────────────────────────────────────────────────
  // Resets all local state while keeping the same UI shell mounted.
  const handleNewSession = useCallback(async () => {
    setShowReset(false);
    try { await resetSession(); } catch(e) { /* non-blocking */ }
    setMsgs([INIT_MSG]);
    setInput("");
    setRawAnswers({});
    setBlocks({ user:"", system:"", tech:"" });
    setConf({});
    setPendingQId("AI-Q1");
    setActiveQIds(getActiveQIds({}));
    setSubmitted(false);
    setBusy(false);
    setStatus("");
  }, []);

  // ── SEND ──────────────────────────────────────────────────────────────────
  // Design:
  //   - Backend extracts answers for ALL questions mentioned in one message
  //   - All extracted answers saved immediately (no LLM gate)
  //   - All affected panels re-polished in one round-trip
  //   - conf_scores sent each turn so backend can compute correct aggregate
  const send = useCallback(async () => {
    if (!input.trim() || busy) return;
    const text = input.trim();
    setInput("");

    const userMsg = { role:"user", id:Date.now(), content:text };
    const history = [...msgs, userMsg];
    setMsgs(history);
    setBusy(true);
    setStatus("thinking…");

    try {
      const apiMessages = history.map(m => ({ role:m.role, content:m.content }));
      const res = await chat(apiMessages, rawAnswers, pendingQId, conf);

      // Agent reply
      const newMsgs = [
        ...history,
        { role:"assistant", id:Date.now()+1, content:res.reply },
      ];

      // Multi-extraction acknowledgement
      // When the user answered >1 question in one message, show a compact summary tag
      if (res.extraction_summary && res.extraction_summary.length > 1) {
        const lines = res.extraction_summary.map(e => `• ${e.label}: "${e.text}"`).join("\n");
        newMsgs.push({
          role:"assistant", id:Date.now()+2, isMulti:true,
          content:`📋 Captured from your message:\n${lines}`,
        });
      }

      // Merge state from backend
      const newRaw  = res.new_raw_answers;
      const newActive = getActiveQIds(newRaw);
      const newConf = { ...conf, ...res.scores };

      setRawAnswers(newRaw);
      setActiveQIds(newActive);
      setConf(newConf);

      // Apply polished blocks (may be multiple panels if multi-extraction)
      if (res.polished_blocks && Object.keys(res.polished_blocks).length) {
        setBlocks(prev => ({ ...prev, ...res.polished_blocks }));
      }

      // Nudge
      if (res.is_nudge && res.nudge_text) {
        const primaryScore = res.scores?.[res.effective_q_id] ?? 0;
        newMsgs.push({
          role:"assistant", id:Date.now()+3, isNudge:true,
          content:`📊 "${Q_MAP[res.effective_q_id]?.label}" scored ${Math.round(primaryScore*100)}% — still needs: ${res.nudge_text}`,
        });
      }
      setMsgs(newMsgs);

      // Advance pendingQId — skip any questions already bulk-answered
      const answeredSet = new Set(Object.keys(newRaw));
      if (res.effective_q_id && (res.coverage_ok || !Q_MAP[res.effective_q_id]?.mandatory)) {
        const next = QUESTIONS.find(q => newActive.has(q.id) && !answeredSet.has(q.id));
        setPendingQId(next?.id ?? null);
      } else if (res.effective_q_id) {
        setPendingQId(res.effective_q_id);
      }

    } catch (e) {
      console.error(e);
      setMsgs(p => [...p, {
        role:"assistant", id:Date.now(), isErr:true,
        content:"Sorry, I hit an error. Please try again.",
      }]);
    }

    setStatus("");
    setBusy(false);
  }, [input, busy, msgs, rawAnswers, pendingQId, conf]);

  // ── BLOCK SAVE + RE-SCORE ─────────────────────────────────────────────────
  const saveBlock = useCallback(async (panel, newContent) => {
    setBlocks(prev => ({ ...prev, [panel]: newContent }));
    if (!newContent.trim()) return;
    setRescoring(true);
    try {
      const panelQIds = QUESTIONS.filter(q =>
        q.panel === panel && activeQIds.has(q.id) && q.id in rawAnswers
      );
      const newConf = { ...conf };
      await Promise.all(panelQIds.map(async q => {
        const res = await scoreQuestion(q.id, newContent);
        newConf[q.id] = res.score;
      }));
      setConf(newConf);
    } catch (e) {
      console.error("Re-score failed:", e);
    }
    setRescoring(false);
  }, [activeQIds, rawAnswers, conf]);

  // ── SUBMIT ────────────────────────────────────────────────────────────────
  const handleSubmit = useCallback(async () => {
    if (busy || submitted) return;
    setBusy(true); setStatus("submitting…");
    try {
      await submitEvaluation(rawAnswers, conf, blocks);
      setSubmitted(true);
      setMsgs(prev => [...prev, {
        role:"assistant", id:Date.now(),
        content:"✅ Evaluation submitted! Your AI governance registration has been recorded.\n\nUse ↺ New Chat to start a fresh session.",
      }]);
    } catch(e) { console.error(e); }
    setStatus(""); setBusy(false);
  }, [busy, submitted, rawAnswers, conf, blocks]);

  const onKey  = e => { if (e.key==="Enter" && !e.shiftKey) { e.preventDefault(); send(); } };
  const c      = scoreColor(totalScore);
  const allDone = pendingQId === null && answered > 0;

  return (
    <div style={S.root}>
      <style>{CSS}</style>
      <div style={S.bgGrid}/>

      {/* ── RESET CONFIRMATION DIALOG ── */}
      {showReset && (
        <div style={S.overlay}>
          <div style={S.dlgCard}>
            <div style={S.dlgTitle}>Start a new session?</div>
            <div style={S.dlgBody}>
              This will clear all answers, scores, and chat history. The current evaluation will be lost unless you submit it first.
            </div>
            <div style={S.dlgBtnRow}>
              <button onClick={() => setShowReset(false)} style={S.dlgCancel}>Cancel</button>
              <button onClick={handleNewSession} style={S.dlgConfirm}>New Session</button>
            </div>
          </div>
        </div>
      )}

      {/* ── HEADER ── */}
      <header style={S.header}>
        <div style={S.brand}>
          <span style={S.brandS}>S</span>
          <span style={S.brandRest}>AGE</span>
          <span style={S.brandSub}>AI Governance &amp; Evaluation</span>
        </div>
        <div style={S.progWrap}>
          <div style={{ display:"flex", justifyContent:"space-between" }}>
            <span style={{ fontSize:9, color:"#2a3a58", letterSpacing:"0.1em", textTransform:"uppercase" }}>
              Evaluation Progress
            </span>
            <span style={{ fontFamily:"'Space Mono',monospace", fontSize:9, color:"#7c8fff" }}>
              {answered} / {activeQIds.size} questions
            </span>
          </div>
          <div style={S.progTrack}>
            <div style={{ ...S.progFill, width:`${progress}%` }}/>
          </div>
        </div>
        <div style={{ ...S.badge, borderColor:`${c}44` }}>
          <span style={{ fontFamily:"'Space Mono',monospace", fontSize:24, fontWeight:700, lineHeight:1, color:c, transition:"color 0.4s" }}>
            {Math.round(totalScore*100)}
          </span>
          <span style={{ fontSize:8, letterSpacing:"0.18em", textTransform:"uppercase", color:c, transition:"color 0.4s" }}>
            {scoreLabel(totalScore)}
          </span>
          <span style={{ fontSize:8, color:"#2a3a58" }}>approval</span>
        </div>
        <div style={S.btnRow}>
          {allDone && !submitted && (
            <button onClick={handleSubmit} style={S.submitBtn} disabled={busy}>Submit ↗</button>
          )}
          <button
            onClick={() => setShowReset(true)}
            style={S.newChatBtn}
            disabled={busy}
            title="Start a fresh session"
          >↺ New Chat</button>
        </div>
      </header>

      {/* ── BODY ── */}
      <div style={S.body}>
        {/* ── CHAT COLUMN ── */}
        <div style={S.chatCol}>
          <div style={S.statusBar}>
            <div style={{ display:"flex", gap:14 }}>
              {["user","system","tech"].map(p => {
                const pQs = QUESTIONS.filter(q => activeQIds.has(q.id) && q.panel===p);
                const done = pQs.filter(q => q.id in rawAnswers).length;
                const acc  = PANELS[p].accent;
                const all  = done===pQs.length && pQs.length>0;
                return (
                  <div key={p} style={{ display:"flex", alignItems:"center", gap:5 }}>
                    <span style={{ width:6, height:6, borderRadius:"50%", display:"inline-block",
                      background:all?acc:done>0?`${acc}66`:"#1e2e44", transition:"background 0.4s" }}/>
                    <span style={{ fontSize:9, letterSpacing:"0.1em", textTransform:"uppercase",
                      color:all?acc:done>0?`${acc}99`:"#2a3a58", transition:"color 0.4s" }}>
                      {PANELS[p].label}
                    </span>
                  </div>
                );
              })}
            </div>
            {status && (
              <span style={{ fontSize:9, color:"#f5c542", animation:"blink 1s infinite", fontStyle:"italic" }}>
                {status}
              </span>
            )}
          </div>

          <div style={S.msgs}>
            {msgs.map(m => (
              <div key={m.id} style={{
                display:"flex", alignItems:"flex-end", gap:7,
                justifyContent:m.role==="user"?"flex-end":"flex-start",
                animation:"fadeUp 0.2s ease",
              }}>
                {m.role==="assistant" && !m.isNudge && !m.isMulti && (
                  <div style={S.avatar}>S</div>
                )}
                <div style={{
                  maxWidth:"82%", padding:"9px 13px", borderRadius:11,
                  fontSize:13, lineHeight:1.6, whiteSpace:"pre-wrap",
                  ...(m.role==="user"  ? S.uBubble :
                      m.isNudge       ? S.nudge   :
                      m.isMulti       ? S.multiTag:
                                        S.aBubble ),
                  ...(m.isErr ? { background:"rgba(255,77,109,0.07)", border:"1px solid rgba(255,77,109,0.2)", color:"#ffb3be" } : {}),
                }}>
                  {m.content}
                </div>
              </div>
            ))}
            {busy && (
              <div style={{ display:"flex", gap:7, alignItems:"flex-end" }}>
                <div style={S.avatar}>S</div>
                <div style={{ ...S.aBubble, padding:"9px 13px", borderRadius:11, display:"flex", gap:4, alignItems:"center" }}>
                  {[0,0.2,0.4].map(d => (
                    <span key={d} style={{ display:"inline-block", width:5, height:5, background:"#7c8fff", borderRadius:"50%", animation:`blink 1.2s ${d}s infinite` }}/>
                  ))}
                </div>
              </div>
            )}
            <div ref={endRef}/>
          </div>

          <div style={{ display:"flex", gap:7, padding:"10px 13px", borderTop:"1px solid rgba(80,100,180,0.08)", background:"rgba(7,11,22,0.96)", flexShrink:0 }}>
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={onKey}
              placeholder="Answer one or multiple questions at once…"
              style={S.ta}
              rows={2}
              disabled={busy}
            />
            <button
              onClick={send}
              disabled={busy || !input.trim()}
              style={{ ...S.sendBtn, opacity:busy||!input.trim()?0.3:1 }}
            >↑</button>
          </div>
        </div>

        {/* ── THREE BLOCKS ── */}
        <div style={{ flex:1, display:"flex", flexDirection:"column", overflow:"hidden" }}>
          {["user","system","tech"].map(panel => (
            <Block
              key={panel}
              panel={panel}
              content={blocks[panel]}
              conf={panelConf(panel, conf, activeQIds)}
              rescoring={rescoring}
              polishing={busy && Q_MAP[pendingQId]?.panel===panel}
              onSave={c => saveBlock(panel, c)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
