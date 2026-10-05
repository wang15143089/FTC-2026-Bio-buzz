# -*- coding: utf-8 -*-
r"""R32 可视化：看拨杆把球送出、经飞轮发射飞出的全过程（NECTAR / POLLEN 任选）。

在仓库根目录（PowerShell）运行：

  # 1) 交互窗口（推荐；可用鼠标转视角）
  .\.venv-cad\Scripts\python.exe simulation/mujoco/view_r32.py
  .\.venv-cad\Scripts\python.exe simulation/mujoco/view_r32.py --ball pollen

  # 2) 直接存成 GIF（不需要显示器，双击就能看）
  .\.venv-cad\Scripts\python.exe simulation/mujoco/view_r32.py --gif cad/output/_t06_r32_launch_nectar.gif

交互窗口：左键拖=旋转，右键拖=平移，滚轮=缩放，空格=暂停/继续，Esc=关闭。
常用开关：--ball、--hold 起扫前等待秒数、--sweep 扫掠角度、--speed 慢放倍数、
          --gif 输出文件、--size 宽x高、--fps，另加 --no-loop 关闭自动重播。
"""
import argparse, math, sys, time
from collections import deque
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r32, mujoco                                    # noqa: E402
import opt_lib as ol                                  # noqa: E402

pv2 = ol.pv2
XC = r32.XC
BALLS = r32.BALLS
FEEDER_LOOKAT = (pv2.PADDLE_CX * 1e-3, 0.0, pv2.PADDLE_CZ * 1e-3)
TRAIL_RGBA = (1.0, 0.42, 0.10, 0.85)
EXIT_MM = pv2.polar(r32.R_IN, 142.0)                 # 出射唇口（mm）
EXIT_P = (EXIT_MM[0] * 1e-3, 0.0, EXIT_MM[1] * 1e-3)

def _aim(cam, d, bid, released):
    """出射前看机构；出射后自动把「出射点+球」框进画面，跟着球拉远。"""
    p = ball_pos(d, bid)
    if not released:
        cam.lookat[:] = FEEDER_LOOKAT
        cam.distance = 0.45
    else:
        cam.lookat[:] = 0.5 * (np.array(EXIT_P) + p)
        cam.distance = float(np.clip(2.2 * np.linalg.norm(p - np.array(EXIT_P)) + 0.35, 0.5, 3.0))
    cam.azimuth = 90.0          # 侧视：屏幕右 = +x（飞轮/发射在左，托板在右）
    cam.elevation = -8.0


class Policy:
    """索引式驱动：停 hold 秒 -> 连续扫掠 sweep 度 -> 释放（口径与 r32.run 相同）。"""

    def __init__(self, aid, jid, hold, sweep, w):
        self.aid, self.jid, self.hold, self.sweep, self.w = aid, jid, hold, sweep, w
        self.released = False

    def __call__(self, t, d):
        J = math.degrees(d.qpos[self.jid])
        if t < self.hold:
            d.ctrl[self.aid] = 0.0
        elif not self.released and J < self.sweep:
            d.ctrl[self.aid] = self.w
        else:
            self.released = True
            d.ctrl[self.aid] = 0.0

    def reset(self):
        self.released = False


def build_case(ball, hold, sweep):
    m, d, aid, jid, bid, ctrl, w = r32.build(xc=XC, **BALLS[ball.upper()])
    return m, d, aid, jid, bid, ctrl, w, d.qpos.copy(), Policy(aid, jid, hold, sweep, w)


def reset_state(d, q0, ctrl, pol):
    m = d.model
    mujoco.mj_resetData(m, d)
    d.qpos[:] = q0
    d.qvel[:] = 0.0
    d.ctrl[:] = [ctrl[0], ctrl[1], 0.0]
    d.act[:] = 0.0
    mujoco.mj_forward(m, d)
    pol.reset()


def ball_pos(d, bid):
    return d.xpos[bid].copy()


def ball_speed(d, bid):
    return float(np.linalg.norm(d.cvel[bid][3:]))


def add_trail(scn, pts, r=0.005):
    for p in pts:
        if scn.ngeom >= scn.maxgeom:
            break
        mujoco.mjv_initGeom(scn.geoms[scn.ngeom], mujoco.mjtGeom.mjGEOM_SPHERE,
                            np.array([r, 0.0, 0.0]), np.array(p, float),
                            np.eye(3).flatten(), np.array(TRAIL_RGBA, float))
        scn.ngeom += 1




def probe_exit_t(ball, hold, sweep):
    """先跑一遍拿到出射时刻，用来决定录制窗口长度。"""
    r = r32.run(xc=XC, hold=hold, sw=sweep, t_end=8.0, **BALLS[ball.upper()])
    e = r.get("exit") or {}
    if r.get("launched") and e.get("t") is not None:
        return float(e["t"]), float(e["speed_m_s"])
    return None, None


def run_gif(args):
    from PIL import Image
    w_px, h_px = (int(v) for v in args.size.lower().split("x"))
    m, d, aid, jid, bid, ctrl, w, q0, pol = build_case(args.ball, args.hold, args.sweep)
    t_exit, v_exit = (None, None) if args.no_probe else probe_exit_t(args.ball, args.hold, args.sweep)
    stop = 8.0 if t_exit is None else min(8.0, t_exit + args.extra)
    print("[%s] 录制到 t=%.2f s%s" % (args.ball.upper(), stop,
          "" if t_exit is None else "（出射 t=%.2f s，v=%.2f m/s）" % (t_exit, v_exit)), flush=True)
    reset_state(d, q0, ctrl, pol)
    renderer = mujoco.Renderer(m, height=h_px, width=w_px)
    cam = mujoco.MjvCamera()
    mujoco.mjv_defaultCamera(cam)
    cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    dt = m.opt.timestep
    k = max(1, int(round(1.0 / args.fps / dt)))
    trail, last_trail = deque(maxlen=300), -1.0
    frames, i = [], 0
    while d.time < stop:
        pol(d.time, d)
        mujoco.mj_step(m, d)
        i += 1
        if i % k:
            continue
        if d.time - last_trail >= 0.004:
            trail.append(ball_pos(d, bid))
            last_trail = d.time
        _aim(cam, d, bid, pol.released and ball_speed(d, bid) > 0.8)
        renderer.update_scene(d, camera=cam)
        scn = renderer.scene
        add_trail(scn, trail)
        frames.append(Image.fromarray(renderer.render()))
        if len(frames) % 40 == 0:
            print("  frame %4d  t=%.2f s" % (len(frames), d.time), flush=True)
    renderer.close()
    out = Path(args.gif)
    out.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=int(1000.0 / args.fps),
                   loop=0, optimize=True)
    print("已保存 %s（%d 帧，%.2f s）" % (out, len(frames), stop), flush=True)


def run_viewer(args):
    import mujoco.viewer
    m, d, aid, jid, bid, ctrl, w, q0, pol = build_case(args.ball, args.hold, args.sweep)
    with mujoco.viewer.launch_passive(m, d) as v:
        cam = v.cam
        cam.type = mujoco.mjtCamera.mjCAMERA_FREE
        _aim(cam, d, bid, False)
        state = {"paused": False}
        try:
            v._key_callback = lambda key: state.__setitem__("paused", not state["paused"]) \
                if key == 32 else None
        except Exception:
            pass
        print("窗口已打开：空格=暂停/继续，Esc=退出（%s，停 %.1f s 后扫 %.0f 度）"
              % (args.ball.upper(), args.hold, args.sweep), flush=True)
        wall0, trail, last_trail, last_msg, last_print = time.time(), deque(maxlen=300), -1.0, 0.0, 0.0
        while v.is_running():
            if state["paused"]:
                target = d.time
            else:
                target = min(args.speed * (time.time() - wall0), 8.0)
            if target - d.time > 0.5:
                wall0 = time.time() - d.time / args.speed
                target = d.time + 0.5
            while d.time < target:
                pol(d.time, d)
                mujoco.mj_step(m, d)
            if d.time - last_trail >= 0.004:
                trail.append(ball_pos(d, bid))
                last_trail = d.time
            released = pol.released and ball_speed(d, bid) > 0.8
            _aim(cam, d, bid, released)
            v.user_scn.ngeom = 0
            add_trail(v.user_scn, list(trail) if released else [])
            v.sync()
            if d.time >= 8.0 and not args.no_loop:
                reset_state(d, q0, ctrl, pol)
                wall0, trail = time.time(), deque(maxlen=300)
                print("—— 重播 ——", flush=True)
            now = time.time()
            if now - last_msg > 0.3:
                p = ball_pos(d, bid)
                print("t=%5.2f s  舵机J=%6.1f°  球 x=%6.1f z=%6.1f mm  v=%5.2f m/s  轨迹点=%d"
                      % (d.time, math.degrees(d.qpos[jid]) % 360.0, p[0] * 1e3, p[2] * 1e3,
                         ball_speed(d, bid), len(trail)), flush=True)
                last_msg = now
            time.sleep(0.002)


def main():
    ap = argparse.ArgumentParser(description="R32 发射系统可视化")
    ap.add_argument("--ball", default="nectar", choices=["nectar", "pollen"])
    ap.add_argument("--hold", type=float, default=1.2, help="起扫前等待秒数（默认 1.2 = 验证过的 A 案）")
    ap.add_argument("--sweep", type=float, default=248.0, help="扫掠角度（默认 248）")
    ap.add_argument("--speed", type=float, default=0.25, help="交互模式慢放倍数，0.25 = 4 倍慢放")
    ap.add_argument("--gif", default="", help="输出 GIF 路径（给了就不开窗口）")
    ap.add_argument("--size", default="480x360", help="GIF 宽x高，默认 480x360")
    ap.add_argument("--fps", type=float, default=40.0, help="GIF 帧率（按仿真时间）")
    ap.add_argument("--extra", type=float, default=0.5, help="GIF 在出射后再录多久（秒）")
    ap.add_argument("--no-probe", action="store_true", help="不预跑，直接录满 8 s")
    ap.add_argument("--no-loop", action="store_true", help="交互模式不自动重播")
    args = ap.parse_args()
    if args.gif:
        run_gif(args)
    else:
        run_viewer(args)


if __name__ == "__main__":
    raise SystemExit(main())
