import React from "react";
import { AbsoluteFill } from "remotion";
import { Character, HOST, NAMES, PALETTES, type Cast } from "./Cast";
import { MOUTHS, POSES, type Reporter } from "./Reporter";

const label: React.CSSProperties = { color: "white", fontFamily: "DejaVu Sans, Arial, sans-serif", fontSize: 26, textAlign: "center", marginTop: 8 };

export type SheetProps = { who?: Cast }; // a candidate from Cast.tsx; the host when unset

// Character sheet for approval (V2.2, V7.1): the five poses plus every lip-sync mouth shape.
export const Sheet: React.FC<SheetProps> = ({ who = HOST }) => {
  const Fig: React.FC<React.ComponentProps<typeof Reporter>> = (p) => <Character who={who} {...p} />;
  const skin = PALETTES[who].skin;
  return (
    <AbsoluteFill style={{ backgroundColor: PALETTES[who].bg2, padding: 40, gap: 30 }}>
      <div style={{ ...label, fontSize: 40, marginTop: 0 }}>{NAMES[who]}</div>
      <div style={{ display: "flex", gap: 24, justifyContent: "center" }}>
        {POSES.map((p) => (
          <div key={p}>
            <div style={{ width: 324, height: 576, borderRadius: 16, overflow: "hidden" }}><Fig pose={p} mouth={p === "talk" ? "C" : "X"} /></div>
            <div style={label}>{p}</div>
          </div>
        ))}
      </div>
      <div style={{ display: "flex", gap: 14, justifyContent: "center" }}>
        {MOUTHS.map((m) => (
          <div key={m}>
            <div style={{ width: 160, height: 176, borderRadius: 12, overflow: "hidden", background: skin }}>
              {/* crop of the face around the mouth */}
              <Fig mouth={m} crop="358 413 364 400" />
            </div>
            <div style={label}>{m}</div>
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};
