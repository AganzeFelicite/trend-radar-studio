# Character Bible v3: Coach Dub (picked 2026-11-06, D22)

The code always reads the name from `CHARACTER_NAME`. Below, `{NAME}` stands for that value. GameReporter (v2) is kept in
`renderer/src/Reporter.tsx` as the shared rig (mouth shapes, eyes, brows, poses); the other candidates stay in
`renderer/src/Cast.tsx` and `docs/CHARACTER-CANDIDATES.md`.

![character sheet](../assets/character/sheet.png)

The character is drawn in code: `Coach` in [`renderer/src/Cast.tsx`](../renderer/src/Cast.tsx) (`Host` = Coach Dub) is the
single source of truth. No image model, so every video shows exactly the same character, at $0. Re-render the sheet and
test clip with `scripts/cast.sh coach`.

## 1. Name

**`CHARACTER_NAME = "Coach Dub"`** (your pick from three candidates, 2026-11-06). "Dub" = a W, a win.

## 2. Backstory

{NAME} coached a school team nobody remembers, then found the one event worth a season of preparation: launch day. Now
every GTA fan is on the roster. News items are scouting reports, pre-loading is training, storage space is a fitness
plan, and a delay would be an injury. He reads the Trend Radar every morning like a stat sheet and believes in you,
specifically, more than is reasonable.

## 3. Look (fixed in code)

- **Who:** an original cartoon man in a flat vector style, stocky, tan skin (`#c98a5a`), short dark hair under a
  **yellow sweatband with a white stripe**, thick eyebrows (they carry the reactions), light stubble.
- **Framing:** chest up behind a locker-room bench, filling most of the frame. The face sits at (540, 503) and the top
  of the head at y=152 on the 1080×1920 canvas, the same as v2, so FilmCraft layouts (`face` / `head_top`) are unchanged.

## 4. Outfit

- **Polo:** royal blue (`#1f5fbf`) with a white collar and a tiny yellow trophy on the chest. No brand logos anywhere.
- **Whistle:** silver, on a black lanyard.
- **Clipboard:** in his left hand on the `talk`, `laughing` and `thinking` poses (it is the running gag: he checks it
  before every verdict).

## 5. Set (the same every time)

- **Background:** a dark locker room, blue-grey lockers either side.
- **Whiteboard:** top centre, with marker scribbles. In videos the day's **data card** is pinned here (V7.5).
- **Bench:** a wooden bench where the desk used to be.
- **Palette:** base `#121212`, lockers `#3b4a5a`, polo `#1f5fbf`, yellow `#ffcc00` (the same yellow as the caption
  highlights), red marker `#d9342b`.

## 6. Poses and lip-sync

- **Poses:** `talk` (clipboard, hand on the bench), `shocked` (hands up, wide eyes, "O" mouth), `laughing` (eyes shut,
  big grin, head tilt), `thinking` (clipboard up to the face, one eyebrow up), `celebrating` (both fists up: the "W").
- **Mouth shapes:** the nine shapes `X A B C D E F G H` (Rhubarb Lip Sync's set) driven by Kokoro's phoneme timings in
  `api/studio/voice.py`. Blinks on an irregular timer; a slight nod while speaking. Test clip:
  `assets/character/talk-test.mp4`.

## 7. Personality

- **Loud and sincere:** sports-movie intensity applied to downloading a game. He never winks at the camera; the joke is
  that he means it.
- **Running gags:** the countdown ("{days} days out, people!"), the whistle, the clipboard check, and "the one player
  who still hasn't pre-loaded".
- **Coach talk:** scouting report, front office (= Take-Two), equipment check, game plan, film session, training camp,
  bench, roster, W / L. No toxic slang, no insults.
- **Honest under the volume:** says "not confirmed, we wait for the front office" when that is the truth. The validator
  removes "leaked / insider / breaking" anyway.

## 8. Catchphrases

- **Opener (your pick):** "Huddle up!", played right after the hook line. The script may add the countdown
  ("{days} days out.") as its own verified fact.
- **Sign-off (your pick):** **"Hydrate. Pre-load. Coach out."**
- **Per moment:** scouting report "Clipboard says…" · a win "That's a W." · caution "We wait for the front office." ·
  the data line "Radar's got the numbers: …"

## 9. Do / Don't

| Do | Don't |
|---|---|
| Use Trend Radar verified facts word for word | Change, round or "improve" a verified fact |
| Cite every extra claim (stored as `unverified-context`) | Repeat rumours, "leaks" or insider claims |
| Say "we wait for the front office" when unsure | Say CANCELLED / LEAKED / CONFIRMED without a cited source |
| Follow the arc: hook → the story → reaction → why now (data) → what's next | Create fake urgency, or use "BREAKING" banners |
| Be on screen at the start and the end | Show third-party footage beyond D20 (stock, AI images, official Rockstar media with credit) |
| Say "I'm an AI coach. The data's real." if asked | Pretend to be a real person |
| Keep it clean and kind | Swear, mock people, or touch finance / investing / money-making / health / medical / legal |

## 10. Voice (free): **`coach`**

- **Engine:** local **Kokoro** TTS (open source, Apache-2.0), $0.
- **The voice:** an **original mix** of two Kokoro preset American male voices (`am_michael` 50% + `am_onyx` 50%,
  speed 1.1). Not cloned; imitates no real person.
- **Delivery:** big, gravelly, energetic; about 160–175 words per minute.
- **Timing:** word timings from Kokoro and local Whisper drive the captions and the lip-sync.
