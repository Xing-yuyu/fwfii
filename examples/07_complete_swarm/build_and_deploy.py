#!/usr/bin/env python
"""
完整蜂群项目工作流 — 三角编队表演
=====================================
演示完整的多机离线任务流程:

  1. MultiPlan.build()       统一脚本 → 自动拆分 + .ls + project.json
  2. SwarmProject.compile()  编译 per-drone .py (可选，MultiPlan 已生成 .ls)
  3. FiiExporter             导出 .fii 项目 (可导入官方炫舞软件)
  4. SwarmProject.deliver()  上传 .ls 到所有无人机
  5. SwarmProject.launch()   同步起飞 + 倒计时 + 音乐

用法:
    python examples/07_complete_swarm/build_and_deploy.py           # 全流程 (skip upload)
    python examples/07_complete_swarm/build_and_deploy.py build     # 仅构建
    python examples/07_complete_swarm/build_and_deploy.py video     # 构建 + 导出 .fii
    python examples/07_complete_swarm/build_and_deploy.py full      # 包含上传 (需连无人机)
"""
from __future__ import division, absolute_import, print_function

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


def step1_multiplan_build():
    """Step 1: MultiPlan — 统一脚本 → 自动拆分 + .ls + 项目结构"""
    banner('STEP 1: MultiPlan.build() — 统一脚本 → 项目结构')

    from fwfii.offline_multi import MultiPlan

    mp = MultiPlan()
    mp.add_drone(98101, pos=(20, 20))
    mp.add_drone(98102, pos=(60, 20))
    mp.add_drone(98103, pos=(40, 60))
    mp.set_music('music.mp3')  # pyfii 仅支持 mp3/wav 导出视频音频
    mp.set_carpet(80)

    mp.info()

    unified_script = os.path.join(SCRIPT_DIR, 'triangle_formation.py')
    mp.build(unified_script, OUTPUT_DIR)

    print()
    print('  [OK] 项目结构已生成: %s/' % OUTPUT_DIR)
    print('    ├── project.json      — 项目元数据')
    print('    ├── scripts/           — 自动生成的 per-drone .py')
    print('    │   ├── drone_98101.py')
    print('    │   ├── drone_98102.py')
    print('    │   └── drone_98103.py')
    print('    ├── 98101.ls           — 编译好的二进制')
    print('    ├── 98102.ls')
    print('    └── 98103.ls')

    return mp


def step2_show_generated_scripts():
    """Step 2: 展示自动生成的 per-drone 脚本"""
    banner('STEP 2: 查看生成的 per-drone 脚本')

    scripts_dir = os.path.join(OUTPUT_DIR, 'scripts')
    for fname in sorted(os.listdir(scripts_dir)):
        if fname.endswith('.py'):
            fpath = os.path.join(scripts_dir, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            print('  ── %s ──' % fname)
            # 只显示前 5 条命令
            cmd_count = 0
            for line in lines:
                stripped = line.strip()
                if '(' in stripped and not stripped.startswith('#') \
                   and not stripped.startswith('from') and not stripped.startswith('f1'):
                    print('    %s' % stripped)
                    cmd_count += 1
                    if cmd_count >= 5:
                        break
            print('    ... (共 %d 条命令)' % sum(
                1 for l in lines if '(' in l and not l.strip().startswith('#')
                and not l.strip().startswith('from')))
            print()


def step3_export_fii():
    """Step 3: FiiExporter — 导出 .fii 项目 (可导入官方炫舞软件)"""
    banner('STEP 3: FiiExporter — 导出 .fii 项目')

    try:
        from fwfii import FiiExporter

        scripts_dir = os.path.join(OUTPUT_DIR, 'scripts')
        fii_dir = os.path.join(SCRIPT_DIR, 'fii_export')

        fii = FiiExporter('triangle_formation')
        fii.add_drone(98101,
                      os.path.join(scripts_dir, 'drone_98101.py'),
                      pos=(20, 20))
        fii.add_drone(98102,
                      os.path.join(scripts_dir, 'drone_98102.py'),
                      pos=(60, 20))
        fii.add_drone(98103,
                      os.path.join(scripts_dir, 'drone_98103.py'),
                      pos=(40, 60))

        music_path = os.path.join(SCRIPT_DIR, 'music.mp3')
        if os.path.exists(music_path):
            fii.set_music(music_path)

        fii.set_field(80, 80, 250)  # 80cm 毯
        fii.info()
        print()
        fii.build(fii_dir)

        print()
        print('  [OK] .fii 项目已生成: %s/' % fii_dir)
        print('  可导入官方炫舞软件查看/编辑')

        return fii_dir

    except Exception as e:
        print('  [WARN] .fii 导出失败: %s' % e)
        import traceback
        traceback.print_exc()
        return None


def step4_swarm_compile():
    """Step 4: SwarmProject — 编译 per-drone .py → .ls"""
    banner('STEP 4: SwarmProject.compile() — 编译 per-drone 脚本')

    from fwfii import SwarmProject

    scripts_dir = os.path.join(OUTPUT_DIR, 'scripts')
    swarm = SwarmProject()
    swarm.add_drone(98101,
                    os.path.join(scripts_dir, 'drone_98101.py'),
                    pos=(20, 20))
    swarm.add_drone(98102,
                    os.path.join(scripts_dir, 'drone_98102.py'),
                    pos=(60, 20))
    swarm.add_drone(98103,
                    os.path.join(scripts_dir, 'drone_98103.py'),
                    pos=(40, 60))
    swarm.set_music(os.path.join(SCRIPT_DIR, 'music.mp3'))

    swarm.info()
    print()
    swarm.compile(OUTPUT_DIR)

    # 显示 .ls 文件
    print()
    for fname in sorted(os.listdir(OUTPUT_DIR)):
        if fname.endswith('.ls'):
            size = os.path.getsize(os.path.join(OUTPUT_DIR, fname))
            print('  %s  (%d bytes = %d 条命令)' %
                  (fname, size, size // 32 - 1))

    return swarm


def step5_deliver_and_launch(swarm):
    """Step 5: 上传 + 起飞 (需要无人机连接)"""
    banner('STEP 5: deliver + launch — 上传 + 同步起飞')

    print('  [!!] 此步骤需要无人机开机并连接 WiFi')
    print()
    print('  上传命令:')
    for uavid in [98101, 98102, 98103]:
        group = uavid // 1000
        num = uavid % 1000
        print('    deliver(%d, "%s", ip="192.168.%d.%d")' %
              (uavid, OUTPUT_DIR, group, num))
    print()
    print('  或使用 SwarmProject 一键上传 + 起飞:')
    print('    swarm.deliver()')
    print('    swarm.launch_with_music(countdown=5)')
    print()
    print('  手动执行:')
    print('    python -c "')
    print('      from fwfii import SwarmProject')
    print('      swarm = SwarmProject()')
    print('      swarm.add_drone(98101, \'scripts/drone_98101.py\', pos=(20,20))')
    print('      swarm.add_drone(98102, \'scripts/drone_98102.py\', pos=(60,20))')
    print('      swarm.add_drone(98103, \'scripts/drone_98103.py\', pos=(40,60))')
    print('      swarm.set_music(\'music.mp3\')')
    print('      swarm.deliver(\'%s\')' % OUTPUT_DIR)
    print('      swarm.launch_with_music(countdown=5)')
    print('    "')


# ============================================================
# 主入口
# ============================================================
def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'build'

    print()
    print('╔' + '═' * 58 + '╗')
    print('║  fwfii 完整蜂群项目 — 三角编队表演 (3 机)' + ' ' * 18 + '║')
    print('╠' + '═' * 58 + '╣')
    print('║  build  = 构建 + 拆分 + 编译 (默认)' + ' ' * 23 + '║')
    print('║  video  = 构建 + 导出 .fii 项目' + ' ' * 26 + '║')
    print('║  full   = 构建 + .fii + 上传 (需连无人机)' + ' ' * 14 + '║')
    print('╚' + '═' * 58 + '╝')
    print()
    print('  统一脚本: triangle_formation.py')
    print('  无人机:   98101 (低层) / 98102 (中层) / 98103 (高层)')
    print('  定位毯:   80cm')
    print('  音乐:     music.mp3 (祖海 — 好运来)')
    print('  总时长:   ~39s')
    print()

    try:
        # Step 1: MultiPlan 构建 (统一脚本 → 项目结构)
        mp = step1_multiplan_build()

        # Step 2: 展示生成的 per-drone 脚本
        step2_show_generated_scripts()

        if mode == 'video' or mode == 'full':
            # Step 3: 导出 .fii 项目
            step3_export_fii()

        # Step 4: SwarmProject 编译
        swarm = step4_swarm_compile()

        if mode == 'full':
            # Step 5: 上传 + 起飞
            step5_deliver_and_launch(swarm)
        else:
            # 显示后续手动命令
            step5_deliver_and_launch(swarm)

    except Exception as e:
        print()
        print('  [ERROR] %s' % e)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print()
    print('=' * 60)
    print('  完成!')
    print()
    if mode == 'video':
        print('  导入官方炫舞软件: fii_export/triangle_formation.fii')
    print('  项目输出: %s/' % OUTPUT_DIR)
    print('=' * 60)
    print()


if __name__ == '__main__':
    main()
