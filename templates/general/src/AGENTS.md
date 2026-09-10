After changes, run your platform's `verify.sh` or `verify.ps1` in `.llm/` or
`src/.llm/` if present.

It runs project verification, including tests and linting.
Print all output; do not repeat checks it already runs.

Performance:

- Prefer borrows: `&str` / `&[T]` returns, `&'static str` constants,
  `Cow<'_, str>` for conditional ownership.
- `Box<str>` for immutable strings.
- Reuse buffers via `.clear()`.
- Const generics for compile-time branching such as
  `<const LINE_NUMBERS: bool>`.
- Prefer performance-oriented crates such as `parking_lot` and `memchr`.
- Keep dependency footprint minimal.
