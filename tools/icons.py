"""Иконки сайтов-приложений: у каждого заведения свой рисунок по смыслу, его шрифт и цвета.

    python tools/icons.py            # все
    python tools/icons.py lado zag   # выборочно

Каждая иконка — SVG 512×512: раскладка (poster, seal, frame, neon) + рисунок из MOTIFS + название
фирменным шрифтом сайта (Google Fonts). Все иконки собираются в одну страницу, Edge в headless-режиме
снимает её, а скрипт режет на файлы: icon-512.png, icon-192.png, apple-touch-icon.png (180),
icon-maskable-512.png (рисунок ужат до 80% под круглую маску Android), favicon.png (64, скруглённая).
Нужен Microsoft Edge (есть в Windows) и интернет (шрифты)."""
import html as H
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SITES = ROOT / "sites"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# Рисунки в поле 100×100. currentColor — основной цвет (fg), var(--fg2) — второй, var(--cut) — вырезы цветом фона.
MOTIFS = {
    "bread": '<path d="M12 64C12 40 30 30 50 30s38 10 38 34c0 7-6 12-14 12H26c-8 0-14-5-14-12z"/>'
             '<path d="M33 42l-6 18M50 38l-6 22M67 42l-6 18" stroke="var(--cut)" stroke-width="4.5" stroke-linecap="round" fill="none"/>',
    "mug": '<rect x="22" y="36" width="44" height="50" rx="6"/>'
           '<path d="M66 46h8a9 9 0 0 1 9 9v12a9 9 0 0 1-9 9h-8v-8h7a3 3 0 0 0 3-3v-8a3 3 0 0 0-3-3h-7z"/>'
           '<path d="M19 40a8 8 0 0 1 8-13 10 10 0 0 1 17-5 9 9 0 0 1 16 2 8 8 0 0 1 9 16z" fill="var(--fg2)"/>'
           '<path d="M34 50v26M44 50v26M54 50v26" stroke="var(--cut)" stroke-width="3.5" stroke-linecap="round"/>',
    "hop": '<path d="M50 22c16 10 22 32 12 52-4 8-8 13-12 15-4-2-8-7-12-15-10-20-4-42 12-52z"/>'
           '<path d="M50 22c6-10 18-12 24-8-4 8-14 10-24 8z" fill="var(--fg2)"/>'
           '<path d="M36 42q14 10 28 0M33 56q17 10 34 0M37 70q13 9 26 0M50 32v52" stroke="var(--cut)" stroke-width="3" fill="none" stroke-linecap="round"/>',
    "sunset": '<circle cx="50" cy="50" r="30"/>'
              '<path d="M14 58h72M14 66h72M14 74h72" stroke="var(--cut)" stroke-width="4"/>'
              '<path d="M10 86c8-6 14-6 20 0s12 6 20 0 14-6 20 0 12 6 20 0" stroke="var(--fg2)" stroke-width="5" fill="none" stroke-linecap="round"/>',
    "shell": '<path d="M50 80L20 46c0-18 14-28 30-28s30 10 30 28z"/><path d="M41 80h18l-3 9H44z"/>'
             '<path d="M50 78L27 44M50 78L36 28M50 78V22M50 78l14-50M50 78l23-34" stroke="var(--cut)" stroke-width="3.2" stroke-linecap="round"/>',
    "fleur": '<path d="M50 10c10 14 12 30 4 48h-8c-8-18-6-34 4-48z"/>'
             '<path d="M45 58c-15 3-28-5-26-18 2-9 13-11 17-3-6 0-8 8-2 12 4 2 8 2 11 0z"/>'
             '<path d="M55 58c15 3 28-5 26-18-2-9-13-11-17-3 6 0 8 8 2 12-4 2-8 2-11 0z"/>'
             '<rect x="32" y="58" width="36" height="8" rx="2" fill="var(--fg2)"/><path d="M44 66l-4 20c4-4 8-4 10 2 2-6 6-6 10-2l-4-20z"/>',
    "wineglass": '<path d="M30 14h40c2 26-6 42-20 44-14-2-22-18-20-44z"/><path d="M33 30h34c-1 14-7 22-17 24-10-2-16-10-17-24z" fill="var(--fg2)"/>'
                 '<rect x="47" y="57" width="6" height="22"/><path d="M33 84c6-5 28-5 34 0v4H33z"/>',
    "grapes": '<path d="M50 28c0-8 4-14 10-16" stroke="currentColor" stroke-width="4" fill="none" stroke-linecap="round"/>'
              '<path d="M52 26c6-12 22-14 28-8-6 10-18 12-28 8z" fill="var(--fg2)"/>'
              + "".join(f'<circle cx="{x}" cy="{y}" r="9"/>' for x, y in [(32, 40), (50, 40), (68, 40), (41, 56), (59, 56), (50, 72)])
              + '<path d="M30 36a6 6 0 0 1 5-4M48 36a6 6 0 0 1 5-4M66 36a6 6 0 0 1 5-4" stroke="#fff" stroke-opacity=".5" stroke-width="2" fill="none"/>',
    "sushi": '<circle cx="50" cy="52" r="32"/><circle cx="50" cy="52" r="24" fill="var(--cut)"/><circle cx="50" cy="52" r="20" fill="#ffffff"/>'
             '<path d="M50 40a12 12 0 1 1-0.1 0z" fill="var(--fg2)"/><path d="M44 50c4-4 9-4 12 0" stroke="#fff" stroke-width="2" fill="none"/>',
    "ball8": '<circle cx="50" cy="50" r="36"/><circle cx="50" cy="44" r="16" fill="var(--fg2)"/>'
             '<text x="50" y="54" text-anchor="middle" font-size="26" font-family="Arial Black,Arial" font-weight="900" fill="currentColor">8</text>'
             '<path d="M30 30a24 24 0 0 1 14-10" stroke="#fff" stroke-opacity=".35" stroke-width="4" fill="none" stroke-linecap="round"/>',
    "skewer": '<g transform="rotate(-40 50 50)"><path d="M6 50h88" stroke="var(--fg2)" stroke-width="4" stroke-linecap="round"/>'
              '<rect x="20" y="38" width="15" height="24" rx="5"/><rect x="40" y="38" width="15" height="24" rx="5"/><rect x="60" y="38" width="15" height="24" rx="5"/>'
              '<circle cx="84" cy="50" r="6" fill="var(--fg2)"/></g>',
    "martini": '<path d="M16 22h68L50 58z"/><rect x="48" y="57" width="4" height="25"/><rect x="34" y="82" width="32" height="5" rx="2"/>'
               '<circle cx="62" cy="31" r="6" fill="var(--fg2)"/><path d="M62 31l12-16" stroke="var(--fg2)" stroke-width="2.5"/>',
    "bottle": '<path d="M30 10h10v14c8 4 10 10 10 18v42a4 4 0 0 1-4 4H24a4 4 0 0 1-4-4V42c0-8 2-14 10-18z"/>'
              '<rect x="24" y="50" width="22" height="18" rx="2" fill="var(--cut)"/>'
              '<path d="M60 44h26c1 13-5 21-13 21s-14-8-13-21z" fill="var(--fg2)"/><rect x="72" y="64" width="2.5" height="16" fill="var(--fg2)"/><rect x="65" y="80" width="17" height="4" rx="2" fill="var(--fg2)"/>',
    "knight": '<path d="M30 84h44v-8h-6c-2-14 2-24-2-36-4-14-16-22-30-20l-3-6-6 8c-4 6-6 14-4 20l10 6 8-4c2 6-4 12-8 20-2 6-2 10-2 12h-1z"/>'
              '<circle cx="40" cy="31" r="3" fill="var(--cut)"/><rect x="24" y="86" width="56" height="7" rx="2" fill="var(--fg2)"/>',
    "flame": '<path d="M50 8c4 16 22 26 22 50 0 17-11 30-22 30S28 75 28 60c0-13 8-19 10-30 4 8 6 12 9 15 3-11 0-24 3-37z"/>'
             '<path d="M50 52c4 8 11 12 11 21 0 7-5 11-11 11s-11-4-11-11c0-7 7-12 11-21z" fill="var(--fg2)"/>',
    "pick": '<path d="M50 92C34 78 16 58 16 36c0-16 16-24 34-24s34 8 34 24c0 22-18 42-34 56z"/>'
            '<path d="M55 20L37 52h13l-7 26 22-36H52l7-22z" fill="var(--cut)"/>',
    "coupe": '<path d="M16 36h68c-2 17-16 24-34 24S18 53 16 36z"/><rect x="48" y="59" width="4" height="21"/><path d="M33 84c6-5 28-5 34 0v4H33z"/>'
             '<circle cx="68" cy="27" r="8" fill="var(--fg2)"/><path d="M69 20c2-7 6-11 12-13" stroke="var(--fg2)" stroke-width="2.6" fill="none"/>',
    "tree": '<circle cx="50" cy="34" r="20"/><circle cx="33" cy="46" r="15"/><circle cx="67" cy="46" r="15"/><circle cx="42" cy="58" r="13"/><circle cx="58" cy="58" r="13"/>'
            '<path d="M46 60h8v26h-8z" fill="var(--fg2)"/><path d="M50 66l-9-9M50 72l9-8" stroke="var(--fg2)" stroke-width="4" stroke-linecap="round"/><path d="M26 88h48" stroke="var(--fg2)" stroke-width="3" stroke-linecap="round"/>',
    "pomegranate": '<circle cx="50" cy="58" r="30"/><path d="M38 32l4-14 8 9 8-9 4 14z" fill="currentColor"/>'
                   '<path d="M32 56a18 18 0 0 1 12-16" stroke="var(--cut)" stroke-width="4" fill="none" stroke-linecap="round" stroke-opacity=".6"/>'
                   + "".join(f'<circle cx="{x}" cy="{y}" r="3.2" fill="var(--fg2)"/>' for x, y in [(52, 60), (60, 66), (46, 70), (56, 74), (64, 56)]),
    "bull": '<path d="M30 34c0-8 8-12 20-12s20 4 20 12c0 16-6 32-10 42-2 6-6 10-10 10s-8-4-10-10c-4-10-10-26-10-42z"/>'
            '<path d="M32 34C20 34 10 26 10 12c6 10 14 14 24 14zM68 34c12 0 22-8 22-22-6 10-14 14-24 14z" fill="var(--fg2)"/>'
            '<path d="M30 40l-12 4 12 5zM70 40l12 4-12 5z"/>'
            '<circle cx="41" cy="44" r="3.2" fill="var(--cut)"/><circle cx="59" cy="44" r="3.2" fill="var(--cut)"/><circle cx="45" cy="76" r="3" fill="var(--cut)"/><circle cx="55" cy="76" r="3" fill="var(--cut)"/>',
    "foot": '<path d="M50 36c14 0 22 12 20 28-2 16-10 26-22 26S30 80 32 66c2-16 6-30 18-30z"/>'
            + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r + 1.5}"/>' for x, y, r in [(31, 30, 6), (41, 21, 6.5), (54, 18, 7), (66, 22, 6.5), (75, 31, 6)]),
    "carpet": '<rect x="22" y="14" width="56" height="72" rx="3"/><rect x="28" y="20" width="44" height="60" rx="2" stroke="var(--cut)" stroke-width="3" fill="none"/>'
              '<path d="M50 28l16 22-16 22-16-22z" fill="var(--cut)"/><path d="M50 38l8 12-8 12-8-12z"/>'
              + "".join(f'<path d="M{x} 8v6M{x} 86v6" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/>' for x in range(27, 76, 6)),
    "corkscrew": '<rect x="18" y="16" width="64" height="12" rx="6"/><rect x="46.5" y="28" width="7" height="12" fill="var(--fg2)"/>'
                 '<path d="M50 40c12 4 12 10 0 12s-12 8 0 10 12 8 0 10-10 8 0 14" stroke="currentColor" stroke-width="5.5" fill="none" stroke-linecap="round"/>',
    "fedora": '<path d="M28 56c0-20 7-32 22-32s22 12 22 32z"/><path d="M50 26v12" stroke="var(--cut)" stroke-width="3"/>'
              '<rect x="28" y="46" width="44" height="7" fill="var(--fg2)"/><path d="M8 60c16-7 68-7 84 0-6 9-78 9-84 0z"/>',
    "macaron": '<path d="M16 44c0-20 68-20 68 0z"/><rect x="18" y="46" width="64" height="8" rx="3" fill="var(--fg2)"/><path d="M16 56c0 20 68 20 68 0z"/>'
               '<path d="M20 44h60M20 56h60" stroke="var(--cut)" stroke-width="2" stroke-dasharray="3 3"/>',
    "swallow": '<path d="M50 50C40 36 24 28 6 30c14 6 26 16 34 26zM50 50c10-14 26-22 44-20-14 6-26 16-34 26z"/>'
               '<path d="M44 46c2-6 10-6 12 0l2 16 6 24-12-16-2 4-2-4-12 16 6-24z"/><circle cx="50" cy="42" r="6"/>',
    "tomato": '<circle cx="50" cy="58" r="31"/><path d="M50 32l-7-8 7 3 6-8v8l9-1-7 6H43l-8-2 8-1z" fill="var(--fg2)"/>'
              '<path d="M50 28V16" stroke="var(--fg2)" stroke-width="4" stroke-linecap="round"/><path d="M30 52a20 20 0 0 1 10-14" stroke="#fff" stroke-opacity=".55" stroke-width="4" fill="none" stroke-linecap="round"/>',
    "pizza": '<path d="M50 90L16 22c22-12 46-12 68 0z"/><path d="M20 28c20-9 40-9 60 0" stroke="var(--fg2)" stroke-width="7" fill="none" stroke-linecap="round"/>'
             + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="var(--cut)"/>' for x, y, r in [(47, 42, 6), (60, 50, 5), (41, 60, 5), (52, 72, 4)]),
    "pineapple": '<path d="M50 34L38 8l10 12 2-16 2 16 10-12z" fill="var(--fg2)"/><ellipse cx="50" cy="62" rx="23" ry="28"/>'
                 '<path d="M32 46l36 36M28 60l26 26M40 38l32 32M68 46L32 82M72 60L46 86M60 38L28 70" stroke="var(--cut)" stroke-width="2.5"/>',
    "anchor": '<circle cx="50" cy="15" r="7" stroke="currentColor" stroke-width="5" fill="none"/><path d="M50 22v62M33 36h34M20 62c2 16 16 24 30 24s28-8 30-24" stroke="currentColor" stroke-width="7" fill="none" stroke-linecap="round"/>'
              '<path d="M13 67l7-13 9 11zM87 67l-7-13-9 11z"/><circle cx="50" cy="36" r="4" fill="var(--fg2)"/>',
    "khinkali": '<path d="M50 14c4 8 6 14 10 18 14 6 26 18 26 32 0 16-16 24-36 24S14 80 14 64c0-14 12-26 26-32 4-4 6-10 10-18z"/>'
                '<path d="M50 28c-4 16-16 26-26 36M50 28c-2 20-6 36-10 54M50 28c2 20 6 36 10 54M50 28c4 16 16 26 26 36" stroke="var(--cut)" stroke-width="3" fill="none" stroke-linecap="round"/>'
                '<rect x="45" y="8" width="10" height="9" rx="3" fill="var(--fg2)"/>',
    "nofish": '<path d="M12 50c12-16 34-20 52-10l20-12-6 22 6 22-20-12c-18 10-40 6-52-10z"/><circle cx="26" cy="46" r="3.5" fill="var(--cut)"/>'
              '<path d="M14 86L86 14" stroke="var(--cut)" stroke-width="13" stroke-linecap="round"/><path d="M14 86L86 14" stroke="var(--fg2)" stroke-width="7" stroke-linecap="round"/>',
    "shot": '<path d="M28 20h44l-7 64H35z" fill="none" stroke="currentColor" stroke-width="5" stroke-linejoin="round"/><path d="M32 44h36l-5 38H37z" fill="var(--fg2)"/>'
            '<path d="M76 18c8 0 12 6 12 12" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round"/>',
    "apple": '<path d="M50 30c-10-8-30-6-30 18 0 22 16 40 30 34 14 6 30-12 30-34 0-24-20-26-30-18z"/>'
             '<path d="M50 30c0-8 2-14 6-18" stroke="var(--fg2)" stroke-width="4" fill="none" stroke-linecap="round"/><path d="M54 22c6-10 18-10 22-6-6 8-14 10-22 6z" fill="var(--fg2)"/>'
             '<path d="M32 46a14 14 0 0 1 8-10" stroke="#fff" stroke-opacity=".5" stroke-width="4" fill="none" stroke-linecap="round"/>',
    "grill": '<circle cx="50" cy="54" r="32" fill="none" stroke="currentColor" stroke-width="6"/>'
             '<path d="M26 40h48M20 54h60M26 68h48" stroke="currentColor" stroke-width="4"/><path d="M30 84l-6 10M70 84l6 10" stroke="currentColor" stroke-width="5" stroke-linecap="round"/>'
             '<rect x="30" y="44" width="40" height="8" rx="4" fill="var(--fg2)" transform="rotate(-12 50 48)"/><rect x="28" y="58" width="40" height="8" rx="4" fill="var(--fg2)" transform="rotate(-12 48 62)"/>',
    "knife": '<circle cx="62" cy="38" r="24" fill="var(--fg2)"/><g transform="rotate(-32 50 55)"><rect x="6" y="51" width="26" height="10" rx="3"/>'
             '<path d="M32 50h48c8 0 14 4 16 6-6 4-12 5-20 5H32z"/></g>',
    "panda": '<path d="M22 30l4-16 16 10zM78 30l-4-16-16 10z"/><path d="M27 22l1-4 6 4zM73 22l-1-4-6 4z" fill="var(--fg2)"/>'
             '<path d="M18 52c0-20 14-30 32-30s32 10 32 30-14 32-32 32-32-12-32-32z"/>'
             '<ellipse cx="36" cy="40" rx="7" ry="4.5" fill="var(--cut)"/><ellipse cx="64" cy="40" rx="7" ry="4.5" fill="var(--cut)"/>'
             '<ellipse cx="31" cy="63" rx="10" ry="8" fill="var(--cut)"/><ellipse cx="69" cy="63" rx="10" ry="8" fill="var(--cut)"/><ellipse cx="50" cy="67" rx="12" ry="10" fill="var(--cut)"/>'
             '<ellipse cx="50" cy="60" rx="5" ry="3.5" fill="var(--fg2)"/><path d="M33 51q5 4 10 0M57 51q5 4 10 0" stroke="var(--fg2)" stroke-width="2.6" fill="none" stroke-linecap="round"/>',
    "cheese": '<path d="M12 70L80 34l8 12v34H12z"/><path d="M12 70L80 34l8 12L20 78z" fill="var(--fg2)" fill-opacity=".25"/>'
              + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="var(--cut)"/>' for x, y, r in [(34, 66, 5), (56, 60, 6), (74, 70, 4), (46, 76, 3)]),
    "meh": '<circle cx="50" cy="50" r="36"/><circle cx="38" cy="44" r="5" fill="var(--cut)"/><circle cx="62" cy="44" r="5" fill="var(--cut)"/>'
           '<path d="M36 64h28" stroke="var(--cut)" stroke-width="5.5" stroke-linecap="round"/><path d="M30 34l12-3M58 31l12 4" stroke="var(--cut)" stroke-width="3.5" stroke-linecap="round"/>',
    "lantern": '<path d="M50 4v10" stroke="var(--fg2)" stroke-width="2.5"/><rect x="36" y="14" width="28" height="9" rx="2" fill="var(--fg2)"/>'
               '<path d="M32 23c-7 12-7 34 0 50h36c7-16 7-38 0-50z"/><path d="M28 36h44M26 48h48M28 60h44" stroke="var(--cut)" stroke-width="2.5" stroke-opacity=".5"/>'
               '<rect x="36" y="73" width="28" height="9" rx="2" fill="var(--fg2)"/><path d="M50 82v12" stroke="var(--fg2)" stroke-width="3"/>',
    "olive": '<path d="M16 84C36 66 56 44 84 16" stroke="currentColor" stroke-width="3.5" fill="none" stroke-linecap="round"/>'
             + "".join(f'<ellipse cx="{x}" cy="{y}" rx="12" ry="5" transform="rotate({a} {x} {y})"/>' for x, y, a in [(30, 62, -80), (40, 70, 10), (46, 46, -80), (56, 54, 10), (62, 30, -80), (72, 38, 10)])
             + '<ellipse cx="34" cy="78" rx="6" ry="7.5" fill="var(--fg2)"/><ellipse cx="66" cy="20" rx="5.5" ry="7" fill="var(--fg2)"/>',
    "horseshoe": '<path d="M28 18v34c0 18 10 30 22 30s22-12 22-30V18" stroke="currentColor" stroke-width="14" fill="none"/>'
                 + "".join(f'<circle cx="{x}" cy="{y}" r="2.3" fill="var(--cut)"/>' for x, y in [(28, 26), (28, 40), (30, 56), (72, 26), (72, 40), (70, 56), (40, 76), (60, 76)])
                 + '<circle cx="50" cy="40" r="8" fill="var(--fg2)"/>',
    "decanter": '<circle cx="50" cy="9" r="5.5" fill="var(--fg2)"/><path d="M43 14h14v18c12 6 18 18 18 30 0 16-12 26-25 26S25 78 25 62c0-12 6-24 18-30z"/>'
                '<path d="M29 64c6-6 11 6 17 0s11 6 17 0 9 4 10 2M31 75c6-6 11 6 17 0s11 6 17 0" stroke="var(--cut)" stroke-width="3" fill="none" stroke-linecap="round"/>',
    "disco": '<path d="M50 4v14" stroke="currentColor" stroke-width="2.5"/><circle cx="50" cy="50" r="31"/>'
             '<path d="M19 50h62M22 36h56M22 64h56M30 25h40M30 75h40M50 19v62M35 22c-6 18-6 38 0 56M65 22c6 18 6 38 0 56" stroke="var(--cut)" stroke-width="2" fill="none"/>'
             '<path d="M86 22l2 6 6 2-6 2-2 6-2-6-6-2 6-2zM12 70l2 5 5 2-5 2-2 5-2-5-5-2 5-2z" fill="var(--fg2)"/>',
    "hotpot": '<path d="M38 8c-6 6 6 10 0 18M50 6c-6 6 6 10 0 18M62 8c-6 6 6 10 0 18" stroke="var(--fg2)" stroke-width="3.5" fill="none" stroke-linecap="round"/>'
              '<rect x="14" y="36" width="72" height="8" rx="3"/><path d="M18 46h64c0 22-14 36-32 36S18 68 18 46z"/>'
              '<path d="M10 40h6M84 40h6" stroke="currentColor" stroke-width="6" stroke-linecap="round"/><path d="M50 46a14 14 0 0 0 0 28" stroke="var(--cut)" stroke-width="3" fill="none"/>',
    "tuna": '<path d="M8 52c18-18 50-22 68-8l18-14-6 22 6 22-18-14c-18 12-50 10-68-8z"/>'
            '<path d="M46 36l6-12 6 14zM46 66l6 12 6-14z" fill="var(--fg2)"/><path d="M62 42l3-5 3 6M62 62l3 5 3-6" stroke="var(--fg2)" stroke-width="2.5" fill="none"/>'
            '<circle cx="22" cy="48" r="3.4" fill="var(--cut)"/><path d="M32 42c-3 6-3 14 0 20" stroke="var(--cut)" stroke-width="2.5" fill="none"/>',
    "axe": '<g transform="rotate(35 50 50)"><rect x="47" y="8" width="6" height="88" rx="2" fill="var(--fg2)"/>'
           '<path d="M53 16c18-4 32 4 36 18-8-2-18 0-28 8h-8zM47 16c-18-4-32 4-36 18 8-2 18 0 28 8h8z"/></g>',
    "jasmine": "".join(f'<ellipse cx="50" cy="28" rx="11" ry="20" transform="rotate({a} 50 52)"/>' for a in (0, 72, 144, 216, 288))
               + '<circle cx="50" cy="52" r="9" fill="var(--fg2)"/>',
    "wheat": '<path d="M50 92V22" stroke="currentColor" stroke-width="3.5" stroke-linecap="round"/>'
             + "".join(f'<ellipse cx="{50 + s * 9}" cy="{y}" rx="6" ry="11" transform="rotate({s * 35} {50 + s * 9} {y})"/>' for y in (30, 44, 58, 72) for s in (-1, 1))
             + '<ellipse cx="50" cy="18" rx="6" ry="11"/>',
}

# Дизайн каждого заведения: раскладка, рисунок, цвета (фон, рисунок, второй цвет, текст), шрифт, название, подпись.
D = lambda layout, motif, bg, fg, fg2, ink, font, label, sub="", w=700, it=False, ring=None: dict(
    layout=layout, motif=motif, bg=bg, fg=fg, fg2=fg2, ink=ink, font=font, label=label, sub=sub, w=w, it=it, ring=ring or fg)
DESIGN = {
    "6_pm_bread_kitchen": D("poster", "bread", "#111111", "#e6c229", "#e6c229", "#ffffff", "Manrope", "6 PM", "BREAD KITCHEN", 800),
    "aksiom_pab": D("seal", "mug", "#7a4a1e", "#fff7ea", "#d9a441", "#fff7ea", "Bitter", "АКСИОМ", "ПАБ", ring="#d9a441"),
    "arma": D("poster", "hop", "#161513", "#f2a93b", "#b5432a", "#f1ece0", "Rubik Mono One", "АРМА", "CRAFT", 400),
    "bali": D("poster", "sunset", "#e8642c", "#f6ecdc", "#2f4a3a", "#f6ecdc", "Lora", "MADE IN BALI", "", 700, True),
    "bebe": D("frame", "shell", "#0d3b4f", "#f4b400", "#f4b400", "#fbf6ea", "Montserrat", "BÉBÉ", "DE LA MER", 600),
    "big_easy_bar": D("seal", "fleur", "#0e1f1a", "#d4af5a", "#3fb58c", "#eee6cf", "Philosopher", "BIG EASY", "BAR", ring="#3fb58c"),
    "bokal": D("frame", "wineglass", "#7b1e3a", "#fdeef2", "#c9956a", "#fdeef2", "Merriweather", "БОКАЛ"),
    "bravis": D("poster", "grapes", "#c8321f", "#fffaf0", "#e9a93a", "#fffaf0", "Lora", "BRAVIS", "ВИННЫЙ РЕСТОРАН"),
    "buddy_bar": D("poster", "sushi", "#0d6e8f", "#0b2c3d", "#f2a541", "#ffffff", "Manrope", "BUDDY", "SUSHI & GRILL", 800),
    "chago": D("poster", "ball8", "#0f8a5f", "#111010", "#f2ede6", "#f2ede6", "Bebas Neue", "CHAGO", "", 400),
    "eks": D("seal", "skewer", "#2b1d12", "#e0891a", "#4c6b22", "#f7f0e0", "Bitter", "ЭКСПРОМТ", "С 1996", ring="#e0891a"),
    "esterum": D("neon", "martini", "#07050c", "#ff3fa4", "#3fd0ff", "#ece6f5", "Italiana", "ESTERUM", "", 400),
    "evina": D("poster", "bottle", "#ff5b3a", "#fbf1e3", "#6b1f2e", "#1e1b18", "Amatic SC", "ЕЩЁ ВИНА"),
    "hava_bar_kukhnya": D("poster", "knight", "#12203b", "#f4b942", "#d4402f", "#ffffff", "Montserrat", "HAVA", "БАР & КУХНЯ", 800),
    "kamin": D("frame", "flame", "#3a231a", "#e8823f", "#f6d36b", "#f6ece2", "Marck Script", "Камин", "", 400),
    "kharddey": D("poster", "pick", "#161514", "#ff7a1a", "#ffc247", "#ffc247", "Ruslan Display", "ХАРДДЕЙ", "", 400),
    "kokteylnaya": D("frame", "coupe", "#fbeaee", "#7b1e3a", "#c1121f", "#2b0f18", "Playfair Display", "Коктейльная", "", 700, True),
    "lado": D("frame", "tree", "#1f4a35", "#f4efe3", "#b88a3b", "#f4efe3", "Cormorant", "ЛАДО", "БИСТРО · БАР", 600),
    "makotse": D("poster", "pomegranate", "#0f7b70", "#ff9f7a", "#7a1f1a", "#ffffff", "Prata", "МАКОЦЕ", "", 400),
    "max": D("seal", "bull", "#12281d", "#c8a24e", "#f2ead9", "#f2ead9", "Old Standard TT", "MAX'S BEEF", "FOR MONEY", ring="#c8a24e"),
    "motyga": D("poster", "foot", "#22201e", "#f4efe8", "#ffc247", "#ffc247", "Caveat", "Мотыга Йети"),
    "na_kovyor": D("poster", "carpet", "#5b2fd0", "#c6f432", "#c6f432", "#ffffff", "Exo 2", "НА КОВЁР", "", 800),
    "nashe": D("frame", "corkscrew", "#6b1830", "#f6d6dd", "#b98a4e", "#f6d6dd", "Prata", "НАШЕ ВИНО", "", 400),
    "nuar": D("neon", "fedora", "#0f0e0d", "#c9a253", "#8a2b2b", "#f1e8d6", "Spectral", "НУАР"),
    "nyuans": D("frame", "macaron", "#f4efe3", "#1f4a35", "#b88a3b", "#14261c", "Tenor Sans", "НЮАНС", "", 400),
    "perelyotny_kabak": D("seal", "swallow", "#8c1c2b", "#fff6ee", "#d0a24a", "#fff6ee", "Old Standard TT", "ПЕРЕЛЁТНЫЙ", "КАБАК", ring="#d0a24a"),
    "peys": D("poster", "tomato", "#f5f2ec", "#e2412b", "#3d6b35", "#151515", "Playfair Display", "PACE", "[ПЭЙС]", 700, True),
    "piu_piu": D("poster", "pizza", "#c8321f", "#fffaf0", "#e9a93a", "#fffaf0", "Old Standard TT", "PIU PIU"),
    "pono_place": D("poster", "pineapple", "#7b56c8", "#ffd36e", "#f0a6c0", "#ffffff", "Comfortaa", "PONO", "PLACE"),
    "portovino": D("frame", "anchor", "#2b5fa8", "#ffffff", "#f0b429", "#ffffff", "Spectral", "PORTOVINO", "", 600),
    "pro_khinkali_by_novikov": D("poster", "khinkali", "#2f7f27", "#f6fbe9", "#ff7a59", "#ffffff", "Amatic SC", "PRO.ХИНКАЛИ"),
    "rybi": D("poster", "nofish", "#0f0a0a", "#f3ebdd", "#c1121f", "#c9a45c", "Yeseva One", "РЫБЫ НЕТ", "", 400),
    "ryumochnaya_kulturno_korotko": D("seal", "shot", "#d02c2c", "#ffffff", "#ffd2d2", "#ffffff", "Alegreya", "КУЛЬТУРНО", "КОРОТКО", ring="#ffffff"),
    "sadu": D("frame", "apple", "#7d8f69", "#b4532a", "#f6ece2", "#f6ece2", "Yeseva One", "SADU", "", 400),
    "serb_ya": D("seal", "grill", "#2f3a4f", "#eceef1", "#d02c2c", "#eceef1", "Bitter", "СЕРБ Я", "КАФАНА", ring="#d02c2c"),
    "shokunin": D("poster", "knife", "#efe8dc", "#0c0b0b", "#d0202f", "#0c0b0b", "Noto Serif", "SHOKUNIN", "職人"),
    "son_krasnoy_pandy": D("poster", "panda", "#fdf1ee", "#b0574b", "#3a2320", "#3a2320", "Yeseva One", "Сон Красной", "ПАНДЫ", 400),
    "syrvin": D("poster", "cheese", "#b0574b", "#f5c84c", "#3a2320", "#fff8f6", "Prata", "СЫРВИН", "", 400),
    "tak_sebe_lyudi": D("poster", "meh", "#f2b01e", "#1b2a4a", "#1b2a4a", "#1b2a4a", "Russo One", "ТАК СЕБЕ", "ЛЮДИ", 400),
    "teburasi": D("poster", "lantern", "#1c2541", "#d8371f", "#f2b632", "#f6ecd8", "Russo One", "ТЕБУРАСИ", "", 400),
    "terra_mare": D("frame", "olive", "#0d6e8f", "#ffffff", "#f2a541", "#ffffff", "Cormorant", "TERRA&MARE", "", 600),
    "udacha": D("seal", "horseshoe", "#0e1f1a", "#d4af5a", "#3fb58c", "#eee6cf", "Tenor Sans", "УДАЧА", "БИЛЬЯРД", 400, ring="#3fb58c"),
    "uye_bar": D("neon", "text:УЕ!", "#120a22", "#ff4fa3", "#38e0ff", "#38e0ff", "Rubik Mono One", "БАР", "", 400),
    "volga": D("frame", "decanter", "#172236", "#eef2f7", "#f0b429", "#eef2f7", "PT Serif", "ВОЛГА", "НАСТОЕЧНАЯ"),
    "vova": D("neon", "disco", "#150a26", "#c6f432", "#ff3d9a", "#ff7a1a", "Unbounded", "ВОВА'З", "", 800),
    "ya_won": D("poster", "hotpot", "#d8232a", "#0c0c0c", "#f5f0ea", "#f5f0ea", "Oswald", "YA WON"),
    "yellowfin_by_bluefin": D("poster", "tuna", "#111111", "#f5f5f2", "#e6c229", "#e6c229", "Unbounded", "YELLOWFIN"),
    "zag": D("poster", "axe", "#0c0f0b", "#8fd21e", "#b3151b", "#e9e2c8", "Ruslan Display", "ЗАГ-ЗАГ", "", 400),
    "zhasmin_belyayevo": D("poster", "jasmine", "#227a68", "#ffffff", "#e8b34a", "#ffffff", "Philosopher", "ЖАСМИН"),
    "zolotoy_kolos": D("seal", "wheat", "#5d6b2f", "#e7b34a", "#c98a2b", "#f2ecdc", "Merriweather", "ЗОЛОТОЙ", "КОЛОС", ring="#e7b34a"),
}


def motif_svg(d, x, y, size):
    m = d["motif"]
    if m.startswith("text:"):  # само название и есть рисунок (неон)
        t = H.escape(m[5:])
        return (f'<text class="fit" data-max="{size * 0.95:.0f}" x="{x + size / 2}" y="{y + size * 0.66}" text-anchor="middle" '
                f'font-size="{size * 0.5:.0f}" fill="{d["fg"]}" style="font-family:\'{d["font"]}\';font-weight:{d["w"]}">{t}</text>')
    return f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 100 100" style="color:{d["fg"]}" fill="currentColor">{MOTIFS[m]}</svg>'


def label_svg(d, y, max_w, size, cls="fit", text=None, color=None, spacing=0, weight=None):
    t = H.escape(text if text is not None else d["label"])
    st = f"font-family:'{d['font']}';font-weight:{weight or d['w']};letter-spacing:{spacing}px" + (";font-style:italic" if d["it"] else "")
    return (f'<text class="{cls}" data-max="{max_w}" x="256" y="{y}" text-anchor="middle" font-size="{size}" '
            f'fill="{color or d["ink"]}" style="{st}">{t}</text>')


def icon_svg(key, d, mask=False):
    L = d["layout"]
    body = []
    if L == "poster":
        body.append(motif_svg(d, 116, 46 if d["sub"] else 56, 280))
        if d["sub"]:
            body.append(label_svg(d, 418, 430, 78))
            body.append(label_svg(d, 466, 400, 28, text=d["sub"], color=d["fg2"] if d["fg2"] != d["bg"] else d["ink"], spacing=4, weight=600))
        else:
            body.append(label_svg(d, 446, 430, 84))
    elif L == "neon":
        body.append(f'<g filter="url(#glow-{key})">{motif_svg(d, 116, 52, 280)}</g>')
        body.append(f'<g filter="url(#glow-{key})">{label_svg(d, 446, 420, 76)}</g>')
    elif L == "frame":
        if not mask:  # под круглой маской уголки рамки обрезались бы
            body.append(f'<rect x="34" y="34" width="444" height="444" rx="18" fill="none" stroke="{d["fg2"]}" stroke-width="4"/>')
            body.append(f'<rect x="48" y="48" width="416" height="416" rx="10" fill="none" stroke="{d["fg2"]}" stroke-opacity=".45" stroke-width="2"/>')
        body.append(motif_svg(d, 146, 82, 220))
        body.append(label_svg(d, 380 if d["sub"] else 392, 360, 68))
        if d["sub"]:
            body.append(label_svg(d, 426, 340, 24, text=d["sub"], color=d["fg2"], spacing=5, weight=600))
    elif L == "seal":
        r = d["ring"]
        body.append(f'<circle cx="256" cy="256" r="214" fill="none" stroke="{r}" stroke-width="12"/>')
        body.append(f'<circle cx="256" cy="256" r="190" fill="none" stroke="{r}" stroke-width="3"/>')
        body.append(f'<path id="top-{key}" d="M106 256a150 150 0 0 1 300 0" fill="none"/><path id="bot-{key}" d="M84 256a172 172 0 0 0 344 0" fill="none"/>')
        st = f"font-family:'{d['font']}';font-weight:{d['w']}"
        body.append(f'<text class="arc" data-arc="400" font-size="50" fill="{d["ink"]}" style="{st};letter-spacing:4px"><textPath href="#top-{key}" startOffset="50%" text-anchor="middle">{H.escape(d["label"])}</textPath></text>')
        if d["sub"]:
            body.append(f'<text class="arc" data-arc="260" font-size="34" fill="{d["ink"]}" style="{st};letter-spacing:6px"><textPath href="#bot-{key}" startOffset="50%" text-anchor="middle" dominant-baseline="hanging">{H.escape(d["sub"])}</textPath></text>')
        for cx in (78, 434):
            body.append(f'<circle cx="{cx}" cy="256" r="7" fill="{r}"/>')
        body.append(motif_svg(d, 166, 176, 180))
    inner = "".join(body)
    if mask:  # всё важное — внутри круга 80%
        inner = f'<g transform="translate(51.2 51.2) scale(.8)">{inner}</g>'
    defs = (f'<defs><filter id="glow-{key}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="9" result="b"/>'
            f'<feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512" '
            f'style="--cut:{d["bg"]};--fg2:{d["fg2"]};display:block">{defs}<rect width="512" height="512" fill="{d["bg"]}"/>{inner}</svg>')


FIT_JS = """
document.fonts.ready.then(() => {
  document.querySelectorAll('text.fit').forEach((t) => {
    const max = +t.dataset.max; let s = parseFloat(t.getAttribute('font-size'));
    while (t.getComputedTextLength() > max && s > 10) { s -= 1; t.setAttribute('font-size', s); }
  });
  document.querySelectorAll('text.arc').forEach((t) => {
    const max = +t.dataset.arc; let s = parseFloat(t.getAttribute('font-size'));
    while (t.getComputedTextLength() > max && s > 12) { s -= 1; t.setAttribute('font-size', s); }
  });
  document.body.dataset.ready = '1';
});
"""


def render(keys, out_dir):
    fams = sorted({DESIGN[k]["font"] for k in keys})
    links = "".join(f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={f.replace(" ", "+")}&display=block">' for f in fams)
    # жирные начертания отдельно: если у шрифта такого нет, ломается только эта ссылка
    links += "".join(f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={DESIGN[k]["font"].replace(" ", "+")}:'
                     f'{"ital," if DESIGN[k]["it"] else ""}wght@{"1," if DESIGN[k]["it"] else ""}{DESIGN[k]["w"]}&display=block">'
                     for k in keys if DESIGN[k]["w"] != 400 or DESIGN[k]["it"])
    cols = 5
    tiles = []
    for i, k in enumerate(keys):
        for j, mask in enumerate((False, True)):
            n = i * 2 + j
            tiles.append(f'<div style="position:absolute;left:{(n % cols) * 512}px;top:{(n // cols) * 512}px">{icon_svg(k, DESIGN[k], mask)}</div>')
    rows = (len(keys) * 2 + cols - 1) // cols
    page = (f'<!doctype html><html><head><meta charset="utf-8">{links}<style>html,body{{margin:0;background:#fff}}</style></head>'
            f'<body>{"".join(tiles)}<script>{FIT_JS}</script></body></html>')
    tmp = Path(tempfile.mkdtemp())
    (tmp / "sheet.html").write_text(page, encoding="utf-8")
    shot = tmp / "sheet.png"
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    f"--window-size={cols * 512},{rows * 512}", "--virtual-time-budget=20000",
                    f"--screenshot={shot}", (tmp / "sheet.html").as_uri()], check=True, capture_output=True, timeout=180)
    sheet = Image.open(shot).convert("RGB")
    for i, k in enumerate(keys):
        crops = []
        for j in (0, 1):
            n = i * 2 + j
            x, y = (n % cols) * 512, (n // cols) * 512
            crops.append(sheet.crop((x, y, x + 512, y + 512)))
        icon, maskable = crops
        d = out_dir(k)
        icon.save(d / "icon-512.png", optimize=True)
        icon.resize((192, 192), Image.LANCZOS).save(d / "icon-192.png", optimize=True)
        icon.resize((180, 180), Image.LANCZOS).save(d / "apple-touch-icon.png", optimize=True)
        maskable.save(d / "icon-maskable-512.png", optimize=True)
        fav = icon.resize((64, 64), Image.LANCZOS)
        m = Image.new("L", (64, 64), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, 63, 63], radius=14, fill=255)
        f = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        f.paste(fav, (0, 0), m)
        f.save(d / "favicon.png", optimize=True)
    return sheet


def main():
    keys = sys.argv[1:] or sorted(DESIGN)
    missing = [k for k in keys if k not in DESIGN]
    if missing:
        sys.exit(f"нет дизайна иконки: {missing} — добавьте в DESIGN")
    render(keys, lambda k: SITES / k)
    print("иконки:", len(keys))


if __name__ == "__main__":
    main()
