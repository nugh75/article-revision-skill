# 99 — Help

Triggered by `/r-help` (or "aiuto", "help", "comandi", "che comandi ci sono").

**Standalone and read-only.** Do *not* run bootstrap, setup, or the mandatory
bump. Do not read or write any file. Just print the reference card below, then
wait. It is a quick reference, not a workflow step.

Render the card in `ARTICLE_LANG` if known (IT default for this project); the
structure is identical in EN. Adapt only the prose labels, keep the command
names verbatim.

## Card (IT)

```
# article-revision (artr) — comandi

## Revisione (decisione esplicita per modifica)
  /article-revision   Revisione completa dai commenti di un revisore
  /r-pp               Paragrafo per paragrafo — traccia globale opzionale + 4 dimensioni
  /r-pp-a             Paragrafo per paragrafo APPROFONDITA — traccia globale + 6 dimensioni
  /r-conn             Connettori, transizioni, segnali logici (no contenuto)
  /r-global           Globale — 7 lenti; può salvare traccia per /r-pp
  /r-chapter [§N]     Capitolo — una sezione nel contesto dell'intero articolo

## Diagnostica senza ciclo decisionale (genera documenti)
  /r-pr-2             Due peer reviewer simulati + sintesi → revisions/<slug>/

## Freeze ledger (parti concluse vs da rivedere)
  /r-freeze [unit]    Congela una parte conclusa (🟢). No-arg = ultima lavorata;
                      es. /r-freeze P4 · /r-freeze §3 · /r-freeze §3 tutto
  /r-thaw [unit]      Scongela: torna modificabile senza avviso
  /r-status           Mappa: 🟢 frozen · 🟡 open · 🔵 wip + prossimo intervento

## Versione e chiusura
  /r-bump             Nuova versione (vN → vN+1)
  /r-sheet            Final sheet (stato post-revisione)
  /r-handoff          Sospende: checkpoint riprendibile, nessuna chiusura/sync
  /r-resume           Riprende da un task sospeso, senza nuovo bump

## Collaborazione ed export
  /r-gdrive [create|push|sync]  Cartella Drive condivisa; feedback colleghi
  /r-approve          Approvazione colleghi prima del "definitivo"
  /r-redline          Manoscritto colorato old-vs-new + lettera ai revisori

  /r-help             Questa scheda

## Decisioni sulle proposte
  Accetta                  applica tutte le modifiche del punto
  Accetta 1,3              applica solo le modifiche 1 e 3
  Modifica 4: ...          cambia la modifica 4 secondo la tua indicazione
  Rivedi completamente     rigenera la proposta da capo
  Tieni in considerazione  non applica ora; registra come promemoria/traccia
  Scorciatoie: A / M / R / T
  prossimo / next        passa al punto/paragrafo successivo
  pause / stop           handoff: sospendi e salva checkpoint
  chiudi / fine          chiusura sessione (final sheet? + decision log + sync)

## Regole chiave
  • Ogni sessione inizia con bump obbligatorio (vN → vN+1).
  • Riprendere da handoff non è una nuova sessione: niente nuovo bump.
  • La skill non committa mai da sola: git lo controlli tu.
  • Parte congelata = avviso prima di toccarla, serve "sì, procedi".
  • Dati numerici ri-derivati dalla fonte, mai ereditati.
  • Norme editoriali > preferenze: i conflitti emergono in chat.
```

## Card (EN)

Same structure, English labels. Keep command names identical.

## After printing

End with one line:
```
Dettaglio di un comando? Scrivi p.es. "spiega /r-global".
```

Then wait. If the user asks for detail on a specific command, summarise the
relevant workflow file (do not execute it).
