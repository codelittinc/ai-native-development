# Historical Supply-Chain Incidents

Pattern recognition ONLY. These are documented past attacks, NOT current IOCs. Never report them as findings unless a live advisory (Check 1) says a currently installed version is affected. Use them to recognize attack shapes.

| Incident | Ecosystem | Date | Attack pattern |
|----------|-----------|------|----------------|
| `event-stream` | npm | Nov 2018 | Maintainer handoff; malicious `flatmap-stream` dependency targeting Copay wallets |
| `ua-parser-js` | npm | Oct 2021 | Account compromise; cryptominer + credential stealer |
| `colors` / `faker` | npm | Jan 2022 | Maintainer self-sabotage; infinite loops |
| `node-ipc` | npm | Mar 2022 | Protestware; file-wiping payload by geography |
| `polyfill.io` | CDN | Jun 2024 | Domain takeover serving malicious scripts |
| `chalk` / `debug` / `ansi-styles` et al. | npm | Sep 2025 | Maintainer phishing; crypto-clipper payload in billions-of-downloads packages |
| `@ctrl/tinycolor` ("Shai-Hulud") | npm | Sep 2025 | Self-replicating credential-stealing worm |
