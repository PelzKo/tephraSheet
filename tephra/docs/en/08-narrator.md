# For the narrator

The narrator is a Django staff user. Log in with **Narrator login** in the header (`/gm/login/`); afterwards **Narrator** in the header opens the narrator page (`/gm/`). The narrator can open every character without its password.

## Settings
- **Random traits:** whether players may pick their random racial trait instead of rolling, and whether they may re-roll it.
- **Background stories** per character and the **highest starting level** for new characters.
- **Admin mode for players:** whether players who unlocked a character may use admin mode on it. The narrator always may.
- **Extensions** and **disabled races:** a switched-on extension is offered for new choices (wizard, level-up, planner, admin mode, random characters, catalog, wiki search); a disabled race is not offered for new characters. Characters keep everything they already have; switching something off never removes it from a sheet.
- **Group passphrase:** if set, every browser has to enter it once before it sees anything. A new passphrase makes every browser enter it again; *Remove the group passphrase* opens the site to anyone who finds it. The narrator never needs it.
- **Email for new feedback:** each new feedback message is mailed to this address, but only if the server has mail settings (`EMAIL_HOST`); the page tells you when it has none.

## Characters
- **Reset password:** type a new password (at least 8 characters) next to the character and click *Set*.
- **Delete** moves a character to the trash.
- **Admin mode** on a sheet lets you change values the rules normally fix (manual Misc values, the creation wizard's choices, level-ups without XP). Specialties and augments added there are marked **GM** and are never removed by rule checks. Every save shows what changed.

## Catalog
- Only the narrator can change **Playing Guide items**. A changed one is marked *modified*; **Reset to book** restores the book values. Deleting a book item hides it: choose *Hidden* in the source filter to find it and restore it. Restarting the server never overwrites these changes and never brings hidden items back.
- **Export CSV** downloads the (filtered) catalog in the import format; **Bulk import** brings an edited file back with a preview (see *Inventory and items*). Custom items that are deleted go to the trash.

## Feedback
Players send bugs, feature requests and feedback with the speech bubble in the bottom right corner. The *Feedback* section lists them with page, character and browser details. Set a status (new, in progress, done, won't fix), keep a **narrator note** or delete a message.

## Table
- **Party overview** shows every active character: HP, wounds, AP left in a fight, stance, active effects, last change, whether a password is set and failed unlock attempts. It refreshes every 10 seconds.
- **Group actions** give XP to every active character, give everyone a breather or end fight mode for everyone. Each character's change is logged like a play action.
- **Action log** lists who changed what (narrator, player session, anonymous, system), with filters for character, kind of action, who and dates. Entries are kept for 180 days.
- **Undo:** in a character's *History* (Story tab), **Undo last action** reverts the last play action and **Reverse last level-up** takes back the last level-up (the max-HP gain and the level history entry go too). It is refused when the same values changed again since, and for changes to items, companions, custom modifiers and texts; change those by hand.

## Export, copies and snapshots
- **Export** downloads a character as a JSON file (without its password). **Import a character** turns such a file into a *new* character with a new password; existing characters are never overwritten. The file is checked strictly; a file that doesn't fit is refused with the reason.
- **Duplicate** makes a copy of a character under a new name and password.
- **Snapshots:** before every level-up the character is saved; the last 10 per character can be downloaded and imported like an export.

## Trash
Deleted characters, wiki pages and custom catalog items go to the **trash** on the narrator page. **Restore** brings them back, **Delete for good** removes them at once. After 30 days in the trash they are deleted for good by the next cleanup (at every server start and, if set up, nightly). *Move abandoned drafts to the trash* collects characters still in creation that nobody changed for 30 days.

## Backups
The server makes a database backup at every start (so before every update) and, once the nightly job is set up, every night; the *Server* section of the narrator page shows the time of the newest one. Setting up the nightly job and restoring a backup are server steps: see the README.

## Other
- The rules switches never change existing characters; they only decide what is offered next.
- Journal versions are restored in the Django admin (*Journal revisions*), wiki versions on the page's *History*.
