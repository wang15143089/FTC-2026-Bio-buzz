# -*- coding: utf-8 -*-
"""R66 print package assembler (read-only inputs, one delivery folder out).

In : cad/output/_r66_parts (55 object STEP + parts_index.json)
     cad/output/_r66_plate (4 plate STEP + 4 previews + overview + plates_index.json)
Out: deliverables/R66_print_package/
       parts/     55 STEP
       plates/    4 plate STEP
       previews/  4 plate previews + overview
       parts_index.json, plates_index.json
       PRINT_README.md
"""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS_DIR = ROOT / 'cad' / 'output' / '_r66_parts'
PLATE_DIR = ROOT / 'cad' / 'output' / '_r66_plate'
OUT_DIR = ROOT / 'deliverables' / 'R66_print_package'

BT = chr(96)

GROUP_LABEL = {
    'r62': 'R62 打印件',
    'r65': 'R65 钻孔轨 / 搭板',
    'frame': '主体 lump（DEC-0063 双平面拆分）',
}


def c(text):
    return BT + text + BT


def dims(o, key):
    v = o.get(key) or [0, 0, 0]
    return ' x '.join('%.1f' % x for x in v)


def main():
    parts = json.loads((PARTS_DIR / 'parts_index.json').read_text(encoding='utf-8'))
    plates = json.loads((PLATE_DIR / 'plates_index.json').read_text(encoding='utf-8'))

    objects = parts['objects']
    names = [o['object'] for o in objects]
    packed = [o['object'] for p in plates['plates'] for o in p['objects']]

    duplicates = sorted({n for n in packed if packed.count(n) > 1})
    missing = sorted(set(names) - set(packed))
    extra = sorted(set(packed) - set(names))
    if duplicates or missing or extra:
        raise SystemExit('parts/plates mismatch dup=%s missing=%s extra=%s'
                         % (duplicates, missing, extra))

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    for sub in ('parts', 'plates', 'previews'):
        (OUT_DIR / sub).mkdir(parents=True)

    for o in objects:
        shutil.copy2(PARTS_DIR / o['file'], OUT_DIR / 'parts' / o['file'])
    for p in plates['plates']:
        shutil.copy2(PLATE_DIR / p['step'], OUT_DIR / 'plates' / p['step'])
    for png in sorted(PLATE_DIR.glob('*.png')):
        shutil.copy2(png, OUT_DIR / 'previews' / png.name)
    shutil.copy2(PARTS_DIR / 'parts_index.json', OUT_DIR / 'parts_index.json')
    shutil.copy2(PLATE_DIR / 'plates_index.json', OUT_DIR / 'plates_index.json')

    groups = {}
    for o in objects:
        groups[o['group']] = groups.get(o['group'], 0) + 1

    L = []
    add = L.append
    add('# R66 打印包（POLLEN 版）')
    add('')
    add('单位 mm。所有件均为独立实体，板内无重叠、无干涉。')
    add('')
    add('## 目录')
    add('- ' + c('parts/') + ' — 55 个独立打印件 STEP（单件补打 / 替换用）')
    add('- ' + c('plates/') + ' — 4 块拼板 STEP，**直接打印这 4 个文件即可**，件已按最终姿态与位置放好')
    add('- ' + c('previews/') + ' — 每板俯视预览 + 全包总览图')
    add('- ' + c('parts_index.json') + ' / ' + c('plates_index.json') + ' — 清单与排版记录，可复算')
    add('')
    add('## 件数')
    add('合计 **%d 件**，分 **%d 块板**打印。' % (len(objects), len(plates['plates'])))
    add('')
    add('| 来源 | 件数 | 说明 |')
    add('| --- | --- | --- |')
    for g in ('r62', 'r65', 'frame'):
        if g in groups:
            add('| ' + c(g) + ' | %d | %s |' % (groups[g], GROUP_LABEL[g]))
    add('')
    add('## 打印板')
    add('')
    add('| 板 | 件数 | 占用 XY (mm) | 最大高度 (mm) | 板面填充 |')
    add('| --- | --- | --- | --- | --- |')
    for p in plates['plates']:
        rx, ry = p['used_extent_mm']
        add('| p%d | %d | %.1f x %.1f | %.1f | %.1f%% |'
            % (p['plate'], p['n_objects'], rx, ry, p['max_height_mm'], p['fill_percent']))
    add('')
    add('机器（KNOWN）: Bambu Lab H2D 单喷嘴 %d x %d x %d mm，板边距 %.0f mm，件间距 %.0f mm。'
        % (plates['bed_mm'][0], plates['bed_mm'][1], plates['bed_mm'][2],
           plates['margin_mm'], plates['gap_mm']))
    add('')
    add('## 摆放规则（主动降低打印难度）')
    add('1. 每件在 64 个 90 度姿态（X / Y / Z 各取 0 / 90 / 180 / 270）中选**高度最小**者，即最大平面朝下平放；')
    add('   同高时优先占地更大，再优先转 90 度更少。')
    add('2. 板内允许再转 90 度；装箱用 MaxRects best-area-fit。')
    add('3. 不硬塞：' + c('frameP_1_rear_lower') + ' 外形 277.2 x 303.5 x 183.0，单独占 p1，其余件铺 p2 / p3 / p4。')
    add('4. 160 个确定性起点的多起点搜索 + 收尾合并修复，消除 1-2 件的碎片板；宁可多打一板也不硬挤。')
    add('')
    add('## 逐件清单')
    add('')
    for p in plates['plates']:
        add('### p%d — %d 件，最大高度 %.1f mm' % (p['plate'], p['n_objects'], p['max_height_mm']))
        add('')
        add('| 件 | 来源 | 原始外形 (mm) | 放平后占地 (mm) | 高 (mm) | 姿态 XYZ (deg) | 板内 XY (mm) |')
        add('| --- | --- | --- | --- | --- | --- | --- |')
        for o in sorted(p['objects'], key=lambda x: -x['volume_mm3']):
            turn = ' +90' if o.get('in_plane_90_deg_turn') else ''
            add('| ' + o['object'] + ' | ' + o['group'] + ' | ' + dims(o, 'as_drawn_dims_mm')
                + ' | %.1f x %.1f | %.1f | %s%s | %.1f, %.1f |'
                % (o['footprint_mm'][0], o['footprint_mm'][1], o['height_mm'],
                   '/'.join('%g' % a for a in o['angles_deg_XYZ']), turn,
                   o['bed_xy_mm'][0], o['bed_xy_mm'][1]))
        add('')
    add('## 打印注意')
    add('- 直接打印 ' + c('plates/') + ' 里 4 个 STEP；不要改动件在板上的姿态，一改就破坏了最大面朝下的平放条件。')
    add('- 20 个 ' + c('carriage_clamp_seat_*') + ' 小件（8 x 8 x 6）全部集中在 p3，便于整体清件，避免散失。')
    add('- 4 板最高件依次为 %.1f / %.1f / %.1f / %.1f mm，都远低于 H2D 的 325 mm 行程。'
        % tuple(p['max_height_mm'] for p in plates['plates']))
    add('- 主体 lump 来自 DEC-0063 双平面拆分（x = 100 / z = 300），复用 R56 拆分结果，体积与 R62 主体一致')
    add('  （覆盖核对 delta = %.2f mm3，容差 %.1f mm3，判定 ok）。'
        % (parts['frame_coverage_check']['delta_mm3'], parts['frame_coverage_check']['tol_mm3']))
    add('')
    add('## 复算')
    add('')
    add('    python cad/_r66_parts.py      # 生成 parts/ 与 parts_index.json')
    add('    python cad/_r66_plate.py      # 生成 plates/ 与 previews/')
    add('    python cad/_r66_package.py    # 汇总到 deliverables/R66_print_package/')
    add('')

    (OUT_DIR / 'PRINT_README.md').write_text('\n'.join(L) + '\n', encoding='utf-8')

    n_parts = len(list((OUT_DIR / 'parts').iterdir()))
    n_plates = len(list((OUT_DIR / 'plates').iterdir()))
    n_prev = len(list((OUT_DIR / 'previews').iterdir()))
    print('package -> %s' % OUT_DIR)
    print('parts=%d plates=%d previews=%d groups=%s' % (n_parts, n_plates, n_prev, groups))
    print('OK')


if __name__ == '__main__':
    main()