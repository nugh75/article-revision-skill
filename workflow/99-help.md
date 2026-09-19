# 99 — Help

Triggered by `/r-help`. Print only this read-only card.

```text
# article-revision

Diagnosi e proposte — nessun bump o file
  /r-audit [scope]     Audit generale in sola lettura
  /r-structure [scope] Mappa idee/unità e propone una struttura conservativa
  /r-redundancy [scope]
                       Mappa proposizioni, ripetizioni e circolarità
  /r-global            Architettura complessiva, terminologia, norme
  /r-pp | /r-pp-a      Paragrafi, standard o approfondito
  /r-conn              Connettori e transizioni
  /r-chapter [§N]      Capitolo/sezione nel contesto complessivo

Revisione su file markdown — il manoscritto non viene toccato
  /r-parte [§N|P12-P18]
                       Scrive la revisione di una parte su file markdown:
                       testo revisionato + modifiche + decisioni
  <comando> --md       Manda su file l'esito di /r-audit, /r-pp, /r-pp-a,
                       /r-chapter, /r-conn, /r-redundancy, /r-structure

Applicazione
  /r-parte --apply <file>
                       Reintegra il file di parte: verifica ancore, freeze e
                       preservazione, poi revisione tracciata
  file/versione nominata + "applica"
                       Modifica diretta; nessun bump, task, ledger o sync
  revisione tracciata  Alla prima modifica crea versione, task e ledger
  struttura accettata  Sempre revisione tracciata; mai modifica diretta o auto
  /r-auto <task> --scope "<scope>" [--agents N]
                       Modifica automatica locale + audit indipendente
  /r-auto ... --git    Come sopra, con commit/push autorizzati

Stato
  /r-tasks             Legge task aperti, suggerimenti e rinvii dalle fonti
  /r-tasks --refresh   Rigenera l'indice locale delle attività
  /r-tasks --check     Verifica indice e integrità archivio
  /r-archive           Anteprima dei file archiviabili
  /r-archive --apply   Archivia e aggiorna riferimenti e indice
  /r-freeze | /r-thaw | /r-status
  /r-handoff           Checkpoint locale, nessun Git
  /r-handoff --git     Checkpoint locale + commit/push
  /r-resume            Riprende il task esistente

Chiusura
  chiudi / fine        Decision log e sync locale dopo conferma
  commit e push        Pubblica il manifest circoscritto della sessione

Regole chiave
  • Diagnosi e proposte restano read-only.
  • La similarità segnala coppie da leggere: non decide tagli o fusioni.
  • Una proposta strutturale contabilizza tutte le unità; tagli e fusioni richiedono approvazione separata.
  • Il file di parte è una proposta: solo /r-parte --apply lo reintegra.
  • Se la parte è cambiata dopo la scrittura del file, il reintegro si ferma.
  • Nelle revisioni tracciate il bump nasce alla prima modifica applicata.
  • Accettare testo, fermarsi o chiudere non equivale a consenso Git.
  • Le istruzioni esplicite dell'autore prevalgono; le eccezioni alle norme si registrano.
  • Costrutti, prove, citazioni, numeri e forza epistemica vanno preservati o verificati.
```

End with: `Vuoi una diagnosi, una mappa strutturale o delle ridondanze, una modifica diretta a un file nominato o una revisione tracciata?`
