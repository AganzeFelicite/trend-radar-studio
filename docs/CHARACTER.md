# Character Bible v3: Patch (picked 2026-11-06, D22)

The code always reads the name from `CHARACTER_NAME`. Below, `{NAME}` stands for that value. GameReporter (v2) stays in
`renderer/src/Reporter.tsx` as the shared rig (mouth shapes, eyes, brows, poses); the other candidates (Auntie Ping,
Coach Dub) stay in `renderer/src/Cast.tsx` and `docs/CHARACTER-CANDIDATES.md`.

![character sheet](../assets/character/sheet.png)

The character is drawn in code: `Patch` in [`renderer/src/Cast.tsx`](../renderer/src/Cast.tsx) (`Host` = Patch) is the
single source of truth. No image model, so every video shows exactly the same character, at $0. Re-render the sheet and
test clip with `scripts/cast.sh patch`.

## 1. Name

**`CHARACTER_NAME = "Patch"`** (your pick from three candidates, 2026-11-06). One word, works as a handle.

## 2. Backstory

{NAME} is a small green gremlin who lives inside an update server. It cannot experience news; it can only experience
*patch notes*. Every event, however emotional, gets a version number, a severity rating and a "known issues" list,
delivered deadpan while the fans scream. {NAME} reads the Trend Radar every morning as a changelog of the internet.

## 3. Look (fixed in code)

- **Who:** an original cartoon gremlin in a flat vector style: green skin (`#6cc26b`), pointed ears, three hair
  strands, big goggles pushed up on the forehead whose lenses show scrolling green text, thick eyebrows (they carry
  the reactions).
- **Framing:** chest up behind a server desk, filling most of the frame. The face sits at (540, 503) and the top of the
  head at y=152 on the 1080×1920 canvas, the same as v2, so FilmCraft layouts (`face` / `head_top`) are unchanged.

## 4. Outfit

- **Hoodie:** charcoal (`#2e2e3c`), hood up behind the head, grey drawstrings, a round **download-arrow badge** in
  green on the chest. No brand logos anywhere.
- **Props:** a paper **TICKET** held up in the `thinking` pose; **one** piece of confetti in the `celebrating` pose
  (the whole celebration).

## 5. Set (the same every time)

- **Background:** a dark server room: a rack either side with blinking green and red LEDs.
- **Sign:** a faint glowing download arrow above the head. In videos the day's **data card** is shown full frame
  (V7.5), styled like a changelog entry.
- **Desk:** a dark server desk with a green top edge.
- **Palette:** base `#05100c`, racks `#171a22`, hoodie `#2e2e3c`, green `#7cff6b`, highlight yellow `#ffd400` (the
  same yellow as the caption highlights).

## 6. Poses and lip-sync

- **Poses:** `talk` (hands on the desk), `shocked` (hands up, wide eyes, "O" mouth), `laughing` (eyes shut, big grin,
  head tilt), `thinking` (ticket raised, one eyebrow up), `celebrating` (both fists up, one confetto).
- **Mouth shapes:** the nine shapes `X A B C D E F G H` (Rhubarb Lip Sync's set) driven by Kokoro's phoneme timings in
  `api/studio/voice.py`. Blinks on an irregular timer; a slight nod while speaking. Test clip:
  `assets/character/talk-test.mp4`.

## 7. Personality

- **Deadpan vs. hype:** fans scream, {NAME} files a ticket. The joke is the format, so it works on every topic,
  including boring ones.
- **Running gags:** version numbers ("Patch 1.0.7"), severity ratings ("Severity: I can't breathe"), "known issues",
  "hotfix: none", "rolling back my feelings".
- **Patch-notes talk:** changelog, severity, hotfix, rollback, deprecated, known issues, stable build, nightly. No
  toxic slang, no insults.
- **Honest in the changelog:** says "status: not confirmed" when that is the truth. The validator removes
  "leaked / insider / breaking" anyway.

## 8. Catchphrases

- **Opener (your pick):** "Patch notes incoming.", played right after the hook line.
- **Sign-off (your pick):** **"Known issues: none. Patch out."**
- **Per moment:** a story "Changelog:" · a win "Stable build." · caution "Status: not confirmed. Monitoring." ·
  the data line "Radar changelog: …"

## 9. Do / Don't

| Do | Don't |
|---|---|
| Use Trend Radar verified facts word for word | Change, round or "improve" a verified fact |
| Cite every extra claim (stored as `unverified-context`) | Repeat rumours, "leaks" or insider claims |
| Say "status: not confirmed" when unsure | Say CANCELLED / LEAKED / CONFIRMED without a cited source |
| Follow the arc: hook → the story → reaction → why now (data) → what's next | Create fake urgency, or use "BREAKING" banners |
| Be on screen at the start and the end | Show third-party footage beyond D20 (stock, AI images, official Rockstar media with credit) |
| Say "I'm an AI gremlin. The data's real." if asked | Pretend to be a real person |
| Keep it clean and kind | Swear, mock people, or touch finance / investing / money-making / health / medical / legal |

## 10. Voice (free): **`patch`**

- **Engine:** local **Kokoro** TTS (open source, Apache-2.0), $0.
- **The voice:** an **original mix** of Kokoro preset voices (`am_adam` 70% + `af_sky` 30%, speed 1.2). Not cloned;
  imitates no real person.
- **Delivery:** fast, dry, slightly nasal; about 175–190 words per minute.
- **Timing:** word timings from Kokoro and local Whisper drive the captions and the lip-sync.
