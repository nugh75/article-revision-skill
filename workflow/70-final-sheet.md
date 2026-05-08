# 70 — Final sheet

Generates `revisioni/<slug>/scheda-revisione-vN.md` summarizing the round's outcome.

## 1. Source material

Read:

- the project file (`progetto-revisione-vN.md`) to extract decisions per point;
- `git log` filtered to commits matching `revision(<slug>):` since the start of the round;
- `audit-bibliografia-vN.md` if any bib check happened;
- the current char/word count.

## 2. Fill the template

Use `templates/scheda-revisione.md` and substitute placeholders. The summary table at the top should report, per point:

| Stato | Significato |
|---|---|
| ✅ Accettato | proposta applicata |
| 🔄 Modificato | proposta riformulata e poi applicata |
| ❌ Scartato | nessuna modifica al testo |
| ⏸️ Rimandato | richiede dato esterno o decisione successiva |

## 3. Recovery suggestions

If the article is over the editorial limit, populate the *"Recuperi pendenti"* section with concrete suggestions (e.g. duplicate prose, redundant section openings). Run:

```
scripts/char_count.py <article> --limit-from-env
```

and propose 3–5 candidate cuts with estimated savings.

## 4. Outstanding tasks

In the *"Punti residui prima del submit"* checklist, list:

- entries `Rimandato` from the project file;
- bibliography entries still flagged (from the audit);
- char overshoot to recover;
- anonymisation pass (if `-anonima` suffix is present and there are remaining `XXX` placeholders the user wants resolved before submission);
- any external check the user mentioned (e.g. *"GPT-5 model name to verify"*).

## 5. Cronologia

Pull from `git log`:

```
git log --oneline --grep "revision(<slug>):" --since "<date round started>"
```

Format as bulleted list under the *"Cronologia interventi"* heading.

## 6. Suggested commit

The skill writes the scheda but **does not commit**. Suggested commit message for the user:

```
revision(<slug>): scheda finale — round closed
```

## 7. Hand off

Final chat message:

```
✅ Scheda finale: revisioni/<slug>/scheda-revisione-vN.md

Round chiuso. Sintesi:
- <X> punti accettati, <Y> modificati, <Z> scartati, <W> rimandati
- conteggio: <M> {chars|words} (<over|under> di <N>)
- bibliografia: <stato>
- task residui: <lista breve>
```

The skill ends here. The next round will start a new project file with version vN+1 (or the same N+1 if the user prefers continuing).
