# Leo Shaw — Neural Atlas

Static, build-free portfolio for GitHub Pages. The homepage uses an organic
canvas network with six project controls: hover, keyboard focus, or tap to reveal
skill nodes. Mouse clicks and keyboard activation open the project directly;
touch users reveal skills first and use **View project** to open the case study.
Ordinary project links
remain available independently of the canvas. Animation respects reduced-motion
preferences, can be paused, and stops off-screen or when the tab is hidden.

## Local preview

Run `python3 -m http.server 8127` from the repository, then visit
`http://localhost:8127/`. Run checks with `python3 tools/test_site.py`.

Homepage files: `index.html`, `neural-atlas.css`, and `neural-atlas.js`.
Open `http://localhost:8127/tools/atlas-interaction-test.html` to run the browser
interaction regressions against the real homepage (touch toggle, outside tap,
buffered pointer exit, keyboard focus, and Escape). All results should say PASS.
Open `http://localhost:8127/tools/design-audit.html` for rendered text contrast,
horizontal overflow, and section-anchor checks across all 11 pages at 1280, 768,
390, and 320 pixels, including expanded atlas states. This is a regression check,
not a substitute for visual review or a complete accessibility certification.
Case studies retain their existing layouts in `styles.css` with a matching dark
palette. Optimized homepage photos are `assets/atlas-*.jpg`.

## Classic design backup

The previous design is preserved on `codex/classic-portfolio` at commit
`d7992f1`. Preview that branch in a separate checkout to compare designs.
Changing local branches does not change the published site; GitHub Pages serves
the branch configured in the repository's Pages settings.
