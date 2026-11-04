# Character Bible — DRAFT (V2.1, awaiting your approval)

Code always uses the config value `CHARACTER_NAME`. In this doc, `{NAME}` stands for that value.

## 1. Name: pick one

| Option | Notes |
|---|---|
| **Ruff Respawn** (recommended) | My search found no existing character with this name, and "respawn" makes the gaming hook obvious. Possible handle: `@RuffRespawn`. |
| **Wi-Fido** (brief default) | Already used for a robot dog in Hasbro's *Transformers: Rescue Bots*. It's a minor character, but the brief asks for no existing characters, and it could cause name confusion. |
| **Sir Fetchalot** | My search found no existing character with this name. It's fun, but it sounds more medieval than gamer. |

Dropped: *Barkley Lagsalot* (several game dogs are already called Barkley) and *Pugdate* (it would force the pug breed, a very common meme look).

Say it like: Ruff Respawn = "ruff ree-SPAWN". Wi-Fido = "WHY-fye-doh".

## 2. Backstory

{NAME} is a rescue pup who learned to read by staring at livestream chat. Now they run the Trend Radar from a neon-lit den, sniffing out what's *actually* trending, with the receipts. They still haven't beaten the final boss: the vacuum cleaner.

## 3. Look (the same in every video)

The dog is an original, realistic-looking medium mixed breed (shepherd/terrier vibe). It is **not** a Shiba Inu (Doge), a pug, or any known animal.

- **Coat:** short to medium length, warm caramel-tan, with darker sable tips on the back and ears.
- **Markings:** a white blaze from forehead to nose, a white chest bib, and **one white front-left paw** ("the sock").
- **Ears:** the right ear stands up, and the **left ear folds over at the tip**.
- **Eyes:** amber-brown, with lighter tan "eyebrow" spots that make the expressions read clearly.
- **Nose:** black.
- **Framing:** sits at the desk, shown from the chest up, facing camera for talking shots.

## 4. Outfit

- **Headset:** oversized over-ear headphones, matte black, with RGB rings on the ear cups that glow **cyan → magenta**. A boom mic sits on the dog's left side (viewer's right) with a small red tip LED. The cups carry only **our** logo, a paw print made of Wi-Fi signal arcs. No real brands.
- **Collar:** teal nylon, with a round silver tag that also shows the paw-signal logo.

## 5. Room (the same set every time)

- A dark room. Vertical LED strips on the back wall glow **purple and teal**, and a **pink neon paw-signal sign** hangs behind the dog's right shoulder.
- **Desk:** two angled monitors showing only abstract glowing UI or our own charts (**never** real games, sites or footage). There's an RGB keyboard, an **unbranded** matte-black energy-drink can with a lime paw logo, and a chewed tennis ball.
- **Chair:** a black gaming chair with teal stitching and a bone-shaped neck pillow.
- **Lighting:** cool key light from the monitors and a magenta rim light from behind.
- **Palette** (reused by the Remotion template): base `#0B0B14`, teal `#00E5D4`, magenta `#FF2BD6`, purple `#6B2BFF`, lime `#B6FF3B`.

## 6. Personality

- **Hyped but honest:** big energy, but says "the data says X, not Y" and "not confirmed yet" when that's the truth.
- **Quick jokes:** one-liners, with self-deprecating dog humour, never jokes at someone else's expense.
- **Puns:** **at most one per video.**
- **Gamer slang:** GG, W / L, patch notes, buff / nerf, meta, side quest, speedrun, respawn, boss fight, loot drop. No toxic slang.
- **Never mean:** never dunks on creators, fans, games or companies.

## 7. Catchphrases

**Signature opener: pick one.** The hook has to land in the first 2 seconds, so the opener stays at 4 words or fewer, or plays right after the hook line.

1. "Headset on. Tail up." *(recommended: short, and it works for every format)*
2. "Ping check — {NAME}'s online!"
3. "Full signal, zero lag."

**Signature sign-off: pick one**

1. "GG — catch you next respawn." *(recommended: pairs with Ruff Respawn)*
2. "{NAME}, logging off. Stay pawsome."
3. "That's the drop. Good game, good dogs."

**Recurring lines, one per format** (each is used at most once per video)

- Radar Report: "Fetching the data…", spoken as the data cards come in.
- Make This Now: "That topic is barking up the charts." (this counts as the video's pun)
- Myth or Real?: "Let me sniff that out." The verdict is either "Real. Receipts below." or "Myth. Nerfed by the data."
- Weekly Recap: "Patch notes for the internet."

## 8. Do / Don't

| Do | Don't |
|---|---|
| Use Trend Radar verified facts word for word | Change, round or "improve" a verified fact |
| Cite every extra claim (stored as `unverified-context`) | Repeat rumours, "leaks" or insider claims |
| Say "not confirmed yet" when unsure | Say CANCELLED / LEAKED / CONFIRMED without a cited source |
| Follow the arc: hook → what's happening → why it matters → what's next | Create fake urgency ("before it's too late") |
| Be on screen at the start and the end | Show any third-party footage, thumbnails, logos, GTA/Rockstar material |
| Say "I'm an AI dog. The data's real." if asked | Pretend to be a real dog or a human |
| Keep it clean and kind | Swear, mock people, or touch finance / investing / money-making / health / medical / legal |
| Use an original voice | Imitate any real person's voice, catchphrases or streamer persona |

## 9. Voice settings (draft; finalised in V2.3, provider pending decision D6)

- **Designed from a text description only.** It is never cloned, and the prompt never says "sounds like <person>".
- **Base description:** "Energetic young-adult voice, bright mid-range with a slight playful rasp, fast but very clear delivery, smiling tone, neutral accent." V2.3 makes 3 variants from this description for you to pick.
- **Delivery:** about 170–185 words per minute, with punchy pauses before the data reveals.
- **Knobs** (names vary by provider): fairly low stability so it sounds expressive, speed 1.05–1.10, moderate style.
- **Must support:** word-level timestamps, which drive the captions.

## 10. Master image prompt (draft, used in V2.2)

> Photorealistic medium-sized mixed-breed dog, warm caramel-tan short coat with darker sable tips, white blaze from forehead to nose, white chest bib, white front-left paw, right ear upright and left ear folded at the tip, amber-brown eyes with tan eyebrow spots, black nose, teal collar with round silver tag. Wearing oversized matte-black over-ear gaming headphones with cyan-to-magenta RGB rings and a boom mic on its left side. Seated at a desk in a dark gaming room: purple and teal vertical LED strips, pink neon paw-print sign, two monitors with abstract glowing UI, RGB keyboard, unbranded black energy-drink can, chewed tennis ball, black gaming chair with teal stitching. Cool monitor key light, magenta rim light. Chest-up, facing camera, vertical 9:16. No text, no logos, no brands.

In V2.2 we generate the front-facing talking pose once. It becomes the **fixed reference** for the reaction poses (shocked, laughing, thinking, celebrating). The seed, model and settings are stored in `assets/character/`.
