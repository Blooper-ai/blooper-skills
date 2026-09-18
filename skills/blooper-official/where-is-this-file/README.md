# Where this file lives

Adds a **Location** panel to the file inspector: where the file sits, what it
was made from, and what else is beside it.

This is a **widget-only** skill. It renders a panel and never starts a run, so
it spends nothing and asks for nothing.

## What it does

Open a file, open the inspector, and pick the **Widgets** tab. The panel shows
five things about the file you are looking at:

- **Where this file lives** — the chain of containers it sits inside,
  outermost first, ending in the file itself.
- **Generated from** — the files this version was generated from, with
  thumbnails. Flat, because several inputs are siblings rather than a chain.
  An input that has moved on since is marked *updated since*.
- **Also in here** — the other files in the same container, with thumbnails.
  The file you are looking at is not listed as its own neighbour.
- **Directly inside** — the immediate container, as a badge.
- **Container type** — whether that container is a tag or a board.

Rows that have no answer say so in words rather than showing a blank, and a
section whose data could not be loaded is marked as incomplete instead of
silently reading as "none".

## When to use it

Chasing a wrong-looking output. "Generated from" answers *what went into this*,
which is usually the first question — and if an input has been updated since
this version was made, the panel says so rather than leaving you to compare
timestamps.

Also useful for finding your way around a project someone else organised.

## What it costs

Nothing. `runnable: false` means the package contributes a panel and no run, so
there is no prompt to execute, no provider call and no credit spend. The
platform enforces that rather than taking the manifest's word for it: a run
requested for this package is refused at the trigger endpoint, at an agent
spawn, and in the Skill IDE's Try-it panel.

## Notes

- **Read-only.** It renders what the project already knows. It cannot change a
  file, a version or a container.
- **"Generated from" is upstream only.** It shows what this version was made
  *from*, not what was made *from it* — that question needs a different query
  than the inspector has to hand.
- **"Also in here" is capped** at the container's first 200 files. Past that it
  shows the first 200 rather than claiming the container is smaller than it is.
- The panel is per-file: it reads the file you have open and nothing else.

## For skill authors

This is the reference example of a widget-only package. The shape is:

```yaml
runnable: false          # authored, not inferred — see below
tools: []
widgets:
  - id: where-is-this-file
    title: Location
    elements: [...]
```

`runnable` defaults to **true**, so every existing manifest keeps its run and a
package that only renders has to declare it. Declaring `widgets` alone is not
enough, and `runnable: false` with no widgets is refused — it would be a
package reachable from nowhere.

A widget is **data, not code**: you choose elements (`text`, `badge`, `tree`)
and bind them to platform-provided sources. You cannot ship a component, and
you never choose layout, spacing or colour. See the `widgets` section of the
manifest reference for the element and source vocabulary — a source the build
does not know makes the manifest non-installable, and a `tree` bound to a
source that does not yield one renders empty.
