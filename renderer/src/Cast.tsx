import React from "react";
import { Brow, COLORS, Eye, FACES, MouthShape, type Eyes, type Mouth, type Pose } from "./Reporter";

// The three character candidates (docs/CHARACTER-CANDIDATES.md, D22), drawn in code on the reporter's rig:
// same canvas (1080x1920), same head centre, same mouth shapes and poses, so lip-sync and layouts need no change.
export type Cast = "patch" | "auntie" | "coach";
export const CAST: Cast[] = ["patch", "auntie", "coach"];
export const NAMES: Record<Cast, string> = { patch: "Patch", auntie: "Auntie Ping", coach: "Coach Dub" };

type Palette = { skin: string; shade: string; top: string; topShade: string; bg1: string; bg2: string; accent: string; hair: string };
export const PALETTES: Record<Cast, Palette> = {
  patch: { skin: "#6cc26b", shade: "#4b9a4b", top: "#2e2e3c", topShade: "#20202c", bg1: "#0f2a20", bg2: "#05100c", accent: "#7cff6b", hair: "#1d3b1d" },
  auntie: { skin: "#7a4a2e", shade: "#5c361f", top: "#c94b45", topShade: "#a53a35", bg1: "#f6dfae", bg2: "#d2a96c", accent: "#ff8c42", hair: "#1b1410" },
  coach: { skin: "#c98a5a", shade: "#a66d42", top: "#1f5fbf", topShade: "#164a97", bg1: "#2d2d2d", bg2: "#121212", accent: "#ffcc00", hair: "#2b1d12" },
};
const SCALE = 1.3;
const DESK_Y = 1660;
const FONT = "DejaVu Sans, Arial, sans-serif";

// One rig: the reporter's arm paths and hand spots, coloured per character.
const ARMS: Record<Pose, { arms: string[]; hands: [number, number][] }> = {
  talk: { arms: ["M320,1230 Q300,1500 420,1660", "M760,1230 Q780,1500 660,1660"], hands: [[425, 1665], [655, 1665]] },
  shocked: { arms: ["M320,1230 Q230,1080 370,960", "M760,1230 Q850,1080 710,960"], hands: [[380, 945], [700, 945]] },
  laughing: { arms: ["M320,1230 Q300,1500 420,1660", "M760,1230 Q780,1500 660,1660"], hands: [[425, 1665], [655, 1665]] },
  thinking: { arms: ["M320,1230 Q330,1110 470,1030", "M760,1230 Q780,1500 660,1660"], hands: [[480, 1020], [655, 1665]] },
  celebrating: { arms: ["M320,1200 Q190,1000 250,720", "M760,1200 Q890,1000 830,720"], hands: [[255, 700], [825, 700]] },
};

const Hand: React.FC<{ x: number; y: number; p: Palette }> = ({ x, y, p }) => (
  <g>
    <circle cx={x} cy={y} r={40} fill={p.skin} />
    <path d={`M${x - 22},${y - 12} Q${x},${y - 22} ${x + 22},${y - 12}`} stroke={p.shade} strokeWidth={6} fill="none" strokeLinecap="round" />
  </g>
);

const Torso: React.FC<{ p: Palette; neck?: number }> = ({ p, neck = 116 }) => (
  <g>
    <rect x={540 - neck / 2} y={900} width={neck} height={170} rx={40} fill={p.shade} />
    <path d="M290,1260 C300,1110 420,1050 540,1050 C660,1050 780,1110 790,1260 L860,1920 L220,1920 Z" fill={p.top} />
  </g>
);

const Bg: React.FC<{ id: string; p: Palette }> = ({ id, p }) => (
  <g>
    <defs>
      <radialGradient id={id} cx="50%" cy="38%" r="80%"><stop offset="0" stopColor={p.bg1} /><stop offset="1" stopColor={p.bg2} /></radialGradient>
      <filter id="cast-glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14" /></filter>
    </defs>
    <rect width={1080} height={1920} fill={`url(#${id})`} />
  </g>
);

// ---------- A. Patch: the patch-notes gremlin in a server room ----------
const PatchSet: React.FC<{ p: Palette }> = ({ p }) => (
  <g>
    <Bg id="bg-patch" p={p} />
    {[90, 870].map((x) => (
      <g key={x}>
        <rect x={x} y={300} width={120} height={1360} rx={10} fill="#171a22" stroke="#2a2f3d" strokeWidth={4} />
        {Array.from({ length: 14 }, (_, i) => (
          <g key={i}>
            <rect x={x + 12} y={330 + i * 94} width={96} height={70} rx={6} fill="#0f1117" />
            <circle cx={x + 30} cy={365 + i * 94} r={6} fill={(i + x) % 3 ? p.accent : "#ff5050"} />
            <circle cx={x + 50} cy={365 + i * 94} r={6} fill={(i + x) % 2 ? p.accent : "#2a2f3d"} />
          </g>
        ))}
      </g>
    ))}
    <g opacity={0.25} fill="none" stroke={p.accent} strokeWidth={10}>
      <path d="M540,250 L540,420 M470,360 L540,430 L610,360" filter="url(#cast-glow)" />
      <path d="M440,470 L640,470" />
    </g>
  </g>
);

const Patch: React.FC<{ pose: Pose; mouth: Mouth; eyes: Eyes; nod: number; p: Palette }> = ({ pose, mouth, eyes, nod, p }) => {
  const f = FACES[pose];
  const a = ARMS[pose];
  return (
    <g transform={`translate(540 ${DESK_Y}) scale(${SCALE}) translate(-540 ${-DESK_Y})`}>
      <ellipse cx={540} cy={760} rx={250} ry={290} fill={p.top} /> {/* hood behind the head */}
      <Torso p={p} neck={100} />
      <path d="M500,1060 L520,1200 M580,1060 L560,1200" stroke="#9aa0b4" strokeWidth={8} strokeLinecap="round" />
      <circle cx={540} cy={1330} r={58} fill={p.accent} />
      <path d="M540,1296 L540,1352 M512,1328 L540,1358 L568,1328" stroke={p.top} strokeWidth={14} fill="none" strokeLinecap="round" strokeLinejoin="round" />
      {a.arms.map((d) => <path key={d} d={d} stroke={p.top} strokeWidth={92} fill="none" strokeLinecap="round" />)}
      <rect x={0} y={1660} width={1080} height={260} fill="#171a22" />
      <rect x={0} y={1654} width={1080} height={8} fill={p.accent} />
      <g transform={`rotate(${f.head + nod} 540 900)`}>
        <path d="M372,760 L300,640 L392,690 Z" fill={p.skin} /><path d="M708,760 L780,640 L688,690 Z" fill={p.skin} />
        <ellipse cx={540} cy={775} rx={172} ry={198} fill={p.skin} />
        {[500, 540, 580].map((x, i) => <path key={x} d={`M${x},585 Q${x + (i - 1) * 40},500 ${x + (i - 1) * 60},470`} stroke={p.hair} strokeWidth={10} fill="none" strokeLinecap="round" />)}
        {/* goggles pushed up on the forehead; the lenses show scrolling text */}
        <path d="M372,640 Q540,590 708,640" stroke="#20242f" strokeWidth={30} fill="none" />
        {[470, 610].map((x) => (
          <g key={x}>
            <circle cx={x} cy={628} r={52} fill="#20242f" /><circle cx={x} cy={628} r={38} fill="#0b2a14" />
            {[-16, 0, 16].map((dy) => <rect key={dy} x={x - 24} y={622 + dy} width={30 + ((dy + 16) % 20)} height={5} fill={p.accent} opacity={0.7} />)}
          </g>
        ))}
        <Brow x={470} lift={f.lift[0]} tilt={f.tilt} /><Brow x={610} lift={f.lift[1]} tilt={f.tilt} flip />
        <Eye x={470} kind={eyes} look={f.look} /><Eye x={610} kind={eyes} look={f.look} />
        <path d="M540,800 C526,840 520,852 544,856" stroke={p.shade} strokeWidth={7} fill="none" strokeLinecap="round" />
        <g transform="translate(540 905)"><MouthShape m={mouth !== "X" ? mouth : f.mouth ?? mouth} /></g>
      </g>
      {a.hands.map(([x, y]) => <Hand key={`${x},${y}`} x={x} y={y} p={p} />)}
      {pose === "celebrating" && <rect x={530} y={560} width={22} height={34} rx={4} fill="#ff2bd6" transform="rotate(25 541 577)" />} {/* one piece of confetti */}
      {pose === "thinking" && (
        <g transform="rotate(-12 480 1020)">
          <rect x={430} y={930} width={120} height={150} rx={8} fill="#fbf7f2" />
          <text x={490} y={985} fontSize={26} fontWeight={700} textAnchor="middle" fill="#20242f" fontFamily={FONT}>TICKET</text>
          {[1010, 1035, 1060].map((y) => <rect key={y} x={448} y={y} width={84} height={8} fill="#c9ccd6" />)}
        </g>
      )}
    </g>
  );
};

// ---------- B. Auntie Ping: the group-chat auntie at her kitchen table ----------
const AuntieSet: React.FC<{ p: Palette }> = ({ p }) => (
  <g>
    <Bg id="bg-auntie" p={p} />
    <rect x={120} y={260} width={380} height={420} rx={16} fill="#bfe3f5" stroke="#8a5a2b" strokeWidth={16} />
    <path d="M310,260 L310,680 M120,470 L500,470" stroke="#8a5a2b" strokeWidth={10} />
    <path d="M120,260 Q200,480 120,700 Z M500,260 Q420,480 500,700 Z" fill={p.accent} opacity={0.9} />
    <rect x={640} y={520} width={320} height={28} rx={6} fill="#8a5a2b" />
    <rect x={690} y={400} width={200} height={120} rx={14} fill="#5a3a22" />
    <circle cx={740} cy={460} r={34} fill="#d9c7a0" /><rect x={800} y={430} width={70} height={60} rx={6} fill="#d9c7a0" />
    <path d="M870,400 L920,330" stroke="#5a3a22" strokeWidth={8} strokeLinecap="round" />
    {Array.from({ length: 8 }, (_, i) => <rect key={i} x={i * 140} y={1540} width={130} height={110} fill={i % 2 ? "#f2e6cf" : "#e3cfa8"} />)}
  </g>
);

const Auntie: React.FC<{ pose: Pose; mouth: Mouth; eyes: Eyes; nod: number; p: Palette }> = ({ pose, mouth, eyes, nod, p }) => {
  const f = FACES[pose];
  const a = ARMS[pose];
  const [px, py] = a.hands[1];
  return (
    <g transform={`translate(540 ${DESK_Y}) scale(${SCALE}) translate(-540 ${-DESK_Y})`}>
      <Torso p={p} />
      <path d="M478,1052 L540,1230 L602,1052 Z" fill="#ffd54a" />
      {[1280, 1380, 1480].map((y) => <circle key={y} cx={540} cy={y} r={11} fill={p.topShade} />)}
      <circle cx={620} cy={1160} r={22} fill={p.accent} stroke="#ffd54a" strokeWidth={6} />
      {a.arms.map((d) => <path key={d} d={d} stroke={p.top} strokeWidth={92} fill="none" strokeLinecap="round" />)}
      <rect x={0} y={1660} width={1080} height={260} fill="#8a5a2b" />
      <rect x={0} y={1654} width={1080} height={14} fill="#a9733a" />
      <g transform={`rotate(${f.head + nod} 540 900)`}>
        <ellipse cx={372} cy={795} rx={26} ry={40} fill={p.shade} /><ellipse cx={708} cy={795} rx={26} ry={40} fill={p.shade} />
        <circle cx={368} cy={850} r={14} fill="#ffd54a" /><circle cx={712} cy={850} r={14} fill="#ffd54a" />
        <ellipse cx={540} cy={775} rx={172} ry={198} fill={p.skin} />
        {/* headwrap with a side knot and a dot pattern */}
        <path d="M362,730 C350,540 450,470 540,470 C630,470 730,540 718,730 C690,650 630,620 540,622 C450,620 390,650 362,730 Z" fill={p.accent} />
        <path d="M700,560 Q790,500 770,610 Q730,640 700,600 Z M705,565 Q640,480 720,470 Q760,520 705,565 Z" fill={p.accent} />
        {[[430, 600], [500, 540], [580, 530], [650, 590], [540, 580]].map(([x, y]) => <circle key={`${x}${y}`} cx={x} cy={y} r={9} fill="#ffd54a" />)}
        <Brow x={470} lift={f.lift[0]} tilt={f.tilt} /><Brow x={610} lift={f.lift[1]} tilt={f.tilt} flip />
        <Eye x={470} kind={eyes} look={f.look} /><Eye x={610} kind={eyes} look={f.look} />
        {/* big round glasses on a chain */}
        <g fill="none" stroke="#e0a63a" strokeWidth={9}>
          <circle cx={470} cy={776} r={52} /><circle cx={610} cy={776} r={52} /><path d="M522,776 Q540,760 558,776" />
          <path d="M418,780 Q380,860 372,900 M662,780 Q700,860 708,900" strokeWidth={5} strokeDasharray="6 8" />
        </g>
        <path d="M540,792 C528,834 520,848 542,854 C556,858 564,850 566,844" stroke={p.shade} strokeWidth={7} fill="none" strokeLinecap="round" />
        <ellipse cx={440} cy={862} rx={28} ry={15} fill="#c9705a" opacity={0.4} /><ellipse cx={640} cy={862} rx={28} ry={15} fill="#c9705a" opacity={0.4} />
        <g transform="translate(540 905)"><MouthShape m={mouth !== "X" ? mouth : f.mouth ?? mouth} /></g>
      </g>
      {a.hands.map(([x, y]) => <Hand key={`${x},${y}`} x={x} y={y} p={p} />)}
      {/* the phone never leaves her hand; the badge keeps going up */}
      <g transform={`translate(${px + 10} ${py - 70}) rotate(${pose === "celebrating" ? 20 : -8})`}>
        <rect x={-34} y={-70} width={68} height={120} rx={12} fill="#1b1b22" />
        <rect x={-27} y={-60} width={54} height={96} rx={6} fill="#2f80ed" />
        <circle cx={30} cy={-66} r={20} fill="#ff3b3b" />
        <text x={30} y={-59} fontSize={18} fontWeight={700} textAnchor="middle" fill="#fff" fontFamily={FONT}>99+</text>
      </g>
    </g>
  );
};

// ---------- C. Coach Dub: the launch-day coach in the locker room (v2 design, 2026-11-06) ----------
const CoachSet: React.FC<{ p: Palette }> = ({ p }) => (
  <g>
    <Bg id="bg-coach" p={p} />
    <ellipse cx={540} cy={120} rx={520} ry={260} fill="#ffffff" opacity={0.05} /> {/* overhead light */}
    {[30, 170, 770, 910].map((x, i) => (
      <g key={x}>
        <rect x={x} y={180} width={134} height={1480} rx={6} fill="#3b4a5a" stroke="#26313d" strokeWidth={6} />
        <rect x={x + 6} y={186} width={122} height={1468} rx={4} fill="none" stroke="#4b5c6e" strokeWidth={3} />
        {[290, 316, 342].map((y) => <rect key={y} x={x + 28} y={y} width={78} height={7} rx={3} fill="#26313d" />)}
        {[1180, 1206, 1232].map((y) => <rect key={y} x={x + 28} y={y} width={78} height={7} rx={3} fill="#26313d" />)}
        <rect x={x + 34} y={230} width={66} height={26} rx={4} fill="#c9d1d9" />
        <text x={x + 67} y={249} fontSize={16} fontWeight={700} textAnchor="middle" fill="#26313d" fontFamily={FONT}>{["QB", "WR", "TE", "RB"][i]}</text>
        <rect x={x + 104} y={880} width={12} height={46} rx={4} fill="#9aa7b4" />
      </g>
    ))}
    {/* the launch board: our own countdown (the day's data card is pinned here in videos) */}
    <g transform="translate(790 200) rotate(2)">
      <rect x={0} y={0} width={270} height={250} rx={14} fill="#15171c" stroke="#5c6673" strokeWidth={8} />
      <rect x={14} y={14} width={242} height={42} rx={6} fill={p.accent} />
      <text x={135} y={44} fontSize={24} fontWeight={900} textAnchor="middle" fill="#15171c" fontFamily={FONT} letterSpacing={4}>LAUNCH DAY</text>
      <text x={135} y={178} fontSize={120} fontWeight={900} textAnchor="middle" fill={p.accent} fontFamily={FONT}>13</text>
      <text x={135} y={226} fontSize={24} fontWeight={700} textAnchor="middle" fill="#c9d1d9" fontFamily={FONT} letterSpacing={6}>DAYS OUT</text>
    </g>
    {/* bench props: the towel and the water bottle (hydrate) */}
    <path d="M60,1660 Q110,1700 80,1800 Q160,1760 150,1660 Z" fill="#f2f2ee" />
    <rect x={930} y={1560} width={56} height={110} rx={14} fill="#2f80ed" /><rect x={944} y={1540} width={28} height={30} rx={6} fill="#1b4f9c" />
    <rect x={940} y={1600} width={36} height={40} fill="#fbf7f2" opacity={0.8} />
  </g>
);

const Coach: React.FC<{ pose: Pose; mouth: Mouth; eyes: Eyes; nod: number; p: Palette }> = ({ pose, mouth, eyes, nod, p }) => {
  const f = FACES[pose];
  const a = ARMS[pose];
  const [cx, cy] = a.hands[0];
  const clipboard = pose !== "celebrating" && pose !== "shocked";
  return (
    <g transform={`translate(540 ${DESK_Y}) scale(${SCALE}) translate(-540 ${-DESK_Y})`}>
      {/* broad shoulders, thick neck */}
      <rect x={462} y={900} width={156} height={170} rx={44} fill={p.shade} />
      <path d="M250,1270 C260,1100 400,1040 540,1040 C680,1040 820,1100 830,1270 L900,1920 L180,1920 Z" fill={p.top} />
      <path d="M250,1270 C260,1100 400,1040 540,1040 L540,1920 L180,1920 Z" fill={p.topShade} opacity={0.35} />
      {/* collar, placket, chest stripe, tiny trophy, whistle on a lanyard, COACH badge */}
      <path d="M452,1046 L540,1180 L628,1046 L598,1030 L540,1120 L482,1030 Z" fill="#fbf7f2" />
      <path d="M540,1180 L540,1300" stroke={p.topShade} strokeWidth={6} />
      <path d="M300,1400 L780,1400" stroke="#fbf7f2" strokeWidth={14} opacity={0.9} />
      <path d="M650,1180 l18,0 l-9,24 z M650,1180 l18,0 l0,-12 l-18,0 z" fill={p.accent} />
      <path d="M470,1060 Q540,1420 610,1060" stroke="#1b1b1b" strokeWidth={6} fill="none" />
      <rect x={512} y={1392} width={56} height={32} rx={10} fill="#d7dde6" /><circle cx={576} cy={1424} r={18} fill="#d7dde6" /><circle cx={576} cy={1424} r={6} fill="#1b1b1b" />
      <rect x={380} y={1300} width={96} height={64} rx={8} fill="#fbf7f2" /><rect x={380} y={1300} width={96} height={20} rx={8} fill={p.accent} />
      <text x={428} y={1348} fontSize={24} fontWeight={900} textAnchor="middle" fill="#15171c" fontFamily={FONT}>COACH</text>
      {/* short sleeves: bare forearms */}
      {a.arms.map((d) => <path key={d} d={d} stroke={p.skin} strokeWidth={88} fill="none" strokeLinecap="round" />)}
      {/* short sleeves: the first stretch of each arm path, drawn over the bare arm */}
      {a.arms.map((d) => <path key={`s${d}`} d={d} stroke={p.top} strokeWidth={104} fill="none" strokeLinecap="butt" strokeDasharray="170 9999" />)}
      <rect x={0} y={1660} width={1080} height={260} fill="#6b4a2b" />
      <rect x={0} y={1654} width={1080} height={18} fill="#8a6238" /><rect x={0} y={1672} width={1080} height={6} fill="#4f3620" />
      <g transform={`rotate(${f.head + nod} 540 900)`}>
        <ellipse cx={368} cy={800} rx={28} ry={42} fill={p.shade} /><ellipse cx={712} cy={800} rx={28} ry={42} fill={p.shade} />
        <ellipse cx={368} cy={800} rx={12} ry={20} fill={p.skin} opacity={0.6} /><ellipse cx={712} cy={800} rx={12} ry={20} fill={p.skin} opacity={0.6} />
        <path d="M358,780 C352,620 420,560 540,560 C660,560 728,620 722,780 C724,900 690,975 540,978 C390,975 356,900 358,780 Z" fill={p.skin} />
        <path d="M540,978 C440,975 400,930 384,870 L696,870 C680,930 640,975 540,978 Z" fill={p.shade} opacity={0.18} /> {/* jaw shadow */}
        <path d="M400,885 Q540,990 680,885" stroke={p.shade} strokeWidth={5} fill="none" opacity={0.45} strokeDasharray="2 10" /> {/* stubble */}
        <path d="M362,720 C356,590 450,556 540,556 C630,556 724,590 718,720 C690,660 640,640 540,642 C440,640 390,660 362,720 Z" fill={p.hair} />
        {[430, 480, 530, 580, 630].map((x) => <path key={x} d={`M${x},600 q10,-18 24,-26`} stroke="#3d2a1a" strokeWidth={5} fill="none" strokeLinecap="round" />)}
        <rect x={362} y={638} width={356} height={58} rx={29} fill={p.accent} /><rect x={362} y={661} width={356} height={12} fill="#fbf7f2" />
        <Brow x={470} lift={f.lift[0]} tilt={f.tilt} /><Brow x={610} lift={f.lift[1]} tilt={f.tilt} flip />
        <Eye x={470} kind={eyes} look={f.look} /><Eye x={610} kind={eyes} look={f.look} />
        <path d="M540,786 C522,838 514,852 546,858 C564,862 574,850 576,840" stroke={p.shade} strokeWidth={8} fill="none" strokeLinecap="round" />
        <ellipse cx={436} cy={868} rx={30} ry={16} fill="#d9604a" opacity={0.28} /><ellipse cx={644} cy={868} rx={30} ry={16} fill="#d9604a" opacity={0.28} />
        <g transform="translate(540 905)"><MouthShape m={mouth !== "X" ? mouth : f.mouth ?? mouth} /></g>
      </g>
      {a.hands.map(([x, y]) => <Hand key={`${x},${y}`} x={x} y={y} p={p} />)}
      {clipboard && (
        <g transform={`translate(${cx - 10} ${cy - 90}) rotate(-10)`}>
          <rect x={-62} y={-92} width={124} height={174} rx={10} fill="#8a6238" />
          <rect x={-52} y={-72} width={104} height={144} fill="#fbf7f2" />
          <rect x={-26} y={-104} width={52} height={28} rx={6} fill="#c0c6d0" />
          {[-44, -20, 4, 28].map((y) => <rect key={y} x={-40} y={y} width={80 - (y + 44) / 2} height={7} fill="#9aa7b4" />)}
          <rect x={6} y={30} width={40} height={34} fill={p.accent} transform="rotate(6 26 47)" />
        </g>
      )}
      {pose === "celebrating" && [[180, 640], [900, 640]].map(([x, y]) => (
        <g key={x} stroke={p.accent} strokeWidth={10} strokeLinecap="round">
          <path d={`M${x},${y} l${x < 540 ? -30 : 30},-40 M${x},${y + 60} l${x < 540 ? -44 : 44},0 M${x},${y + 120} l${x < 540 ? -30 : 30},40`} />
        </g>
      ))}
    </g>
  );
};

const SETS: Record<Cast, React.FC<{ p: Palette }>> = { patch: PatchSet, auntie: AuntieSet, coach: CoachSet };
const BODIES = { patch: Patch, auntie: Auntie, coach: Coach };

export const Character: React.FC<{ who: Cast; pose?: Pose; mouth?: Mouth; blink?: boolean; background?: boolean; crop?: string; nod?: number }> = ({
  who, pose = "talk", mouth = "X", blink = false, background = true, crop = "0 0 1080 1920", nod = 0,
}) => {
  const p = PALETTES[who];
  const f = FACES[pose];
  const eyes: Eyes = blink && f.eyes !== "happy" ? "closed" : f.eyes;
  const Set = SETS[who];
  const Body = BODIES[who];
  return (
    <svg viewBox={crop} width="100%" height="100%">
      {background && <Set p={p} />}
      <Body pose={pose} mouth={mouth} eyes={eyes} nod={nod} p={p} />
    </svg>
  );
};

// The host (D22, 2026-11-06). Everything that used to draw the reporter draws the host.
export const HOST: Cast = "patch";
export const HostSet: React.FC = () => { const Set = SETS[HOST]; return <Set p={PALETTES[HOST]} />; };
export const Host: React.FC<Omit<React.ComponentProps<typeof Character>, "who">> = (p) => <Character who={HOST} {...p} />;

export { COLORS };
