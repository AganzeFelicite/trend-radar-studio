// Our own B-roll (D18): full-frame data cards and headlines in the studio look, one clip per card/headline scene.
// Values are shown exactly as given (no count-up animation: no frame shows a number that isn't the fact).
import { useEffect, useState } from "react";
import {
  AbsoluteFill, cancelRender, continueRender, delayRender, spring, staticFile, useCurrentFrame, useVideoConfig,
  type CalculateMetadataFunction,
} from "remotion";
import { COLORS as c, Studio } from "./Reporter";
import { FPS } from "./TalkingClip";

export type Row = { topic: string; metric: string; value: string };
export type BrollProps = { kind: "card" | "headline"; duration: number; title: string; rows: Row[]; sources: string[]; footer: string };
export const brollMetadata: CalculateMetadataFunction<BrollProps> = ({ props }) => ({
  durationInFrames: Math.max(1, Math.ceil(props.duration * FPS)),
});

export const ANTON = "Anton, DejaVu Sans, sans-serif";
const SANS = "DejaVu Sans, sans-serif";

export const useAnton = () => {
  const [handle] = useState(() => delayRender("Anton font"));
  useEffect(() => {
    new FontFace("Anton", `url('${staticFile("fonts/Anton-Regular.ttf")}')`).load()
      .then((f) => { document.fonts.add(f); continueRender(handle); })
      .catch((e) => cancelRender(e));
  }, [handle]);
};

// element i slides up and fades in, 6 frames after element i-1
const useEnter = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (i: number): React.CSSProperties => {
    const p = spring({ frame: frame - i * 6, fps, config: { damping: 14 } });
    return { opacity: p, transform: `translateY(${(1 - p) * 50}px)` };
  };
};

const byTopic = (rows: Row[]) =>
  rows.reduce<[string, Row[]][]>((acc, r) => {
    const g = acc.find(([t]) => t === r.topic);
    if (g) g[1].push(r);
    else acc.push([r.topic, [r]]);
    return acc;
  }, []);

const Card: React.FC<BrollProps> = ({ title, rows, sources, footer }) => {
  const enter = useEnter();
  let i = 0;
  return (
    // ends at y 1420: the lower band is your caption line (y 1530)
    <div style={{ position: "absolute", left: 110, right: 110, top: 240, bottom: 500, display: "flex", flexDirection: "column", gap: 34 }}>
      <div style={{ ...enter(i++), alignSelf: "flex-start", border: `3px solid ${c.teal}`, color: c.teal, borderRadius: 40,
        padding: "8px 26px", fontFamily: SANS, fontWeight: 700, fontSize: 32, letterSpacing: 2 }}>
        {rows.length ? "Trend Radar data" : "Receipts"}
      </div>
      <div style={{ ...enter(i++), fontFamily: ANTON, fontSize: 96, lineHeight: 1.05, color: c.white }}>{title}</div>
      {byTopic(rows).slice(0, 3).map(([topic, rs]) => (
        <div key={topic} style={{ ...enter(i++), background: "rgba(11,16,38,0.82)", border: `3px solid ${c.teal}`, borderRadius: 28, padding: "22px 30px" }}>
          <div style={{ fontFamily: ANTON, fontSize: 56, color: c.teal }}>{topic}</div>
          <div style={{ display: "flex", gap: 34, marginTop: 6 }}>
            {rs.slice(0, 3).map((r) => (
              <div key={r.metric} style={{ flex: 1 }}>
                <div style={{ fontFamily: ANTON, fontSize: 104, lineHeight: 1.1, color: c.yellow }}>{r.value}</div>
                <div style={{ fontFamily: SANS, fontSize: 28, color: c.white, opacity: 0.8 }}>{r.metric}</div>
              </div>
            ))}
          </div>
        </div>
      ))}
      {sources.length > 0 && (
        <div style={{ ...enter(i++), display: "flex", flexWrap: "wrap", gap: 18 }}>
          {sources.map((s) => (
            <div key={s} style={{ background: c.magenta, color: c.white, borderRadius: 40, padding: "10px 26px", fontFamily: SANS, fontWeight: 700, fontSize: 34 }}>{s}</div>
          ))}
        </div>
      )}
      <div style={{ ...enter(i++), marginTop: "auto", fontFamily: SANS, fontSize: 30, color: c.white, opacity: 0.6 }}>{footer}</div>
    </div>
  );
};

const Headline: React.FC<BrollProps> = ({ title }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const words = title.split(/\s+/);
  const bar = spring({ frame: frame - words.length * 5, fps, config: { damping: 18 } });
  return (
    <div style={{ position: "absolute", left: 110, right: 110, top: 520, display: "flex", flexDirection: "column", alignItems: "center" }}>
      <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", columnGap: 30, textAlign: "center" }}>
        {words.map((w, i) => {
          const p = spring({ frame: frame - i * 5, fps, config: { damping: 11 } });
          return (
            <span key={i} style={{ fontFamily: ANTON, fontSize: 150, lineHeight: 1.08, color: i === words.length - 1 ? c.yellow : c.white,
              display: "inline-block", opacity: Math.min(1, p * 2), transform: `scale(${0.6 + 0.4 * p})` }}>{w}</span>
          );
        })}
      </div>
      <div style={{ height: 16, width: 640 * bar, background: c.magenta, borderRadius: 8, marginTop: 36 }} />
    </div>
  );
};

export const Broll: React.FC<BrollProps> = (props) => {
  useAnton();
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const push = 1 + 0.03 * (frame / durationInFrames); // slow push-in, like your full-frame shots
  return (
    <AbsoluteFill style={{ background: c.bg2 }}>
      <svg viewBox="0 0 1080 1920" width="100%" height="100%" style={{ position: "absolute" }}><Studio /></svg>
      <AbsoluteFill style={{ transform: `scale(${push})` }}>
        {props.kind === "card" ? <Card {...props} /> : <Headline {...props} />}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
