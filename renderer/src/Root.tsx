import { Composition, Still } from "remotion";
import { Reporter, type Mouth, type Pose } from "./Reporter";
import { Sheet } from "./Sheet";
import { FPS, TalkingClip, talkMetadata, type TalkProps } from "./TalkingClip";

const Frame: React.FC<{ pose: Pose; mouth: Mouth }> = (p) => <Reporter {...p} />;
const noTalk: TalkProps = { audio: "test/line.wav", duration: 1, cues: [], poses: [] };

export const Root = () => (
  <>
    <Still id="CharacterSheet" component={Sheet} width={1800} height={900} />
    <Still id="ReporterStill" component={Frame} width={1080} height={1920} defaultProps={{ pose: "talk" as Pose, mouth: "C" as Mouth }} />
    <Composition id="TalkingClip" component={TalkingClip} width={1080} height={1920} fps={FPS} durationInFrames={30}
      defaultProps={noTalk} calculateMetadata={talkMetadata} />
  </>
);
