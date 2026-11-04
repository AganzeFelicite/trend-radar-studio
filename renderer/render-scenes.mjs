// Renders many Broll clips with one bundle: node render-scenes.mjs out/broll.json out/broll
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import { mkdirSync, readFileSync } from "node:fs";
import path from "node:path";

const [list, outDir] = process.argv.slice(2);
const items = JSON.parse(readFileSync(list, "utf8"));
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
mkdirSync(outDir, { recursive: true });
for (const { id, props } of items) {
  const composition = await selectComposition({ serveUrl, id: "Broll", inputProps: props });
  await renderMedia({ composition, serveUrl, codec: "h264", muted: true, inputProps: props, outputLocation: `${outDir}/${id}.mp4` });
  console.log(`rendered ${id}`);
}
