import { useState, useEffect, useRef } from "react";
import { PANELS, scoreColor, scoreLabel, scorePct } from "../hooks/questions";

const BL = {
  card:      { display:"flex", flexDirection:"column", borderTop:"2px solid", flex:1, background:"rgba(8,13,26,0.7)", borderBottom:"1px solid rgba(80,100,180,0.07)" },
  header:    { display:"flex", alignItems:"flex-start", gap:10, padding:"11px 16px 9px", flexShrink:0 },
  icon:      { fontSize:16, marginTop:1, flexShrink:0 },
  mid:       { flex:1, display:"flex", flexDirection:"column", gap:2 },
  title:     { fontFamily:"'Space Mono',monospace", fontSize:10, fontWeight:700, letterSpacing:"0.14em", textTransform:"uppercase" },
  desc:      { fontSize:10, color:"#2a3a58", lineHeight:1.3 },
  scoreArea: { display:"flex", alignItems:"center", gap:7, flexShrink:0 },
  barWrap:   { width:64, height:4, background:"#101b30", borderRadius:2, overflow:"hidden" },
  barFill:   { height:"100%", borderRadius:2, transition:"width 0.5s ease" },
  pct:       { fontFamily:"'Space Mono',monospace", fontSize:10, fontWeight:700, width:30, textAlign:"right" },
  lbl:       { fontSize:9, width:36 },
  noData:    { fontSize:10, color:"#1e2e44", fontStyle:"italic" },
  editBtn:   { background:"none", border:"1px solid rgba(80,100,180,0.18)", borderRadius:5, color:"#3a4a68", fontSize:10, cursor:"pointer", padding:"3px 9px", fontFamily:"'Space Mono',monospace" },
  fullBar:   { height:2, background:"#101b30", overflow:"hidden", flexShrink:0 },
  fullFill:  { height:"100%", transition:"width 0.6s ease" },
  body:      { flex:1, overflow:"hidden", padding:"12px 16px" },
  prose:     { fontSize:13.5, lineHeight:1.75, whiteSpace:"pre-wrap", cursor:"text", height:"100%", overflowY:"auto" },
  dot:       { display:"inline-block", width:6, height:6, background:"#7c8fff", borderRadius:"50%", animation:"blink 1.2s infinite" },
  editTA:    { flex:1, background:"rgba(16,24,44,0.9)", border:"1px solid", borderRadius:7, padding:"10px 13px", color:"#c0cfea", fontSize:13, resize:"none", lineHeight:1.65, width:"100%", minHeight:100 },
  saveBtn:   { border:"1px solid", borderRadius:5, fontSize:10, cursor:"pointer", padding:"4px 14px", fontFamily:"'Space Mono',monospace" },
  cancelBtn: { background:"none", border:"1px solid rgba(80,100,180,0.15)", borderRadius:5, color:"#3a4a68", fontSize:10, cursor:"pointer", padding:"4px 14px", fontFamily:"'Space Mono',monospace" },
};

export default function Block({ panel, content, conf, polishing, rescoring, onSave }) {
  const [editing, setEditing] = useState(false);
  const [draft,   setDraft]   = useState(content);
  const meta  = PANELS[panel];
  const taRef = useRef(null);

  useEffect(() => { setDraft(content); }, [content]);
  useEffect(() => { if (editing) taRef.current?.focus(); }, [editing]);

  const save   = () => { onSave(draft); setEditing(false); };
  const cancel = () => { setDraft(content); setEditing(false); };
  const c      = scoreColor(conf);
  const filled = !!content;

  return (
    <div style={{ ...BL.card, borderTopColor: meta.accent }}>
      {/* ── Header ── */}
      <div style={BL.header}>
        <span style={{ ...BL.icon, color: meta.accent }}>{meta.icon}</span>
        <div style={BL.mid}>
          <span style={{ ...BL.title, color: meta.accent }}>{meta.label}</span>
          <span style={BL.desc}>{meta.desc}</span>
        </div>
        <div style={BL.scoreArea}>
          {rescoring ? (
            <span style={{ fontSize:9, color:"#f5c542", fontStyle:"italic", animation:"blink 1s infinite" }}>re-scoring…</span>
          ) : conf != null ? (
            <>
              <div style={BL.barWrap}>
                <div style={{ ...BL.barFill, width:`${conf*100}%`, background:`linear-gradient(90deg,${c},${c}88)` }}/>
              </div>
              <span style={{ ...BL.pct, color:c }}>{scorePct(conf)}</span>
              <span style={{ ...BL.lbl, color:c }}>{scoreLabel(conf)}</span>
            </>
          ) : (
            <span style={BL.noData}>No data yet</span>
          )}
          {!editing && filled && !polishing && !rescoring && (
            <button onClick={() => setEditing(true)} style={BL.editBtn}>✎ Edit</button>
          )}
        </div>
      </div>

      {/* ── Score bar ── */}
      {conf != null && (
        <div style={BL.fullBar}>
          <div style={{ ...BL.fullFill, width:`${conf*100}%`, background:`${c}33` }}/>
        </div>
      )}

      {/* ── Body ── */}
      <div style={BL.body}>
        {polishing ? (
          <div style={{ display:"flex", alignItems:"center", gap:8 }}>
            {[0, 0.25, 0.5].map(d => (
              <span key={d} style={{ ...BL.dot, animationDelay:`${d}s` }}/>
            ))}
            <span style={{ fontSize:11, color:"#3a4a68", fontStyle:"italic" }}>SAGE is polishing…</span>
          </div>
        ) : !editing ? (
          <div
            style={{ ...BL.prose, color: filled ? "#b0c0dc" : "#1e2e44" }}
            onClick={filled ? () => setEditing(true) : undefined}
            title={filled ? "Click to edit" : ""}
          >
            {filled
              ? content
              : <span style={{ fontStyle:"italic", fontSize:12 }}>Content will appear here as you answer questions.</span>
            }
          </div>
        ) : (
          <div style={{ display:"flex", flexDirection:"column", gap:8, height:"100%" }}>
            <textarea
              ref={taRef}
              value={draft}
              onChange={e => setDraft(e.target.value)}
              onKeyDown={e => e.key === "Escape" && cancel()}
              style={{ ...BL.editTA, borderColor:`${meta.accent}44` }}
              rows={5}
            />
            <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between" }}>
              <span style={{ fontSize:10, color:"#2a3a58", fontStyle:"italic" }}>Save to re-score changes</span>
              <div style={{ display:"flex", gap:7 }}>
                <button onClick={cancel} style={BL.cancelBtn}>Cancel</button>
                <button onClick={save} style={{ ...BL.saveBtn, background:`${meta.accent}18`, borderColor:`${meta.accent}55`, color:meta.accent }}>Save</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
