# Claude Loop Checklist

## Before start

- Confirm target directory.
- Confirm whether to delete existing files.
- Confirm whether public URL should stay disabled.

## Prompt quality checklist

- Include concrete output path.
- Include required features list.
- Include completion marker (`DONE`).
- Include forbidden shortcuts (if any).

## Stall diagnosis

If terminal shows only spinner:

1. Check latest Claude debug log timestamp.
2. Confirm API stream started.
3. Poll again after 20-40s.
4. If no tool action appears, send a short nudge prompt.
5. If still stalled, interrupt and resend reduced prompt.

## Completion checklist

- Claude printed `DONE`.
- Target file exists.
- Quick grep confirms required features.
- Session exited cleanly.
