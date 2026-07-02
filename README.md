# Nested Hearth — Tatar Memory Palace

A memory-first Tatar study system. One JSON spine holds **vocabulary**, **media** (lectures, books, poems, images, authentic texts), and a **memory palace** of rooms. Every drill — listening and speaking — is generated from that spine, so adding a word or a lecture once makes it show up everywhere it belongs.

> The organizing idea, borrowed from Chulpan Khismatova's CLI lecture: *Tatar as a living archive of identity, resilience, and cultural memory.* The palace is that archive made walkable.

---

## Run it

No build step. Two ways:

1. **Double-click `index.html`** — it ships with the database embedded, so it works offline and on mobile.
2. **VSCode + Live Server** (recommended for development) — right-click `index.html` → *Open with Live Server*. Served over `http://`, the app re-reads the live `data/tatar_db.json`, so edits show up on refresh.

Listening (text-to-speech) and speaking (speech recognition) work best in **Chrome** (desktop or Android). Tatar voices are rare, so the app falls back to the **Russian** engine — a phonetic approximation, not perfect, but close enough to shadow and self-check.

---

## Layout

```
Tatar Memory Palace/
├── index.html            # the Palace Studio app (database embedded at the `const DB` line)
├── tatar_db.json         # THE SPINE — edit this, then re-embed it into index.html
├── tatar-nested-hearth/  # the Pygame desktop app — reads the SAME tatar_db.json
│   ├── main.py           #   (python main.py; needs pygame + edge-tts, kk-KZ neural voice)
│   └── core/             #   data_loader / grammar_rules / audio_engine
└── README.md
```

> **Keep them in sync:** the app reads only the embedded copy. After editing
> `tatar_db.json`, replace the single `const DB = …;` line in `index.html`
> with the compact JSON (Claude Code does this automatically when asked).

`data/tatar_db.json` is the single source of truth. The pygame Memory Wheel, the Sentence Cog, the PDF Field Kit, and this app can all read the same `vocab.verbs` / `vocab.nouns` records — the schema is unchanged from `memory_wheel.py`.

---

## The spine, in three layers

**1. `vocab`** — `verbs`, `nouns`, `expressions`.
Verbs and nouns use the existing app schema (`inf/stem/vstem/pres/cls/back/en`, and `s/en/back/cat`). Each verb now also carries `cond` and `fut` example forms. Loanwords carry an **explicit** `back` flag because the last vowel lies (табип → *back*: табипка, not табипкә). `expressions` holds the somatic emotion vocabulary, idioms, **doubt/epistemic words** (бәлки, ихтимал, -дыр), **spatial postpositions** (…янында, …эчендә), and direction lines — each tagged `kind`, `somatic` (heart / head / none) and `valence`, so the rooms build themselves. Nouns now cover **directions** (`cat: Direction`) and **body parts** (`cat: Body`), the latter wired to the Heart/Head emotion idioms.

### Conjugation Forge
The app ports the verb engine from `memory_wheel.py` (vowel sets, voiceless set `пфктшсчщхцһқ`, the `vbuild` logic) into JS and adds the **conditional**. The Forge renders any verb across **present · past · future · conditional × six persons**, with a negative toggle; tap any cell to hear it. The future definite is `vstem + -ачак/-әчәк` (vowel-stems `-ячак/-ячәк`) + endings — so өйрәнү → өйрәнәчәкмен, exactly your Week 5 form.

**2. `media`** — every lecture, book, poem, image, slide, or authentic text, with an `id`. The Khismatova lecture, *Tatar Empire* (Ross), *Becoming Muslim in Imperial Russia* (Kefeli), the Miñnullin poem, Kul Sharif at night, and the Ufa flyer are all in here.

**3. `palace.stations`** — the rooms. Each station names a `locus`, then **references** vocab (by surface form), expressions, and media (by id), and supplies a `listen` and a `speak` prompt. This is where everything converges: a station is just pointers into layers 1 and 2 plus two drills.

```
station → vocab[]  ─┐
        → expressions[] ─┼─→ rendered as tappable cards
        → media[]  ──────┘
        → listen{tt,en}  → TTS
        → speak{tt,en}   → mic + similarity score
```

---

## Working with Claude Code

Point Claude Code at `data/tatar_db.json` and treat it as the contract. Useful moves:

- **"Add this week's worksheet vocab"** → append to `vocab.*`, then add or extend a station that references it. The drills appear automatically.
- **"Bind my lecture recording"** → add a `media` entry (type `lecture`, with `url`), reference its `id` from the relevant station.
- **"Generate a listening quiz for the Heart Room"** → read `stations[id].expressions`, emit prompts. No new data needed.
- Keep entries **individually** schema-valid so the pygame tools keep working: `json.load(...)["vocab"]["verbs"]` must still yield the records `memory_wheel.py` expects.

---

## The Hearth layer (v0.8.0)

The 🔥 **Hearth** tab makes the nested frame walkable: five rings
(Учак → Бижбүләк → Өфө/Уфа → Башкортостан → Казан) drawn as nested boxes, then
three wings hanging off them:

- **Тормыш бүлмәләре — use-case rooms** (`zone: "Use cases"` stations): the Çäy
  Table, the Market, the Canteen, the Ufa Train — deployable phrase scripts with
  the same listen/speak drills as every other station.
- **Дәрес бүлмәләре — class rooms**: the course palace grouped by zone, one tap
  jumps into the Palace tab at that station.
- **Белем бүлмәләре — knowledge rooms** (`knowledge.decks`): History, Literature,
  Culture, and the Bashkir Wing — 24 facts, each with a Tatar anchor term and a
  Bashkir comparison where one exists, plus a generated multiple-choice **quiz**.

**Memory seals** (from the old `Tatar_Lab/palace_seals.json`) now live on the
stations themselves: the Kal-Fuk әби at Söyembikä Tower (кал), the Keel at Kul
Sharif (кил), the Bar patron on Bauman Street (бар), the Yard-Rat in the Heart
Room (ярат), the On-lah monk in the Lecture Hall (аңла) — statue, action, peg,
and spell sentence rendered as a dark plaque on each room.

**Шәһәрләр юлы — the Road of Cities** (v0.9.0): seven settlement cards on the
Hearth tab between the rings and the wings — Бижбүләк, Стәрлетамак, Казан,
Иннополис, Чистай, Бөгелмә, Нурлат. Each carries what the town is known for, a
peg image (a cauldron for Kazan, a river-swallowing throat for Стәрле-**тамак**,
Švejk saluting an oil derrick for Bugulma), one line of Tatar to say there with
its grammar note, and a Bashkir comparison where one applies. The same material
is quizzable as the **Шәһәрләр deck** in the knowledge wing.

**Case Forge** (Sentence Cog tab): any noun through all six cases with the full
allomorphy — voiceless finals take -ка/-кә, -та/-тә, -тан/-тән; nasal finals
take -нан/-нән; loanwords obey their explicit `back` flag.

**Voice fallback** now prefers Tatar → **Kazakh** → Bashkir → Russian: Kazakh
Cyrillic contains ә ң ө ү һ natively (the pygame `audio_engine.py` insight), so
if the browser has a kk voice (Edge on Windows does), pronunciation improves a lot.

---

## Roadmap (the next few days, and after)

- **Speaking, deeper.** Add a shadow mode (play model → record → A/B playback) and a per-station streak.
- **The Ufa palace.** The *Ufa Gate* station is the bridge. Build the Bashkir-heritage layer (Lälä Tülpan, Salavat Yulaev Arena, the monument over the Belaya) as its own `palace` block, with the Ufa flyer as authentic reading.
- **Izafet layer.** Show simple vs possessive forms side by side (туган көн → туган көнем), declining only the head noun at first.
- **Feed the Sentence Cog.** Have the Cog pull its noun list from whichever station is active, so grammar practice is anchored to the room you're standing in.
- **Bashkir contrast.** A parallel column leveraging how close Bashkir and Tatar are.
- ~~**Conditional conjugator.**~~ ✅ Done — the Forge generates present/past/future/conditional live. Next: wire `-дыр` presumptive and the modal `-ган булыр иде` (contrary-to-fact) as Forge rows.

---

*Bizhbulyak → Ufa → Bashkortostan is the outer frame; the Kazan class layer is the first walkable wing. Walk the same route each time, and the wheel turns on its own.*
