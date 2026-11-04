import { Composition, Still } from "remotion";
import { Reporter, type Mouth, type Pose } from "./Reporter";
import { Sheet } from "./Sheet";

const Frame: React.FC<{ pose: Pose; mouth: Mouth }> = (p) => <Reporter {...p} />;

export const Root = () => (
  <>
    <Still id="CharacterSheet" component={Sheet} width={1800} height={900} />
    <Still id="ReporterStill" component={Frame} width={1080} height={1920} defaultProps={{ pose: "talk" as Pose, mouth: "C" as Mouth }} />
    {/* ponytail: placeholder kept for the container smoke test; replaced by the talking-clip composition in V2.4 */}
    <Composition id="Placeholder" component={() => null} width={1080} height={1920} fps={30} durationInFrames={30} />
  </>
);
