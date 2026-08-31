# Character Turn Around

Four views of the character you are standing on — front, three-quarter, side and
back — in one horizontal row on a plain studio background, saved as a new asset.

Run it from an IMAGE in the **Characters** tag. It takes no input: the card is
the character.

## Why it does not describe the character

The reference image is attached to the generation (`ref_version_ids`), so the
model can already see the character. An earlier, unpublished version of this
skill also asked the agent to *write a description* of it first — a habit
inherited from a version that had no tools and whose only product was text.

That description is a second, lossier source of truth, and the model sometimes
follows it instead of the picture. Measured on a graffiti character with
mechanical wings riding a bicycle: the agent wrote "a 2D stylized illustration
of a young human, slim build, medium-length hair" and the render came back as a
plain boy — no wings, no bicycle — from the same reference and the same
provider. Removing the describe step also made the prompt identical run to run,
so repeat runs hit the generation cache instead of paying for a fresh render
that disagrees with the last one.

`blooper-official/character-emotions` states the same rule for the same reason.
