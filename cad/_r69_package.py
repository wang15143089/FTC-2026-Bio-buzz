# -*- coding: utf-8 -*-
"""R69 print package assembler (read-only inputs, one delivery folder out).

In : cad/output/_r69_parts (5 new STEP + parts_index.json + fasteners.json, rest re-used
     from cad/output/_r66_parts)
     cad/output/_r69_plate (8 plate STEP + 8 previews + overview + plates_index.json)
Out: deliverables/R69_print_package/
"""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS_DIR = ROOT / 'cad' / 'output' / '_r69_parts'
OLD_PARTS = ROOT / 'cad' / 'output' / '_r66_parts'
PLATE_DIR = ROOT / 'cad' / 'output' / '_r69_plate'
OUT_DIR = ROOT / 'deliverables' / 'R69_print_package'
BT = chr(96)

GROUP_LABEL = {
    'r69': 'R69 新件（拆件 / 耳片 / 整轨）',
    'r62+r69': 'R62 打印件（未改）',
    'r65+r69': 'R65 件（未改）',
    'frame+r69': '主体 lump（DEC-0063 拆分，未改）',
}


def c(t):
    return BT + t + BT


def dims(o, key):
    v = o.get(key) or [0, 0, 0]
    return ' x '.join('%.1f' % x for x in v)


def main():
    parts = json.loads((PARTS_DIR / 'parts_index.json').read_text(encoding='utf-8'))
    plates = json.loads((PLATE_DIR / 'plates_index.json').read_text(encoding='utf-8'))
    fast = json.loads((PARTS_DIR / 'fasteners.json').read_text(encoding='utf-8'))

    objects = parts['objects']
    names = [o['object'] for o in objects]
    packed = [o['object'] for p in plates['plates'] for o in p['objects']]
    dup = sorted({n for n in packed if packed.count(n) > 1})
    missing = sorted(set(names) - set(packed))
    extra = sorted(set(packed) - set(names))
    if dup or missing or extra:
        raise SystemExit('mismatch dup=%s missing=%s extra=%s' % (dup, missing, extra))

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    for sub in ('parts', 'plates', 'previews'):
        (OUT_DIR / sub).mkdir(parents=True)
    for o in objects:
        f = PARTS_DIR / o['file']
        if not f.exists():
            f = OLD_PARTS / o['file']
        shutil.copy2(f, OUT_DIR / 'parts' / o['file'])
    for p in plates['plates']:
        shutil.copy2(PLATE_DIR / p['step'], OUT_DIR / 'plates' / p['step'])
    for png in sorted(PLATE_DIR.glob('*.png')):
        shutil.copy2(png, OUT_DIR / 'previews' / png.name)
    for f in ('parts_index.json', 'fasteners.json'):
        shutil.copy2(PARTS_DIR / f, OUT_DIR / f)
    shutil.copy2(PLATE_DIR / 'plates_index.json', OUT_DIR / 'plates_index.json')

    groups = {}
    for o in objects:
        groups[o['group']] = groups.get(o['group'], 0) + 1
    st = {i['tag']: i for i in fast['items']}

    L = []
    add = L.append
    add('# R69 打印包（POLLEN 版）')
    add('')
    add('> 版本：**R69 修订**（DEC-0076 / V-0076）。相对 R67 三处改动：')
    add('> 1. 最大的 ' + c('frameP_1_rear_lower') + '（277 x 183 x 304，占一板还装不下支架）按 **y = ±68**（侧板内表面）')
    add('>    拆成 3 件：' + c('side_plate_left') + ' / ' + c('side_plate_right') + ' / ' + c('shroud_tray_mid')
        + '，切割体积守恒 ΔV = 0.000 mm3。')
    add('> 2. 3 件之间用 **8 处 M3 螺栓（每侧 4 处）+ 环氧胶** 固定：外罩壁与侧板内面之间本来就有 11 mm 空腔，')
    add('>    从外罩壁咬入 3 mm 做一个 12 x 10 的耳片桥到 |y| = 67.8（对侧板留 0.2 mm 胶缝），Ø3.4 孔贯通耳片 + 侧板。')
    add('> 3. 滑轨改 **方案 C**：每侧一根 **380 mm 整轨**' + c('base_rail_+72') + ' / ' + c('base_rail_-72')
        + '（前段 + 后段合成），')
    add('>    删除 ' + c('rail_splice_plate_+72') + ' / ' + c('rail_splice_plate_-72') + '（2 块搭板）、跨轨筋与 4 x M3x30。')
    add('')
    add('单位 mm。所有件均为独立实体，板内无重叠、无干涉。')
    add('')
    add('## 目录')
    add('- ' + c('parts/') + ' — %d 个独立打印件 STEP（单件补打 / 替换用）' % len(objects))
    add('- ' + c('plates/') + ' — %d 块拼板 STEP，**直接打印这几个文件即可**，件已按最终姿态与位置放好' % len(plates['plates']))
    add('- ' + c('previews/') + ' — 每板俯视预览 + 全包总览图')
    add('- ' + c('parts_index.json') + ' / ' + c('plates_index.json') + ' / ' + c('fasteners.json') + ' — 清单、排版与紧固记录，可复算')
    add('')
    add('## 件数')
    add('合计 **%d 件**，分 **%d 块板**打印。' % (len(objects), len(plates['plates'])))
    add('')
    add('| 来源 | 件数 | 说明 |')
    add('| --- | --- | --- |')
    for g in ('r69', 'r62+r69', 'r65+r69', 'frame+r69'):
        if g in groups:
            add('| ' + c(g) + ' | %d | %s |' % (groups[g], GROUP_LABEL[g]))
    add('')
    add('## 拆件与紧固（R69 核心）')
    add('')
    add('| 工位 | x | z | 螺栓 | 夹持长度 | 侧板厚 | 螺母座 |')
    add('| --- | --- | --- | --- | --- | --- | --- |')
    for tag in ('A', 'D', 'B', 'C'):
        i = st[tag]
        add('| %s（左右各一） | %.0f | %.0f | %s | %.1f | %.1f | 外罩壁内表面 |'
            % (tag, i['x'], i['z'], i['bolt'], i['clamp_mm'], i['plate_mm']))
    add('')
    add('- 排布：A 在最前下方（16 mm 厚的前下法兰上），D / B / C 沿侧板上缘向后依次布置，覆盖面尽可能大。')
    add('- 装配：螺栓头 + 垫圈在**侧板外侧**（可及面），垫圈 + 六角螺母在**外罩壁内表面**，每螺栓 2 个平垫圈。')
    add('- 胶：所有贴合面（耳片 / 外罩壁 / 侧板内面）涂双组分环氧，0.2 mm 胶缝。')
    add('- 不用扎带：扎带要在侧板上开槽（削弱 4 mm 薄壁），对已螺栓 + 粘接的接头没有额外收益，反而增加打印与装配步骤。')
    add('- 8 处耳片均在真实实体上复核：咬入体积 188.6 ~ 651.6 mm3，孔贯通后无残留（< 1 mm3），')
    add('  对其它 %d 个件的干涉检查为 none。' % (len(objects) - 5))
    add('')
    add('## 打印板')
    add('')
    add('| 板 | 件数 | 占用 XY (mm) | 最大高度 (mm) | 填充 |')
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
    add('## 摆放规则')
    add('1. 每件在「64 个 90 度姿态」+「该件每个平面法向朝下的姿态」里选**离床最矮**者，同高时优先占地更小。')
    add('2. R69 新增：若以上姿态都放不进板（长件），再按 30 / 35 / 40 / 45 / 50 / 55 / 60 度**板内斜放**重试；')
    add('   并且判据补上了「高度 <= 325 mm」，避免长件立着摆（H 380 超行程）。')
    add('   两根 380 mm 整轨因此各自 45 度斜放，占地 287.1 x 287.1，p2 单独一板。')
    add('3. 板内允许再转 90 度；装箱用 MaxRects best-area-fit + 160 起点多起点搜索 + 收尾合并修复。')
    add('4. 3 件拆件各占一板（' + c('shroud_tray_mid') + ' 248 x 233 x 136 与 ' + c('paddle_rotor')
        + ' 合板；两块侧板 262 x 284 各配小件）。')
    add('')
    add('## 逐件清单')
    add('')
    for p in plates['plates']:
        add('### p%d — %d 件，最大高度 %.1f mm' % (p['plate'], p['n_objects'], p['max_height_mm']))
        add('')
        add('| 件 | 来源 | 原始外形 (mm) | 放平后占地 (mm) | 高 (mm) | 放平姿态 | 板内 XY (mm) |')
        add('| --- | --- | --- | --- | --- | --- | --- |')
        for o in sorted(p['objects'], key=lambda x: -x['volume_mm3']):
            turn = ' +90' if o.get('in_plane_90_deg_turn') else ''
            pz = o.get('pose', {})
            if pz.get('type') == 'axis':
                sit = 'X%g/Y%g/Z%g' % tuple(pz['angles_deg_XYZ'])
            else:
                sit = '面 %s 朝下, 绕 %s 转 %g' % (
                    ','.join('%.2f' % v for v in pz['face_normal']),
                    ','.join('%g' % v for v in pz['rot_axis']), pz['rot_deg'])
            if 'in_plane_deg' in pz:
                sit += ', 板内斜 %g 度' % pz['in_plane_deg']
            add('| ' + o['object'] + ' | ' + o['group'] + ' | ' + dims(o, 'as_drawn_dims_mm')
                + ' | %.1f x %.1f | %.1f | %s%s | %.1f, %.1f |'
                % (o['footprint_mm'][0], o['footprint_mm'][1], o['height_mm'],
                   sit, turn, o['bed_xy_mm'][0], o['bed_xy_mm'][1]))
        add('')
    add('## 打印注意')
    add('- 直接打印 ' + c('plates/') + ' 里的 STEP；不要改动件在板上的姿态，一改就破坏贴床面朝下的平放条件；')
    add('  两根轨道是 45 度斜放，不要「扶正」。')
    add('- ' + c('side_plate_left') + ' / ' + c('side_plate_right') + ' 摊平后 262 x 284，接近 H2D 可用区 315 x 310，')
    add('  请确认板面清洁、首层附着可靠。')
    add('- 20 个小件 ' + c('carriage_clamp_seat_*') + '（8 x 8 x 6）集中在同一板，便于整体清件。')
    add('- 耳片是外罩件上的小凸台，打印时保证该面冷却，避免翘边影响 0.2 mm 胶缝。')
    add('')
    add('## 已知限制 / TBD')
    add('- 螺母座在外罩内表面，装配时需在内腔放螺母（TBD：确认实际装配顺序与扳手空间）。')
    add('- 胶缝 0.2 mm 为设计值（ASSUMED）；实际打印件表面误差按 1 mm 内接受。')
    add('')
    add('## 复算')
    add('')
    add('    python cad/_r69_build.py     # 拆 3 件 + 耳片 + 孔 + 整轨 -> cad/output/_r69_parts/')
    add('    python cad/_r69_view.py      # 拆解 / 关节剖面 / 轨道对比图')
    add('    python cad/_r69_plate.py     # 排版 -> cad/output/_r69_plate/')
    add('    python cad/_r69_package.py   # 汇总到 deliverables/R69_print_package/')
    add('')

    (OUT_DIR / 'PRINT_README.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('package -> %s' % OUT_DIR)
    print('parts=%d plates=%d previews=%d groups=%s'
          % (len(list((OUT_DIR / 'parts').iterdir())), len(list((OUT_DIR / 'plates').iterdir())),
             len(list((OUT_DIR / 'previews').iterdir())), groups))


if __name__ == '__main__':
    main()
