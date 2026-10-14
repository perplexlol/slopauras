# Unreleased

## Fixed

- Preserve empty class and power-type overrides when sharing configurations, and
  keep groups selecting no units from switching to the player after import.
- Reject fractional icon counts and draw layers during import.
- Position priority-stack icons during initialization so rebuilding them in
  combat can preserve their anchors and display order.

# 0.5.0

## New

- Added LibGetFrame which should mean we now play nice with whatever popular frame addon you're using (Grid2, EUI, ...)
- Sisyphean settings improvements

## Fixed

- Sisyphean perf improvements
