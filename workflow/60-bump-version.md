# 60 — Bump version

Triggered:

- when the user signals end of revision round (*"chiudiamo questa versione"*);
- when the *accepted-since-last-bump* counter in the project file reaches `AUTO_BUMP_THRESHOLD` (default 5) — the skill **proposes** the bump in chat, the user confirms;
- when the user explicitly asks (*"crea v(N+1) ora"*).

Never bump without explicit confirmation.

## 1. Pre-flight checks

Before bumping:

- Show in chat the count of accepted changes since the last bump and a short list of which points they affected.
- Report current char/word count and budget status.
- Ask the user to confirm the bump:

  ```
  Pronto a creare una nuova versione:
  - <K> modifiche accettate dall'ultimo bump
  - punti: <list>
  - conteggio: <M> chars (<over|under> di <N>)

  Procedo? (sì / no / mostra di nuovo i punti)
  ```

- If there are points still `Da decidere`, mention them: *"Ci sono <X> punti ancora aperti. Vuoi forzare il bump (i punti restano nel progetto) o chiuderli prima?"*.

## 2. Run the bump script

```
NEW_PATH=$(scripts/new_version.sh <current-article-path>)
```

The script:

- copies the current file with incremented `vN+1` and the current timestamp `YYYY-MM-DD-HHMM`;
- preserves the `-anonima` suffix if present;
- prints the new path on stdout.

Resulting filename pattern: `articolo-v(N+1)-YYYY-MM-DD-HHMM[-anonima].md`. Multiple bumps in the same day get distinct files because the time differs.

## 3. Generate the diff summary

```
scripts/diff_versions.sh --auto $NEW_PATH > revisioni/<slug>/diff-vN-to-v(N+1).md
```

The diff lists what changed between the previous file and the new one. Useful for the *Cronologia interventi* section of the next scheda.

## 4. Reset the counter

In the project file, reset `<!-- accepted_since_bump: 0 -->` and add an entry to a *History* section at the bottom:

```markdown
## Cronologia bump

- vN → v(N+1) — YYYY-MM-DD HH:MM — <K> modifiche accettate
```

## 5. Notify the user

```
✅ Versione v(N+1) creata: <NEW_PATH>
   timestamp: <YYYY-MM-DD HH:MM>
   diff: <X> righe modificate · chars <signed> · words <signed>

Counter azzerato. Modifiche pendenti (non committate): N file.

Suggerimento commit message (se vuoi committare):
  bump: vN → v(N+1) (<K> punti accettati)

Pronto per:
- continuare la revisione su v(N+1)?
- generare la scheda finale (`70-final-sheet.md`)?
- chiudere la sessione?
```

The skill **does not commit**. The suggested message is provided in chat for the user to copy if they wish.

## 6. Edge case — destination already exists

If by any chance `articolo-v(N+1)-YYYY-MM-DD-HHMM[-anonima].md` exists (extremely unlikely with minute-level resolution), the script aborts. Ask:

> Esiste già un file con lo stesso timestamp. Aspetto un minuto e riprovo? (sì / annulla)
