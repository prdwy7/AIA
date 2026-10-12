# agri_vocab — lexicon / ASR evaluation utterances (docs/05 §5)

≥ **500 utterances** of Telugu + Latin (script/mixed/transliterated) covering the
full agricultural lexicon for the KVK Banavasi / Kurnool domain. Used to evaluate
the ASR chain (primary `whisper-large-v3-vaani-telugu`, fast fallback
`SraVaani-1.0`) and the entity normalizer (brand → active ingredient).

## Coverage (≥ 100 each, target 500+)

| Class | Examples |
|---|---|
| Crop names | పత్తి (cotton), వరి (paddy), వేరుశనగ (groundnut), మొక్కజొన్న (maize), కందులు (arhar), ఆముదం (castor), చిరుధాన్యాలు (millets), మిరప (chilli) |
| Stages | విత్తనం (seed), నాటు (transplant), పుష్పించే (flowering), పంట (harvest) |
| Diseases / pests | bollworm, leaf blight, ఆకు మచ్చ (leaf spot), మిల్డ్యూ (mildew) |
| Local brand names | → active-ingredient mapping (confirmation gate) |
| Units / measures | per acre (ఎకరాకి), ml, gm, spray schedule |
| Weather / locations | Kurnool, Banavasi, rainfall, humidity |
| Greetings / consent | consent phrases (DPDP) |

## Format (one TSV / JSONL line per utterance)

```jsonl
{"id":"AV-001","text_te":"పత్తిలో ఆకులు పసుపు రంగులోకి మారుతున్నాయి","text_en":"cotton leaves turning yellow","mode":"te","expected_entities":["cotton","yellowing"]}
```

## Acceptance

- ≥ 500 total utterances; ≥ 100 per major class above.
- Every crop has ≥ 20 utterances spanning stages × symptoms.
- Local brand names each have an active-ingredient mapping (never guessed).
- WER/correction metrics (docs/05 §5) reported against this set per release.
