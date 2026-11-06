// Thumbnail options (V4.3): our own design, the reporter in a reaction pose with the script's thumbnail text.
import { AbsoluteFill } from "remotion";
import { ANTON, useAnton } from "./Broll";
import { Host } from "./Cast";
import { COLORS as c, type Pose } from "./Reporter";

export type ThumbProps = { text: string; pose: Pose; accent: string };

export const Thumbnail: React.FC<ThumbProps> = ({ text, pose, accent }) => {
  useAnton();
  return (
    <AbsoluteFill>
      <Host pose={pose} mouth="X" />
      {/* over the blazer, under the face: readable in the feed's centre crop */}
      <div style={{ position: "absolute", left: 60, right: 60, top: 1130, display: "flex", flexDirection: "column", alignItems: "center" }}>
        <div style={{ fontFamily: ANTON, fontSize: 168, lineHeight: 1.02, textAlign: "center", color: c.yellow,
          WebkitTextStroke: "14px #000", paintOrder: "stroke fill", textShadow: "0 10px 0 rgba(0,0,0,0.45)" }}>{text}</div>
        <div style={{ height: 22, width: 560, background: accent, borderRadius: 11, marginTop: 26 }} />
      </div>
    </AbsoluteFill>
  );
};
