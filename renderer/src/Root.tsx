import { Composition, Still } from "remotion";
import { Broll, brollMetadata, type BrollProps } from "./Broll";
import { Reporter, type Mouth, type Pose } from "./Reporter";
import { Sheet } from "./Sheet";
import { FPS, TalkingClip, talkMetadata, type TalkProps } from "./TalkingClip";

const Frame: React.FC<{ pose: Pose; mouth: Mouth }> = (p) => <Reporter {...p} />;
const noTalk: TalkProps = { audio: "test/line.wav", duration: 1, cues: [], poses: [] };
const sampleCard: BrollProps = {
  kind: "card", duration: 4, title: "Pre-load holds #1", sources: ["destructoid.com"], footer: "Data: Trend Radar · 2026-11-04 09:00 UTC",
  rows: [{ topic: "Pre-load", metric: "rank", value: "#1" }, { topic: "Pre-load", metric: "score (0-100)", value: "68" },
    { topic: "File size", metric: "rank", value: "#3" }, { topic: "File size", metric: "score (0-100)", value: "36" }],
};

export const Root = () => (
  <>
    <Still id="CharacterSheet" component={Sheet} width={1800} height={900} />
    <Still id="ReporterStill" component={Frame} width={1080} height={1920} defaultProps={{ pose: "talk" as Pose, mouth: "C" as Mouth }} />
    <Composition id="TalkingClip" component={TalkingClip} width={1080} height={1920} fps={FPS} durationInFrames={30}
      defaultProps={noTalk} calculateMetadata={talkMetadata} />
    <Composition id="Broll" component={Broll} width={1080} height={1920} fps={FPS} durationInFrames={30}
      defaultProps={sampleCard} calculateMetadata={brollMetadata} />
  </>
);
