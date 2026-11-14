# Story journal

The **Story** tab is your campaign journal: what happened, why you are doing what, who you met.

- **+ New block** starts a block with a heading (e.g. a day or a city). `# Heading` starts a block, `## Sub-heading` a smaller one.
- Inside a block: empty lines separate paragraphs, `- ` starts a list, `**bold**`, `*italic*`.
- Blocks can be collapsed, and the search box filters them.
- The one-line field at the top adds a line to the end of the journal without opening the editor.
- Every change keeps the previous text; the narrator can restore it (Django admin → Journal revisions).

## History

Below the journal, **History** lists the last 30 changes to the character: when, who (narrator, a player session, anyone) and what changed (old → new). It is read-only. The narrator can undo the last play action or reverse the last level-up there, as long as nothing has changed the same values since; changes to items, companions and texts are never undone automatically.
