import { AbsoluteFill, Composition } from "remotion";

// ponytail: placeholder so the image can prove Chrome renders; V4.1 replaces it with the signature template.
const Placeholder = () => <AbsoluteFill style={{ backgroundColor: "#0B0B14" }} />;

export const Root = () => (
  <Composition id="Placeholder" component={Placeholder} width={1080} height={1920} fps={30} durationInFrames={30} />
);
