# Character candidates (D22): pick one

Three hosts for the story videos. All three are drawn in code (SVG, like GameReporter), voiced with a free Kokoro mix,
clearly cartoon and clearly AI, and none of them is a Rockstar character or look-alike. Each comes with hooks written for
today's three topics (Nov 6: Launch Screenshots, Take-Two business, PS5 Pro) so you can hear the voice, not just read a
description. The numbers in the hooks are placeholders for verified facts.

**See and hear them:** `scripts/cast.sh` renders each one's sheet and a 10 s talking clip into `assets/cast/` and opens `assets/cast/compare.html`.

**Reply with A, B or C** (or "A but …"). Then V7.1 finishes that one: bible, poses and voice tuned to your notes.

---

## A. Patch — the patch-notes gremlin

**Who:** A small, over-caffeinated green gremlin in an oversized hoodie who lives inside an update server. It cannot
experience news; it can only experience *patch notes*. Every event, however emotional, gets a version number, a
severity rating and a "known issues" list, delivered deadpan.

**Comedy engine:** Hype vs. deadpan. Fans scream; Patch files a ticket. The joke is the format, so it works on every
topic, including boring ones (earnings calls become "Patch 2.4: Take-Two said words. Severity: medium. Hotfix: none").

**Look:** Big round goggles (the lenses show tiny scrolling text), three strands of hair, hoodie with a download-arrow
badge, sits on a stack of servers with blinking lights. Poses: typing, "ticket raised" (holds up a paper), facepalm,
tiny celebration (confetti is just one piece of confetti), squint.

**Voice:** Fast, dry, slightly nasal. Kokoro mix leaning `am_adam` + a touch of `af_sky`, speed 1.2.

**Opener / sign-off:** "Patch notes incoming." / "Known issues: none. Patch out."

**Sample hooks:**
- *Screenshots:* "Patch 1.0.7: Rockstar dropped {N} new screenshots. Severity: I can't breathe."
- *Take-Two:* "New patch for your feelings: Take-Two just talked money. Reading the changelog."
- *PS5 Pro:* "Known issue: your PS5 Pro and your wallet are fighting. Here's the ticket."

---

## B. Auntie Ping — the group-chat auntie

**Who:** A warm, nosy middle-aged auntie in a bright headwrap and reading glasses who runs the neighbourhood WhatsApp
group and has decided GTA 6 is family business. She reports gaming news exactly the way she reports who got engaged:
leaning in, hand on chest, "did you hear".

**Comedy engine:** Gossip framing. Corporate news becomes neighbourhood drama ("Take-Two, that family with the big
house, they had their money meeting"). She mothers the audience ("have you pre-loaded? have you eaten?"). Warmth makes
her very shareable; nobody else in GTA content sounds like this.

**Look:** Round face, big glasses on a chain, headwrap, cardigan, a phone always in hand with a notification badge
that keeps going up. Set: a kitchen table with a radio. Poses: lean-in whisper, hand on chest (shocked), "mm-hmm" nod,
phone held up to the camera, laughing with hand on the table.

**Voice:** Warm, unhurried, musical. Kokoro mix `af_bella` + `af_sarah`, speed 1.0.

**Opener / sign-off:** "Come, come, sit. You won't believe this." / "Okay, go and play. And drink water. Auntie out."

**Sample hooks:**
- *Screenshots:* "Sit down. Rockstar posted {N} new pictures and I have not slept."
- *Take-Two:* "You know Take-Two, the family with the big house? They had their money meeting."
- *PS5 Pro:* "Your cousin bought a PS5 Pro for this game. I have questions."

---

## C. Coach Dub — the launch-day coach

**Who:** A sweatband-wearing, whistle-blowing motivational coach who treats every GTA fan as a player on his team
preparing for one event: launch day. News items are "scouting reports"; pre-loading is "training"; a delay would be
"an injury". He is loud, he is sincere, and he believes in you specifically.

**Comedy engine:** Misplaced intensity. Sports-movie energy applied to downloading a game. Counts down the days every
video ("Thirteen days out, people!"), does locker-room speeches about storage space. Easy running gags: the clipboard,
the whistle, the one player who hasn't pre-loaded.

**Look:** Stocky, sweatband, polo with a tiny trophy logo, whistle, clipboard. Set: a locker-room bench with a
whiteboard behind him (the whiteboard shows the day's data card). Poses: whistle blow, clipboard point, "huddle up"
arms wide, fist pump, hands on knees (exhausted).

**Voice:** Big, gravelly, energetic. Kokoro mix `am_michael` + `am_onyx`, speed 1.1.

**Opener / sign-off:** "Huddle up! {days} days out." / "Hydrate. Pre-load. Coach out."

**Sample hooks:**
- *Screenshots:* "Scouting report! Rockstar leaked nothing, they POSTED {N} screenshots. Different thing. Huddle up."
  (note: "leaked" is on the never-list; the validator would make this "Rockstar posted {N} screenshots. Official. Huddle up.")
- *Take-Two:* "Front office spoke. Take-Two had their money meeting. Here's what it means for the team."
- *PS5 Pro:* "Equipment check! PS5 Pro versus PS5 for launch day. Clipboard says…"

---

## How they compare

| | A. Patch | B. Auntie Ping | C. Coach Dub |
|---|---|---|---|
| Comedy | deadpan, format jokes | warm gossip, mothering | loud, sports-movie hype |
| Works on boring topics | **best** (everything is a patch note) | good (everything is drama) | okay (needs an "event") |
| Different from other GTA channels | high | **highest** | medium (hype hosts exist) |
| Running gags | tickets, severity, known issues | the phone badge, "have you eaten" | countdown, whistle, the one who didn't pre-load |
| Risk | can feel cold; needs reaction poses | pacing must stay quick for Shorts | tips into sensational wording; validator catches it |
| Drawing effort | low | medium (expressive face) | low |

My recommendation: **B. Auntie Ping** for reach (nobody sounds like her, and warmth travels on Shorts), **A. Patch** if
you want the safest fit with data cards and deadpan one-liners. Both keep every video obviously cartoon and AI.
