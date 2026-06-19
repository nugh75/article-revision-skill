# 98 — Recommended Revision Guide

Triggered by `/r-guide` (or "guida", "percorso consigliato", "recommended
workflow").

**Standalone and read-only.** Do not run bootstrap, setup, mandatory bump, or
file writes. Print the guide below, then wait. This command explains the
recommended path; it does not execute it.

Render in `ARTICLE_LANG` if known (IT default). Keep command names verbatim.

## Card (IT)

```text
# Percorso consigliato di revisione completa

1. TOV + setup
   - Carica tono di voce, norme editoriali, lingua articolo e vincoli.
   - Se disponibile, usa la skill `tone-of-voice` o le note `ARTICLE_STYLE_NOTES`.
   - Il TOV orienta ogni proposta: non è una riscrittura libera finale.

2. Prima analisi globale
   - Esegui `/r-global`.
   - Controlla tesi, architettura, proporzioni, ridondanze, terminologia e norme.
   - Salva una traccia globale per guidare la revisione paragrafo per paragrafo.

3. Revisione paragrafo per paragrafo
   - Esegui `/r-pp` o, se serve maggiore profondità, `/r-pp-a`.
   - Usa la traccia globale come orientamento.
   - Ogni paragrafo deve riportare: capitolo + numero paragrafo + righe Markdown.
   - Ogni proposta resta nel ciclo Accetta / Modifica / Rivedi completamente / Tieni in considerazione.

4. Handoff alla fine di ogni capitolo
   - Alla fine del capitolo: recap, eventuale freeze delle parti concluse, poi `/r-handoff`.
   - Ogni handoff scrive checkpoint, decision log, sync current files e commit scoped.
   - La sessione resta sospesa e riprendibile con `/r-resume`.

5. Chiusura della revisione
   - Quando tutti i capitoli sono processati, chiudi il round.
   - La chiusura finale esegue decision log + sync current files.

6. Controllo con due revisori simulati
   - Dopo la prima revisione completa, esegui `/r-pr-2`.
   - Il feedback è `simulated`: serve per QA interna, non per la risposta al journal.

7. Triage e mini-round finale
   - Leggi la sintesi dei due revisori.
   - Lavora prima sui punti critici e convergenti [A+B].
   - Riapri un ciclo mirato con `/article-revision`, `/r-pp-a`, `/r-global` o `/r-conn`.
   - Se non emergono problemi sostanziali, passa a `/r-redline` o `/r-sheet`.

Sequenza breve:
TOV + setup → /r-global → /r-pp-a con /r-handoff a fine capitolo → chiusura/sync → /r-pr-2 → triage → mini-round finale → /r-redline o /r-sheet
```

## Card (EN)

```text
# Recommended Full Revision Path

1. TOV + setup
   - Load tone of voice, editorial norms, article language, and constraints.
   - If available, use the `tone-of-voice` skill or `ARTICLE_STYLE_NOTES`.
   - TOV guides every proposal; it is not a final free rewrite.

2. First global analysis
   - Run `/r-global`.
   - Check thesis, architecture, proportions, redundancy, terminology, and norms.
   - Save a global trace to guide paragraph-by-paragraph revision.

3. Paragraph-by-paragraph revision
   - Run `/r-pp`, or `/r-pp-a` for deeper review.
   - Use the global trace as orientation.
   - Every paragraph must show chapter + paragraph number + Markdown line range.
   - Every proposal stays in the Accetta / Modifica / Rivedi completamente / Tieni in considerazione loop.

4. Handoff at the end of each chapter
   - At chapter end: recap, optionally freeze concluded units, then `/r-handoff`.
   - Every handoff writes checkpoint, decision log, current-file sync, and a scoped commit.
   - The session remains paused and resumable with `/r-resume`.

5. Close the revision
   - Once all chapters are processed, close the round.
   - Final closure runs decision log + current-file sync.

6. Simulated two-reviewer QA
   - After the first complete revision, run `/r-pr-2`.
   - Feedback is `simulated`: use it for internal QA, not as journal feedback.

7. Triage and final mini-round
   - Read the two-reviewer synthesis.
   - Prioritize critical and convergent [A+B] points.
   - Reopen a focused cycle with `/article-revision`, `/r-pp-a`, `/r-global`, or `/r-conn`.
   - If no substantial issues remain, proceed to `/r-redline` or `/r-sheet`.

Short sequence:
TOV + setup → /r-global → /r-pp-a with /r-handoff at chapter end → closure/sync → /r-pr-2 → triage → final mini-round → /r-redline or /r-sheet
```

## After printing

End with one line:

```text
Vuoi che ti spieghi uno dei passaggi o che inizi dal primo step operativo?
```

Then wait.
