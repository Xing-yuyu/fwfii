#!/usr/bin/env python
"""
测试 FiiExporter — 多机 .fii 官方项目导出
==========================================
完整工作流:
  1. MultiPlan     — 统一脚本 → per-drone .py + .ls + project.json
  2. FiiExporter   — per-drone .py → .fii 官方项目
  3. FiiExporter.load()    — 读取 .fii 验证
  4. SwarmProject.load()   — SwarmProject 读取验证

用法:
    python test/test_fii_export/test_fii_export.py
"""
from __future__ import division, absolute_import, print_function

import io
import os
import sys

# 确保项目根目录在 path 中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'output')


def banner(title):
    """打印阶段标题"""
    w = 60
    print()
    print('=' * w)
    print('  %s' % title)
    print('=' * w)
    print()


def check(ok, msg):
    """简单的断言"""
    status = 'PASS' if ok else 'FAIL'
    print('  [%s] %s' % (status, msg))
    return ok


# ═══════════════════════════════════════════════════════
# Step 1: MultiPlan — 统一脚本 → per-drone .py + .ls
# ═══════════════════════════════════════════════════════
def step1_multiplan():
    banner('Step 1: MultiPlan.build() → per-drone 脚本 + .ls')

    from fwfii.offline_multi import MultiPlan

    mp = MultiPlan()
    mp.add_drone(98101, pos=(100, 100))
    mp.add_drone(98102, pos=(460, 100))
    mp.add_drone(98103, pos=(280, 460))
    mp.set_carpet(560)

    unified = os.path.join(SCRIPT_DIR, 'triangle_unified.py')
    mp.build(unified, OUTPUT_DIR)

    # 验证输出
    all_ok = True
    for uavid in [98101, 98102, 98103]:
        py_path = os.path.join(OUTPUT_DIR, 'scripts', 'drone_%d.py' % uavid)
        ls_path = os.path.join(OUTPUT_DIR, '%d.ls' % uavid)
        all_ok &= check(os.path.exists(py_path),
                        'per-drone .py: drone_%d.py' % uavid)
        all_ok &= check(os.path.exists(ls_path),
                        '.ls 编译文件: %d.ls' % uavid)

    json_path = os.path.join(OUTPUT_DIR, 'project.json')
    all_ok &= check(os.path.exists(json_path), 'project.json')

    return all_ok


# ═══════════════════════════════════════════════════════
# Step 2: FiiExporter — per-drone .py → .fii 官方项目
# ═══════════════════════════════════════════════════════
def step2_fii_export():
    banner('Step 2: FiiExporter → .fii 官方项目')

    from fwfii import FiiExporter

    scripts_dir = os.path.join(OUTPUT_DIR, 'scripts')
    fii_dir = os.path.join(OUTPUT_DIR, 'fii_project')

    fii = FiiExporter('triangle_show')
    fii.add_drone(98101,
                  os.path.join(scripts_dir, 'drone_98101.py'),
                  pos=(100, 100))
    fii.add_drone(98102,
                  os.path.join(scripts_dir, 'drone_98102.py'),
                  pos=(460, 100))
    fii.add_drone(98103,
                  os.path.join(scripts_dir, 'drone_98103.py'),
                  pos=(280, 460))
    fii.set_carpet(560)

    fii.info()
    print()
    fii.build(fii_dir)

    # 验证输出结构
    all_ok = True

    # 顶层文件
    all_ok &= check(os.path.exists(os.path.join(fii_dir, 'triangle_show.fii')),
                    'triangle_show.fii 项目清单')
    actions_dir = os.path.join(fii_dir, '动作组')
    all_ok &= check(os.path.isdir(actions_dir),
                    '动作组/ 目录')
    all_ok &= check(os.path.exists(os.path.join(actions_dir, 'checksums.xml')),
                    'checksums.xml')

    # 每个无人机的 webCodeAll.py + webCodeAll.xml
    for i, uavid in enumerate([98101, 98102, 98103], 1):
        ag_dir = os.path.join(actions_dir, '动作组%d' % i)
        py_path = os.path.join(ag_dir, 'webCodeAll.py')
        xml_path = os.path.join(ag_dir, 'webCodeAll.xml')

        all_ok &= check(os.path.exists(py_path),
                        '动作组%d/webCodeAll.py (UAVID=%d)' % (i, uavid))
        all_ok &= check(os.path.exists(xml_path),
                        '动作组%d/webCodeAll.xml (UAVID=%d)' % (i, uavid))

        # 检查 .py 内容
        if os.path.exists(py_path):
            with io.open(py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            all_ok &= check('Start()' in content,
                            '  包含 Start() 入口')
            all_ok &= check('inittime(' in content,
                            '  包含 inittime() 时间块')
            all_ok &= check('f1' in content,
                            '  使用 f1 作为飞行对象')

    return all_ok, fii_dir


# ═══════════════════════════════════════════════════════
# Step 3: 展示生成的 webCodeAll.py 内容
# ═══════════════════════════════════════════════════════
def step3_show_content(fii_dir):
    banner('Step 3: 查看生成的 webCodeAll.py (各无人机前 10 行)')

    actions_dir = os.path.join(fii_dir, '动作组')
    for i in [1, 2, 3]:
        py_path = os.path.join(actions_dir, '动作组%d' % i, 'webCodeAll.py')
        print('  ── 动作组%d ──' % i)
        with io.open(py_path, 'r', encoding='utf-8') as f:
            for j, line in enumerate(f):
                if j >= 10:
                    break
                print('    %s' % line.rstrip())
        print()

    # 展示 .fii XML
    fii_xml = os.path.join(fii_dir, 'triangle_show.fii')
    print('  ── triangle_show.fii ──')
    with io.open(fii_xml, 'r', encoding='utf-8') as f:
        print(f.read())


# ═══════════════════════════════════════════════════════
# Step 4: FiiExporter.load() — 读取验证
# ═══════════════════════════════════════════════════════
def step4_fii_load(fii_dir):
    banner('Step 4: FiiExporter.load() → 读取 .fii 验证')

    from fwfii import FiiExporter

    result = FiiExporter.load(fii_dir)
    all_ok = True

    all_ok &= check(result['project_name'] == 'triangle_show',
                    '项目名称: triangle_show')
    all_ok &= check(result['device'] == 'F600',
                    '设备类型: F600')
    all_ok &= check(len(result['drones']) == 3,
                    '无人机数量: 3')

    expected = [
        (98101, 100, 100),
        (98102, 460, 100),
        (98103, 280, 460),
    ]
    for i, (uavid, x, y) in enumerate(expected):
        d = result['drones'][i]
        all_ok &= check(d['uavid'] == uavid,
                        '  UAVID=%d' % uavid)
        all_ok &= check(d['pos'] == (x, y),
                        '  pos=(%d,%d)' % (x, y))
        all_ok &= check(os.path.exists(d['webcodeall_py']),
                        '  webCodeAll.py 存在')

    print()
    print('  FiiExporter.load() 返回:')
    print('    项目名: %s' % result['project_name'])
    print('    设备:   %s' % result['device'])
    print('    场地:   %d x %d cm' % (result['field'][0], result['field'][1]))
    for d in result['drones']:
        print('    UAVID=%d  pos=(%d,%d)  ag=%d' %
              (d['uavid'], d['pos'][0], d['pos'][1], d['action_group']))

    return all_ok


# ═══════════════════════════════════════════════════════
# Step 5: SwarmProject.load() — 完整读取
# ═══════════════════════════════════════════════════════
def step5_swarm_load(fii_dir):
    banner('Step 5: SwarmProject.load() → 读取 .fii')

    from fwfii import SwarmProject

    swarm = SwarmProject()
    swarm.load(fii_dir)
    swarm.info()

    all_ok = True
    all_ok &= check(len(swarm.drones) == 3,
                    'SwarmProject 加载 3 架无人机')

    return all_ok


# ═══════════════════════════════════════════════════════
# main
# ═══════════════════════════════════════════════════════
def main():
    print()
    print('╔' + '═' * 58 + '╗')
    print('║  FiiExporter 测试 — 多机 .fii 官方项目导出' + ' ' * 15 + '║')
    print('║  3 机三角编队 (560cm / 6m 毯)' + ' ' * 25 + '║')
    print('╚' + '═' * 58 + '╝')

    results = []

    results.append(('MultiPlan 构建', step1_multiplan()))
    ok2, fii_dir = step2_fii_export()
    results.append(('FiiExporter 导出', ok2))
    step3_show_content(fii_dir)
    results.append(('FiiExporter.load()', step4_fii_load(fii_dir)))
    results.append(('SwarmProject.load()', step5_swarm_load(fii_dir)))

    # ── 总结 ──
    print()
    print('=' * 60)
    print('  测试总结')
    print('=' * 60)
    all_pass = True
    for name, ok in results:
        status = 'PASS' if ok else 'FAIL'
        print('  [%s] %s' % (status, name))
        if not ok:
            all_pass = False
    print()

    if all_pass:
        print('  全部测试通过!')
        print()
        print('  输出目录: %s/' % os.path.abspath(OUTPUT_DIR))
        print('  .fii 项目: %s/' % os.path.abspath(fii_dir))
        print()
        print('  可导入官方炫舞软件查看:')
        print('    %s' % os.path.join(os.path.abspath(fii_dir),
                                       'triangle_show.fii'))
    else:
        print('  部分测试失败，请检查上方 [FAIL] 项')

    return 0 if all_pass else 1


if __name__ == '__main__':
    sys.exit(main())
