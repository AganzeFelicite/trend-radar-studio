import React from "react";
import { AbsoluteFill, type CalculateMetadataFunction, Html5Audio, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Character, type Cast } from "./Cast";
import { Reporter, type Mouth, type Pose } from "./Reporter";

// The host's A-roll: the voice track plus mouth cues from api/studio/voice.py (Rhubarb-style).
// FilmCraft uses this clip where the real shorts use phone footage.
type Span = { start: number; end: number };
export type TalkProps = {
  audio: string; // path under public/
  duration: number; // seconds
  cues: (Span & { value: Mouth })[];
  poses: (Span & { pose: Pose })[];
  who?: Cast; // a candidate from Cast.tsx; GameReporter when unset
};

export const FPS = 30;
export const talkMetadata: CalculateMetadataFunction<TalkProps> = ({ props }) => ({
  durationInFrames: Math.ceil((props.duration + 0.5) * FPS),
});

const at = <T extends Span>(spans: T[], t: number) => spans.find((s) => s.start <= t && t < s.end);
// ~every 3.5 s for 4 frames, with a second irregular rhythm so blinks don't look mechanical.
const blinking = (f: number) => f % 105 < 4 || (f + 41) % 167 < 3;

export const TalkingClip: React.FC<TalkProps> = ({ audio, cues, poses, who }) => {
  const frame = useCurrentFrame();
  const t = frame / useVideoConfig().fps;
  const mouth = at(cues, t)?.value ?? "X";
  const p = { pose: at(poses, t)?.pose ?? "talk", mouth, blink: blinking(frame), nod: mouth === "X" ? 0 : Math.sin(frame / 7) * 1.2 };
  return (
    <AbsoluteFill>
      {who ? <Character who={who} {...p} /> : <Reporter {...p} />}
      <Html5Audio src={staticFile(audio)} />
    </AbsoluteFill>
  );
};
