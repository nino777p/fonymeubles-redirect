# Fony Meubles — Product Video Production Rules

## When to Use

Any video for Fony Meubles (furniture shop): Reels, ads, website loops, catalogue videos.
These rules override generic creative guidance (including `commercial-product-video.md`) wherever they conflict.

## Non-negotiables

1. **Real photos only.** The visuals are the client's own product photos. Do not generate, edit, inpaint,
   upscale with generative models, or animate the product with any image/video generation provider.
   The furniture must look exactly as photographed.
2. **Zero cost by default.** Do not call any paid provider or API key unless the client explicitly asks for it
   and approves the cost first.
3. **Style playbook:** `fony-meubles` (`styles/custom/fony-meubles.yaml`). Professional, calm, premium. Never
   childish, never gimmicky.
4. **No invented claims.** No price, dimension, material or promotion text unless the client supplied it.

## Production Recipe (20-30 s)

| Step | Tool | Rule |
|---|---|---|
| Shots | `fony_photo_motion` | One clip per photo, 3-5 s each. Alternate movements: avance, recule, derive_droite, derive_gauche. `framing=auto` (it picks full-bleed or off-white gallery frame). |
| Order | agent | Wide/hero view first, then 3/4 angle, then material details, hero again near the end. |
| Edit | Remotion or FFmpeg | Dissolves of ~0.8 s only. First shot fades in from black. |
| End card | Remotion / HyperFrames text card | Off-white `#F5F2ED`, "Fony Meubles" in Didot, website below in Helvetica Neue, 3-3.5 s, text fades in. No fade to black after the card. |
| Music | music library / free sources | Soft acoustic or minimal piano, royalty-free **with commercial licence**; record the licence in the decision log. Fade in 1 s, fade out 2.5 s. |
| QA | standard self-review | Compare every shot's product against the source photo; reject any shot where the product differs. |

## Formats

- Reel / TikTok / Shorts: `aspect=portrait` (1080x1920)
- Website / YouTube: `aspect=landscape` (1920x1080)
- Instagram feed: `aspect=square` (1080x1080)

## If the brief asks for more than photos can give

If the client asks for a 360° orbit, an assembly animation, or angles that are not in the photos: say so
plainly, and propose either more photos or a short filmed clip from the client. Do not substitute generated footage.
