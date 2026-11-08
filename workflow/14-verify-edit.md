# Verify an article edit

Use this gate for every article write. Keep the snapshots in temporary files
outside tracked revision records. For preflight only, complete steps 1–3.

1. Read the live source and its applicable freeze ledger. Preserve the exact
   source bytes as `BEFORE` and record the ledger contents. Check advisory
   freezes in scope and keep 🔒 text intact. Resolve a pre-existing ambiguous
   anchor in the affected scope before editing that scope.
2. Build `CANDIDATE` from `BEFORE` using only approved replacements or eligible
   automatic changes. Check the scope and preservation rules in `SKILL.md`.
3. When a ledger applies, compare the candidate with the baseline. Exit 0
   permits the edit. Report pre-existing issues separately. Exit 1 blocks it.

   ```bash
   "$PYTHON_BIN" "<skill-root>/scripts/freeze_check.py" "$CANDIDATE" \
     --before "$BEFORE" --ledger "$LEDGER"
   ```

4. Immediately before writing, compare the live file and ledger with the
   baselines. Resolve the active version again for versioned projects. For
   `articles/versions/article-vN-…md` require exit 0 from
   `bash <skill-root>/scripts/sync_current.sh --check-source <ARTICLE_PATH>`.
   Rebuild the candidate if a baseline drifted. Apply only the verified edit.
5. Re-read the saved text and verify it matches the candidate. Repeat the
   ledger comparison on the saved text before recording application or
   approval. If another writer changed the file, report the conflict and
   preserve the live content for reconciliation.
