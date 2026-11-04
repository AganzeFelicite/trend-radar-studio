import React from "react";

// Original cartoon news reporter, drawn in code so every video uses the exact same character.
// Canvas: 1080x1920 (9:16). Head centre ~ (540, 770); mouth centre (540, 905).

export type Pose = "talk" | "shocked" | "laughing" | "thinking" | "celebrating";
// Rhubarb Lip Sync mouth shapes: A=M/B/P, B=most consonants, C=EH, D=AA, E=AO/ER, F=OO/W, G=F/V, H=L, X=rest.
export type Mouth = "X" | "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H";
export const MOUTHS: Mouth[] = ["X", "A", "B", "C", "D", "E", "F", "G", "H"];
export const POSES: Pose[] = ["talk", "shocked", "laughing", "thinking", "celebrating"];

export const COLORS = {
  skin: "#8d5a3b", skinShade: "#74482f", hair: "#1b1410",
  blazer: "#22305a", blazerShade: "#18223f", shirt: "#0fb5a8",
  headset: "#1f2233", mic: "#2a2d3e", teal: "#00e5d4", magenta: "#ff2bd6", yellow: "#ffd400",
  lip: "#4a2419", mouth: "#3a1410", tongue: "#e0606e", white: "#fbf7f2", iris: "#3b2416",
  bg1: "#2a1a5e", bg2: "#0b1026", desk: "#141a33",
};
const c = COLORS;
const SCALE = 1.3;
const DESK_Y = 1660;
// Where the face lands after scaling, for FilmCraft layouts (plan.json `face` / `head_top`) and crops.
export const FACE = { x: 540, y: 503, headTop: 152 };

const MouthShape: React.FC<{ m: Mouth | "side" }> = ({ m }) => {
  const teeth = (w: number, y: number) => (
    <path d={`M${-w},${y} Q0,${y - 8} ${w},${y} L${w - 3},${y + 10} Q0,${y + 5} ${-w + 3},${y + 10} Z`} fill={c.white} />
  );
  const open = (w: number, top: number, depth: number, tongueY: number, tongueW: number) => (
    <g>
      <path d={`M${-w},${top} Q0,${top - 12} ${w},${top} Q0,${depth} ${-w},${top} Z`} fill={c.mouth} stroke={c.lip} strokeWidth={6} strokeLinejoin="round" />
      {teeth(w - 10, top - 2)}
      <ellipse cx={0} cy={tongueY} rx={tongueW} ry={tongueW / 2.2} fill={c.tongue} />
    </g>
  );
  switch (m) {
    case "X": return <path d="M-46,0 Q0,20 46,0" stroke={c.lip} strokeWidth={9} fill="none" strokeLinecap="round" />;
    case "A": return <path d="M-40,4 Q0,10 40,4" stroke={c.lip} strokeWidth={11} fill="none" strokeLinecap="round" />;
    case "B": return open(44, -2, 26, 14, 12);
    case "C": return open(50, -6, 50, 24, 22);
    case "D": return open(60, -10, 82, 40, 30);
    case "E": return (
      <g>
        <ellipse cx={0} cy={8} rx={30} ry={32} fill={c.mouth} stroke={c.lip} strokeWidth={6} />
        <ellipse cx={0} cy={28} rx={16} ry={7} fill={c.tongue} />
      </g>
    );
    case "F": return <ellipse cx={0} cy={6} rx={17} ry={20} fill={c.mouth} stroke={c.lip} strokeWidth={8} />;
    case "G": return (
      <g>
        <path d="M-40,0 Q0,-8 40,0 Q0,24 -40,0 Z" fill={c.mouth} stroke={c.lip} strokeWidth={6} />
        <path d="M-30,-4 L30,-4 L28,9 L-28,9 Z" fill={c.white} />
      </g>
    );
    case "H": return open(50, -6, 50, 10, 20);
    case "side": return <path d="M-30,6 Q10,10 40,-6" stroke={c.lip} strokeWidth={9} fill="none" strokeLinecap="round" />;
  }
};

type Eyes = "open" | "wide" | "happy" | "closed";
const Eye: React.FC<{ x: number; kind: Eyes; look: [number, number] }> = ({ x, kind, look }) => {
  const y = 770;
  if (kind === "happy") return <path d={`M${x - 30},${y + 8} Q${x},${y - 24} ${x + 30},${y + 8}`} stroke={c.iris} strokeWidth={10} fill="none" strokeLinecap="round" />;
  if (kind === "closed") return <path d={`M${x - 30},${y + 4} Q${x},${y + 16} ${x + 30},${y + 4}`} stroke={c.iris} strokeWidth={9} fill="none" strokeLinecap="round" />;
  const wide = kind === "wide";
  const [lx, ly] = look;
  return (
    <g>
      <ellipse cx={x} cy={y} rx={wide ? 38 : 34} ry={wide ? 46 : 38} fill={c.white} />
      <circle cx={x + lx} cy={y + ly + 4} r={wide ? 15 : 20} fill={c.iris} />
      <circle cx={x + lx} cy={y + ly + 4} r={wide ? 7 : 10} fill="#0d0705" />
      <circle cx={x + lx - 7} cy={y + ly - 4} r={6} fill={c.white} />
    </g>
  );
};

const Brow: React.FC<{ x: number; lift: number; tilt: number; flip?: boolean }> = ({ x, lift, tilt, flip }) => {
  const s = flip ? -1 : 1;
  const y = 712 + lift;
  return <path d={`M${x - 36 * s},${y + tilt} Q${x},${y - 14} ${x + 36 * s},${y - tilt}`} stroke={c.hair} strokeWidth={15} fill="none" strokeLinecap="round" />;
};

const Fist: React.FC<{ x: number; y: number }> = ({ x, y }) => (
  <g>
    <circle cx={x} cy={y} r={40} fill={c.skin} />
    <path d={`M${x - 22},${y - 12} Q${x},${y - 22} ${x + 22},${y - 12}`} stroke={c.skinShade} strokeWidth={6} fill="none" strokeLinecap="round" />
  </g>
);

const Arm: React.FC<{ d: string }> = ({ d }) => <path d={d} stroke={c.blazer} strokeWidth={92} fill="none" strokeLinecap="round" />;

type Face = { lift: [number, number]; tilt: number; eyes: Eyes; look: [number, number]; mouth?: Mouth | "side"; head: number };
const FACES: Record<Pose, Face> = {
  talk: { lift: [0, 0], tilt: 0, eyes: "open", look: [0, 0], head: 0 },
  shocked: { lift: [-30, -30], tilt: 0, eyes: "wide", look: [0, 0], mouth: "E", head: 0 },
  laughing: { lift: [-12, -12], tilt: -4, eyes: "happy", look: [0, 0], mouth: "D", head: -5 },
  thinking: { lift: [-26, 2], tilt: 4, eyes: "open", look: [-10, -12], mouth: "side", head: 3 },
  celebrating: { lift: [-16, -16], tilt: -4, eyes: "happy", look: [0, 0], mouth: "D", head: 3 },
};

// Arms drawn behind the desk; hands are drawn after the desk so they rest on it.
const ARMS: Record<Pose, { arms: string[]; fists: [number, number][] }> = {
  talk: { arms: ["M320,1230 Q300,1500 420,1660", "M760,1230 Q780,1500 660,1660"], fists: [[425, 1665], [655, 1665]] },
  shocked: { arms: ["M320,1230 Q230,1080 370,960", "M760,1230 Q850,1080 710,960"], fists: [[380, 945], [700, 945]] },
  laughing: { arms: ["M320,1230 Q300,1500 420,1660", "M760,1230 Q780,1500 660,1660"], fists: [[425, 1665], [655, 1665]] },
  thinking: { arms: ["M320,1230 Q330,1110 470,1030", "M760,1230 Q780,1500 660,1660"], fists: [[480, 1020], [655, 1665]] },
  celebrating: { arms: ["M320,1200 Q190,1000 250,720", "M760,1200 Q890,1000 830,720"], fists: [[255, 700], [825, 700]] },
};

export const Studio: React.FC = () => (
  <g>
    <defs>
      <radialGradient id="studio-bg" cx="50%" cy="38%" r="80%">
        <stop offset="0" stopColor={c.bg1} />
        <stop offset="1" stopColor={c.bg2} />
      </radialGradient>
      <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14" /></filter>
    </defs>
    <rect width={1080} height={1920} fill="url(#studio-bg)" />
    {[[60, c.teal], [1006, c.magenta]].map(([x, col]) => (
      <g key={String(x)}>
        <rect x={Number(x)} y={160} width={16} height={1460} rx={8} fill={String(col)} filter="url(#glow)" opacity={0.9} />
        <rect x={Number(x) + 4} y={170} width={8} height={1440} rx={4} fill={String(col)} />
      </g>
    ))}
    {/* our own "radar" sign: no third-party logos anywhere */}
    <g opacity={0.35} stroke={c.teal} fill="none" strokeWidth={5}>
      {[50, 100, 150].map((r) => <circle key={r} cx={850} cy={360} r={r} />)}
      <path d="M850,360 L960,250" strokeWidth={8} />
    </g>
    <circle cx={930} cy={300} r={12} fill={c.magenta} opacity={0.8} />
  </g>
);

const Desk: React.FC = () => (
  <g>
    <rect x={0} y={1660} width={1080} height={260} fill={c.desk} />
    <rect x={0} y={1652} width={1080} height={12} fill={c.teal} filter="url(#glow)" />
    <rect x={0} y={1655} width={1080} height={6} fill={c.teal} />
  </g>
);

export const Reporter: React.FC<{ pose?: Pose; mouth?: Mouth; blink?: boolean; background?: boolean; crop?: string; nod?: number }> = ({
  pose = "talk", mouth = "X", blink = false, background = true, crop = "0 0 1080 1920", nod = 0,
}) => {
  const f = FACES[pose];
  const a = ARMS[pose];
  const eyes: Eyes = blink && f.eyes !== "happy" ? "closed" : f.eyes;
  return (
    <svg viewBox={crop} width="100%" height="100%">
      {background && <Studio />}
      <g transform={`translate(540 ${DESK_Y}) scale(${SCALE}) translate(-540 ${-DESK_Y})`}>
      {/* body */}
      <rect x={482} y={900} width={116} height={170} rx={40} fill={c.skinShade} />
      <path d="M290,1260 C300,1110 420,1050 540,1050 C660,1050 780,1110 790,1260 L860,1920 L220,1920 Z" fill={c.blazer} />
      <path d="M478,1052 L540,1210 L602,1052 Z" fill={c.shirt} />
      <path d="M478,1052 L540,1210 L470,1330 L430,1080 Z" fill={c.blazerShade} />
      <path d="M602,1052 L540,1210 L610,1330 L650,1080 Z" fill={c.blazerShade} />
      {/* press badge on a lanyard */}
      <path d="M500,1062 L640,1330 M580,1062 L660,1330" stroke={c.teal} strokeWidth={6} />
      <rect x={605} y={1325} width={100} height={124} rx={12} fill={c.white} />
      <rect x={605} y={1325} width={100} height={34} rx={12} fill={c.teal} />
      <text x={655} y={1406} fontSize={30} fontWeight={900} textAnchor="middle" fill={c.bg2} fontFamily="Arial Rounded MT Bold, Arial, sans-serif">PRESS</text>
      {a.arms.map((d) => <Arm key={d} d={d} />)}
      <Desk />
      {/* head */}
      <g transform={`rotate(${f.head + nod} 540 900)`}>
        <ellipse cx={372} cy={795} rx={26} ry={40} fill={c.skinShade} />
        <ellipse cx={708} cy={795} rx={26} ry={40} fill={c.skinShade} />
        <ellipse cx={540} cy={775} rx={172} ry={198} fill={c.skin} />
        {/* hair: short curly top with a fade */}
        <path d="M372,735 C362,575 460,548 540,548 C620,548 718,575 708,735 C690,668 640,650 540,652 C440,650 390,668 372,735 Z" fill={c.hair} />
        {[400, 440, 480, 520, 560, 600, 640, 680].map((x, i) => <circle key={x} cx={x} cy={590 - (i % 2) * 14 - (x > 420 && x < 660 ? 16 : 0)} r={34} fill={c.hair} />)}
        {/* headset */}
        <path d="M350,780 C336,560 440,500 540,500 C640,500 744,560 730,780" stroke={c.headset} strokeWidth={36} fill="none" strokeLinecap="round" />
        {[350, 730].map((x) => (
          <g key={x}>
            <rect x={x - 44} y={722} width={88} height={160} rx={40} fill={c.headset} />
            <rect x={x - 30} y={738} width={60} height={128} rx={28} fill="none" stroke={x < 540 ? c.teal : c.magenta} strokeWidth={8} />
          </g>
        ))}
        <path d="M352,868 C356,950 400,972 458,958" stroke={c.mic} strokeWidth={13} fill="none" strokeLinecap="round" />
        <ellipse cx={470} cy={955} rx={22} ry={18} fill={c.mic} />
        <circle cx={457} cy={945} r={5} fill="#ff3b3b" />
        {/* face */}
        <Brow x={470} lift={f.lift[0]} tilt={f.tilt} />
        <Brow x={610} lift={f.lift[1]} tilt={f.tilt} flip />
        <Eye x={470} kind={eyes} look={f.look} />
        <Eye x={610} kind={eyes} look={f.look} />
        <path d="M540,792 C530,830 522,846 540,853 C552,857 560,851 563,845" stroke={c.skinShade} strokeWidth={7} fill="none" strokeLinecap="round" />
        <ellipse cx={440} cy={858} rx={26} ry={14} fill="#b0654a" opacity={0.35} />
        <ellipse cx={640} cy={858} rx={26} ry={14} fill="#b0654a" opacity={0.35} />
        <g transform="translate(540 905)"><MouthShape m={mouth !== "X" ? mouth : f.mouth ?? mouth} /></g>
      </g>
      {/* hands last: they rest on the desk or sit in front of the face */}
      {a.fists.map(([x, y]) => <Fist key={`${x},${y}`} x={x} y={y} />)}
      </g>
    </svg>
  );
};
