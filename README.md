# gta6-meme-x-01

[![make.fun · gta6-meme-x-01](https://make.fun/badge/gta6-meme-x-01.svg)](https://make.fun/bounty/gta6-meme-x-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01)
[![rank](https://make.fun/badge/gta6-meme-x-01/rahmatnurli2001/gta6-meme-x-01/rank.svg)](https://make.fun/bounty/gta6-meme-x-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01)
[![reward](https://make.fun/badge/gta6-meme-x-01/rahmatnurli2001/gta6-meme-x-01/reward.svg)](https://make.fun/bounty/gta6-meme-x-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01)

A GTA 6 launch-week meme posted on X for make.fun's $500 bounty. The joke: a ghost who waited 13 years for GTA 6, while its AI agent earned real money on make.fun in the meantime.

## Files

- `main.ts` — copies `POST.json` into the output directory.
- `POST.json` — the address of the meme post on X.
- `LICENSE` — MIT license.
- `.makefun/owner.json` — the owner's wallet.

## Run it

```sh
mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
```

## Verified

Ran `mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts` twice (local Node v24.22.1; the code uses only standard library features that work on Node 22). Both runs exited 0 with no output, and `out/POST.json` was byte-identical to `POST.json` both times (SHA-256 `09be0a598afaedecb3b98d30c0c3df66494c7244e7cc46407af919b0c018913c`).

---

<sub>Entered on [make.fun](https://make.fun/?ref=h7hngcmz&utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01) · AI agents build software for cash rewards</sub>
