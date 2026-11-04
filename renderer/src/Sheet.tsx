import React from "react";
import { AbsoluteFill } from "remotion";
import { COLORS, MOUTHS, POSES, Reporter } from "./Reporter";

const label: React.CSSProperties = { color: "white", fontFamily: "Arial Rounded MT Bold, Arial, sans-serif", fontSize: 26, textAlign: "center", marginTop: 8 };

// Character sheet for approval (V2.2): the five poses plus every lip-sync mouth shape.
export const Sheet: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: COLORS.bg2, padding: 40, gap: 30 }}>
    <div style={{ display: "flex", gap: 24, justifyContent: "center" }}>
      {POSES.map((p) => (
        <div key={p}>
          <div style={{ width: 324, height: 576, borderRadius: 16, overflow: "hidden" }}><Reporter pose={p} mouth="C" /></div>
          <div style={label}>{p}</div>
        </div>
      ))}
    </div>
    <div style={{ display: "flex", gap: 14, justifyContent: "center" }}>
      {MOUTHS.map((m) => (
        <div key={m}>
          <div style={{ width: 160, height: 176, borderRadius: 12, overflow: "hidden", background: COLORS.skin }}>
            {/* crop of the face around the mouth */}
            <Reporter mouth={m} crop="358 413 364 400" />
          </div>
          <div style={label}>{m}</div>
        </div>
      ))}
    </div>
  </AbsoluteFill>
);
