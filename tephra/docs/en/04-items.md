# Inventory and items

- **Found something?** Type a name (blanket, bottle, shark tooth …), a quantity and notes in the inventory tab: it is added as a *general item*.
- **Add from catalog** shows every item; *pay* takes the price from your money on hand (only if you have enough). Filter by source (*book*, *modified* book items, *custom*) and extension; long lists have pages.
- **Copy** opens the object creator with a copy of any catalog item, saved as your own custom item.
- **Export CSV** downloads the (filtered) catalog in the import format: edit it in a spreadsheet and bring it back with **Bulk import**. The import preview shows per row whether it is new, updates an existing item, is unchanged or is skipped (Playing Guide items can only be changed by the narrator).
- Playing Guide items can only be changed by the narrator. Changed ones are marked *modified* and have **Reset to book**; deleting one hides it (filter *Hidden* to restore). Restarting the server never overwrites these changes.
- **Create item** opens the object creator: choose kind and size and the rules fill in damage class, AP, range and armor values ("auto"). Weapons can get an **Accuracy bonus** and melee weapons and bows a **Strike bonus**. Armor penalties are entered as numbers and subtracted.
- Every item you create is also **saved to the shared catalog**, so everyone can use it.
- Choose where an item is (left/right hand, armor, deflection, worn, carried, stored). Only worn and held items apply their modifiers. A two-handed item goes into the left hand and blocks the right one.
- **From the catalog:** search the catalog right in the inventory tab and add an item without leaving the sheet.
- **Give** hands an item (or part of a stack) to another character you have unlocked; both journals note it.
- On page 2, tap a gear line with a quantity (ammunition, stacks) for − / +.

## Bulk import format
**Bulk import** (catalog) takes a CSV file or a pasted table: from a spreadsheet, CSV with `,` or `;`, or a markdown table. The first row names the columns; only `name` is needed. *Download CSV template* gives a sample file.

- Useful columns: `kind` (melee, firearm, bow, crossbow, armor, deflection, ammo, gear, animal, vehicle …), `size`, `variants` (flexible / polearm / throwing / impromptu / double-barreled), `material`, `price` (`5 pr`, `3 d`), `augments` (`Accurate II; Damaging I`), `description`, `quantity`. Common other names are understood (e.g. *type* for kind, *cost* for price, *qty* for quantity).
- Empty number columns (damage class, AP, range, soak …) use the rules' size tables.
- The preview lists every row with its problems; only rows without problems are imported. Opened from a character's inventory, you choose whether they go into that inventory or into the shared catalog.
- The file from **Export CSV** has the same format (with the exact price in dukes and a few more columns), so it can be edited and imported again.
