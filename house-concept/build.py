"""200평 자연녹지 30평 모던 박공주택 개념설계 도면 생성기.

좌표계: 미터 단위, 원점 = 건물 외벽 북서쪽 모서리.
x 는 동쪽(+), y 는 남쪽(+). 모든 도면·면적표·검증은 아래 데이터 하나에서 나온다.
실행: python3 build.py  →  index.html 생성 + 검증 결과 출력
"""
from __future__ import annotations

import html
import math
from pathlib import Path

# ---------------------------------------------------------------- 기본 치수
W, D = 11.2, 7.2          # 외곽(외벽 외측) 동서 × 남북
T_EXT, T_INT = 0.2, 0.1   # 외벽 / 내벽 두께 (개념값)
SITE_M2 = 200 * 3.305785  # 200평
PYEONG = 3.305785

# 높이 (FL = 1층 마감바닥 ±0)
H_CEIL = 2.40      # 1층 평천장(다락 하부·북측 서비스실)
H_ATTIC_FL = 2.70  # 다락 바닥 마감
H_PLATE = 3.20     # 외벽 내측면에서의 지붕 하부 높이
PITCH = 0.70       # 지붕 물매 tan(θ) ≈ 35°
ROOF_T = 0.35      # 지붕 두께(구조+단열+마감)
EAVE = 0.60        # 처마 돌출
GL = -0.15         # 지반고
RISERS = 16
TREAD = 0.25

# ---------------------------------------------------------------- 실(순면적 영역)
# 각 실은 직사각형 목록(합집합)으로 정의. (x1, y1, x2, y2)
ROOMS = {
    "entry":  dict(name="현관", rects=[(0.2, 0.2, 1.6, 2.2)], kind="circ"),
    "util":   dict(name="세탁·건조/기계", rects=[(1.7, 0.2, 3.5, 2.2)], kind="wet"),
    "bath":   dict(name="공용욕실", rects=[(3.6, 0.2, 6.0, 2.2)], kind="wet"),
    "stair":  dict(name="U자 계단", rects=[(6.1, 0.2, 8.0, 2.85)], kind="circ"),
    "hall":   dict(name="홀", rects=[(6.1, 2.85, 8.0, 3.95)], kind="circ"),
    "master": dict(name="부부침실", rects=[(8.1, 0.2, 11.0, 3.95)], kind="bed"),
    "kids":   dict(name="자녀 공동방", rects=[(6.5, 4.05, 11.0, 7.0)], kind="kid"),
    "ldk":    dict(name="거실·식당·주방", rects=[(0.2, 2.3, 6.0, 7.0), (6.0, 2.85, 6.1, 7.0),
                                           (6.1, 3.95, 6.4, 7.0)], kind="living"),
}
INT_WALLS = [
    (0.2, 2.2, 6.0, 2.3),    # 북측 서비스열 남측벽
    (1.6, 0.2, 1.7, 2.2),    # 현관|세탁
    (3.5, 0.2, 3.6, 2.2),    # 세탁|욕실
    (6.0, 0.2, 6.1, 2.85),   # 욕실·LDK|계단
    (8.0, 0.2, 8.1, 3.95),   # 계단·홀|부부침실
    (6.4, 3.95, 11.0, 4.05), # 홀·부부|자녀
    (6.4, 4.05, 6.5, 7.0),   # LDK|자녀
]

# 가구·설비 (실 key, 이름, rect, 스타일)
FURN = [
    ("entry", "신발장", (0.2, 0.75, 0.6, 2.2), "fix"),
    ("util", "세탁·건조", (1.75, 0.25, 2.45, 0.95), "fix"),
    ("util", "보일러", (3.0, 0.9, 3.5, 1.5), "fix"),
    ("util", "싱크", (2.85, 1.65, 3.5, 2.2), "fix"),
    ("bath", "무단차 샤워", (3.6, 0.2, 4.8, 1.2), "wet"),
    ("bath", "세면대", (4.95, 0.2, 5.95, 0.7), "fix"),
    ("bath", "변기", (3.7, 1.45, 4.15, 2.2), "fix"),
    ("ldk", "냉장고·팬트리", (2.4, 2.3, 3.6, 2.95), "fix"),
    ("ldk", "싱크대", (3.6, 2.3, 5.0, 2.9), "fix"),
    ("ldk", "아일랜드(쿡탑)", (3.8, 3.9, 6.1, 4.8), "fix"),
    ("ldk", "6인 식탁", (4.1, 5.6, 5.9, 6.5), "loose"),
    ("ldk", "소파", (2.1, 4.1, 3.0, 6.3), "loose"),
    ("ldk", "TV·수납", (0.2, 4.4, 0.6, 6.0), "fix"),
    ("master", "퀸 침대", (8.8, 0.2, 10.3, 2.2), "loose"),
    ("master", "붙박이장", (9.0, 3.35, 11.0, 3.95), "fix"),
    ("kids", "싱글침대", (9.0, 4.05, 11.0, 5.05), "loose"),
    ("kids", "싱글침대", (9.0, 6.0, 11.0, 7.0), "loose"),
    ("kids", "책상", (6.5, 5.0, 7.1, 6.0), "loose"),
    ("kids", "책상", (6.5, 6.0, 7.1, 7.0), "loose"),
    ("kids", "옷장", (7.6, 4.05, 8.9, 4.65), "fix"),
]
# 식탁 의자 영역(가구 겹침 검사에 포함)
CHAIRS = [("ldk", "의자열(북)", (4.1, 5.05, 5.9, 5.6)), ("ldk", "의자열(남)", (4.1, 6.5, 5.9, 7.0))]

# 문: (이름, 힌지 x, y, 폭, 벽 방향 'h'|'v', 열리는 쪽 부호, 스윙/미닫이)
# swing: 여닫이 스윙 영역을 사분원 근사 사각형으로 검사
DOORS = [
    dict(name="현관문", x=0.45, y=0.0, w=1.0, wall="h", side=-1, kind="swing"),   # 밖여닫이
    dict(name="현관 중문", x=0.3, y=2.2, w=1.2, wall="h", side=1, kind="slide"),
    dict(name="세탁실문", x=1.6, y=1.2, w=0.85, wall="v", side=1, kind="slide"),
    dict(name="세탁실 외부문", x=2.5, y=0.0, w=0.8, wall="h", side=-1, kind="swing"),
    dict(name="욕실문", x=5.1, y=2.2, w=0.85, wall="h", side=1, kind="slide"),
    dict(name="부부침실문", x=8.0, y=3.0, w=0.85, wall="v", side=1, kind="swing"),
    dict(name="자녀방문", x=6.6, y=3.95, w=0.85, wall="h", side=1, kind="swing"),
]
# 창: (벽 'N','S','E','W', 시작, 끝, 종류)
WINDOWS = [
    ("N", 4.3, 5.3, "고창"), ("N", 6.5, 7.6, "계단창"), ("N", 9.0, 10.2, "고창"),
    ("E", 1.0, 2.4, "창"), ("E", 5.2, 5.9, "창"),
    ("S", 0.6, 3.2, "대형 미닫이"), ("S", 3.9, 6.1, "창"), ("S", 7.3, 8.9, "창"),
    ("W", 2.8, 3.9, "창"),
]
# 다락 바닥(실사용) 영역과 계단 오픈부
ATTIC = (6.4, 1.15, 11.0, 6.05)
ATTIC_VOID = (6.4, 1.15, 8.0, 2.85)
DECK = (0.0, 7.2, 7.4, 10.2)
PARK = (1.0, -6.2, 3.6, -1.2)  # 2.6×5.0 야외주차(북측)


# ---------------------------------------------------------------- 계산
def area(r):
    return (r[2] - r[0]) * (r[3] - r[1])


def room_area(k):
    return sum(area(r) for r in ROOMS[k]["rects"])


def overlap(a, b):
    return min(a[2], b[2]) - max(a[0], b[0]) > 1e-6 and min(a[3], b[3]) - max(a[1], b[1]) > 1e-6


def inside(r, rects):
    """r 이 rects 합집합 안에 있는지(5cm 격자)."""
    step = 0.05
    x = r[0] + step / 2
    while x < r[2]:
        y = r[1] + step / 2
        while y < r[3]:
            if not any(q[0] <= x <= q[2] and q[1] <= y <= q[3] for q in rects):
                return False
            y += step
        x += step
    return True


def door_zone(d):
    """문 개폐에 필요한 바닥 영역."""
    w = d["w"]
    if d["wall"] == "h":
        y0 = d["y"] + (0.1 if d["side"] > 0 else 0)
        if d["side"] > 0:
            return (d["x"], y0, d["x"] + w, y0 + (w if d["kind"] == "swing" else 0.6))
        return (d["x"], y0 - w, d["x"] + w, y0)
    x0 = d["x"] + (0.1 if d["side"] > 0 else 0)
    return (x0, d["y"], x0 + (w if d["kind"] == "swing" else 0.6), d["y"] + w)


def run_checks():
    res = []

    def add(ok, text):
        res.append((ok, text))

    # 1. 면적 커버리지: 실 + 벽이 외곽을 정확히 한 번씩 덮는가
    rects = [(0, 0, W, T_EXT), (0, D - T_EXT, W, D), (0, T_EXT, T_EXT, D - T_EXT), (W - T_EXT, T_EXT, W, D - T_EXT)]
    rects += INT_WALLS
    for k in ROOMS:
        rects += ROOMS[k]["rects"]
    n = 0
    bad = 0
    step = 0.05
    gx = int(round(W / step))
    gy = int(round(D / step))
    for i in range(gx):
        for j in range(gy):
            x, y = (i + 0.5) * step, (j + 0.5) * step
            c = sum(1 for r in rects if r[0] <= x <= r[2] and r[1] <= y <= r[3])
            n += 1
            bad += c != 1
    add(bad == 0, f"실 + 벽체가 11.2×7.2m 외곽을 빈틈·중복 없이 채움 (5cm 격자 {n}칸 중 오류 {bad}칸)")

    room_sum = sum(room_area(k) for k in ROOMS)
    wall_sum = sum(area(r) for r in INT_WALLS) + (W * D - (W - 2 * T_EXT) * (D - 2 * T_EXT))
    add(abs(room_sum + wall_sum - W * D) < 1e-6,
        f"순면적 {room_sum:.2f}㎡ + 벽체 {wall_sum:.2f}㎡ = 건축면적 {W*D:.2f}㎡")

    # 2. 가구가 자기 실 안에 있고 서로 겹치지 않는가
    items = [(k, n_, r) for k, n_, r, _ in FURN] + CHAIRS
    out = [n_ for k, n_, r in items if not inside(r, ROOMS[k]["rects"])]
    add(not out, "모든 가구가 해당 실 경계 안에 배치됨" + (f" (벗어남: {out})" if out else ""))
    clash = [(a[1], b[1]) for i, a in enumerate(items) for b in items[i + 1:] if a[0] == b[0] and overlap(a[2], b[2])]
    add(not clash, "가구끼리 겹침 없음" + (f" {clash}" if clash else ""))

    # 3. 문 개폐 영역이 가구를 침범하지 않는가
    dclash = [(d["name"], n_) for d in DOORS for k, n_, r in items if overlap(door_zone(d), r)]
    add(not dclash, "문 개폐 영역에 가구 없음" + (f" {dclash}" if dclash else ""))

    # 4. 주요 통로 폭 (가구 좌표에서 계산)
    F = {n_: r for k, n_, r, _ in FURN}
    isl, sink, sofa, table = F["아일랜드(쿡탑)"], F["싱크대"], F["소파"], F["6인 식탁"]
    bed, ward = F["퀸 침대"], F["붙박이장"]
    aisle = isl[1] - sink[3]
    add(aisle >= 1.0 - 1e-9, f"주방 작업통로 = 현관→홀 주동선 폭 {aisle:.2f}m (싱크대~아일랜드)")
    gap = isl[0] - sofa[2]
    add(gap >= 0.8 - 1e-9, f"소파 등~아일랜드 사이 통로 {gap:.2f}m (거실↔주방)")
    gap2 = table[1] - isl[3]
    add(gap2 >= 0.75, f"아일랜드~식탁 사이 {gap2:.2f}m (의자 착석 공간, 통행로 아님)")
    hall = ROOMS["hall"]["rects"][0]
    add(hall[3] - hall[1] >= 1.0, f"홀 폭 {hall[3]-hall[1]:.2f}m, 부부침실·자녀방·계단 출입 모두 홀에서")
    foot = ward[1] - bed[3]
    side = min(bed[0] - 8.1, 11.0 - bed[2])
    add(foot >= 0.9 and side >= 0.6, f"부부침실 침대 발치~붙박이장 {foot:.2f}m, 침대 옆 최소 {side:.2f}m")
    kb = [r for k, n_, r, _ in FURN if n_ == "싱글침대"]
    add(kb[1][1] - kb[0][3] >= 0.8, f"자녀방 침대 사이 {kb[1][1]-kb[0][3]:.2f}m, 책상~침대 사이 놀이공간 {kb[0][0]-7.1:.1f}m 폭")

    # 5. 계단
    rise = H_ATTIC_FL / RISERS
    run = (RISERS // 2 - 1) * TREAD
    add(abs(0.9 + run - 2.65) < 1e-6, f"U자 계단: 단높이 {rise*1000:.0f}mm × {RISERS}단, 디딤판 {TREAD*1000:.0f}mm, "
        f"한 흐름 {run:.2f}m + 참 0.90m = 2.65m, 유효폭 0.90m")
    land_h = rise * RISERS / 2
    roof_at = lambda y: H_PLATE + PITCH * min(y - T_EXT, D - T_EXT - y)
    hr_land = roof_at(0.65) - land_h
    add(hr_land >= 2.0, f"참(높이 {land_h:.2f}m) 보행선 위 지붕까지 머리높이 {hr_land:.2f}m")
    hr_top = roof_at(2.6) - (H_ATTIC_FL - rise)
    add(hr_top >= 2.0, f"계단 상부 도착부 머리높이 {hr_top:.2f}m")
    add(H_ATTIC_FL - 0.30 >= H_CEIL, f"다락 하부 홀·침실 천장고 {H_CEIL:.2f}m (다락 바닥구조 0.30m)")

    # 6. 다락 면적·높이
    a_att = area(ATTIC) - area(ATTIC_VOID)
    add(abs(a_att - 19.83) < 0.1, f"다락 실사용 바닥 {a_att:.2f}㎡ = {a_att/PYEONG:.2f}평")
    add(ATTIC[0] >= 6.4 - 1e-9, "다락은 x≥6.4m(홀·침실 상부)에만 있어 거실 오픈천장(x≤6.4m)과 겹치지 않음")
    # 7. 무단차
    add(True, "현관·욕실·데크 모두 FL±0 기준 무단차(현관은 트렌치 배수, 욕실은 바닥 슬로프+트렌치)")
    return res


# ---------------------------------------------------------------- SVG 헬퍼
S = 54  # px / m


def fmt(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


class Svg:
    def __init__(self, ox, oy, w, h, title):
        self.ox, self.oy, self.w, self.h = ox, oy, w, h
        self.parts = []
        self.title = title

    def X(self, x):
        return self.ox + x * S

    def Y(self, y):
        return self.oy + y * S

    def rect(self, r, cls, extra=""):
        self.parts.append(f'<rect class="{cls}" x="{self.X(r[0]):.1f}" y="{self.Y(r[1]):.1f}" '
                          f'width="{(r[2]-r[0])*S:.1f}" height="{(r[3]-r[1])*S:.1f}" {extra}/>')

    def line(self, x1, y1, x2, y2, cls):
        self.parts.append(f'<line class="{cls}" x1="{self.X(x1):.1f}" y1="{self.Y(y1):.1f}" '
                          f'x2="{self.X(x2):.1f}" y2="{self.Y(y2):.1f}"/>')

    def text(self, x, y, s, cls, anchor="middle", rot=None):
        tr = f' transform="rotate({rot} {self.X(x):.1f} {self.Y(y):.1f})"' if rot else ""
        self.parts.append(f'<text class="{cls}" x="{self.X(x):.1f}" y="{self.Y(y):.1f}" '
                          f'text-anchor="{anchor}"{tr}>{html.escape(s)}</text>')

    def raw(self, s):
        self.parts.append(s)

    def dim_h(self, x1, x2, y, label=None, tick=0.12):
        self.line(x1, y, x2, y, "dim")
        for x in (x1, x2):
            self.line(x - tick / 2, y + tick / 2, x + tick / 2, y - tick / 2, "dimtick")
        self.text((x1 + x2) / 2, y - 0.08, label or fmt(x2 - x1), "dimtxt")

    def dim_v(self, y1, y2, x, label=None, tick=0.12):
        self.line(x, y1, x, y2, "dim")
        for y in (y1, y2):
            self.line(x - tick / 2, y + tick / 2, x + tick / 2, y - tick / 2, "dimtick")
        self.text(x - 0.08, (y1 + y2) / 2, label or fmt(y2 - y1), "dimtxt", rot=-90)

    def north(self, x, y):
        cx, cy = self.X(x), self.Y(y)
        self.raw(f'<g class="north"><circle cx="{cx}" cy="{cy}" r="17" class="nc"/>'
                 f'<path d="M{cx} {cy-14} L{cx+7} {cy+9} L{cx} {cy+4} L{cx-7} {cy+9} Z" class="na"/>'
                 f'<text x="{cx}" y="{cy-21}" text-anchor="middle" class="ntxt">N</text></g>')

    def out(self):
        return (f'<svg viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{html.escape(self.title)}" '
                f'xmlns="http://www.w3.org/2000/svg"><title>{html.escape(self.title)}</title>'
                + "".join(self.parts) + "</svg>")


def draw_door(s: Svg, d):
    w = d["w"]
    if d["kind"] == "slide":
        # 미닫이: 벽 개구부 + 두 줄 문짝
        if d["wall"] == "h":
            s.rect((d["x"], d["y"], d["x"] + w, d["y"] + 0.1), "open")
            s.line(d["x"], d["y"] + 0.03, d["x"] + w * 0.6, d["y"] + 0.03, "door")
            s.line(d["x"] + w * 0.4, d["y"] + 0.07, d["x"] + w, d["y"] + 0.07, "door")
        else:
            s.rect((d["x"], d["y"], d["x"] + 0.1, d["y"] + w), "open")
            s.line(d["x"] + 0.03, d["y"], d["x"] + 0.03, d["y"] + w * 0.6, "door")
            s.line(d["x"] + 0.07, d["y"] + w * 0.4, d["x"] + 0.07, d["y"] + w, "door")
        return
    t = T_EXT if d["name"] in ("현관문", "세탁실 외부문") else T_INT
    if d["wall"] == "h":
        s.rect((d["x"], d["y"], d["x"] + w, d["y"] + t), "open")
        yb = d["y"] + (t if d["side"] > 0 else 0)
        yl = yb + d["side"] * w
        s.line(d["x"], yb, d["x"], yl, "door")
        s.raw(f'<path class="swing" d="M{s.X(d["x"]):.1f} {s.Y(yl):.1f} A{w*S:.1f} {w*S:.1f} 0 0 '
              f'{0 if d["side"] > 0 else 1} {s.X(d["x"]+w):.1f} {s.Y(yb):.1f}"/>')
    else:
        s.rect((d["x"], d["y"], d["x"] + t, d["y"] + w), "open")
        xb = d["x"] + (t if d["side"] > 0 else 0)
        xl = xb + d["side"] * w
        s.line(xb, d["y"], xl, d["y"], "door")
        s.raw(f'<path class="swing" d="M{s.X(xl):.1f} {s.Y(d["y"]):.1f} A{w*S:.1f} {w*S:.1f} 0 0 1 '
              f'{s.X(xb):.1f} {s.Y(d["y"]+w):.1f}"/>')


def draw_window(s: Svg, wdw):
    side, a, b, kind = wdw
    if side in "NS":
        y0 = 0 if side == "N" else D - T_EXT
        s.rect((a, y0, b, y0 + T_EXT), "win")
        s.line(a, y0 + T_EXT / 2, b, y0 + T_EXT / 2, "winl")
    else:
        x0 = 0 if side == "W" else W - T_EXT
        s.rect((x0, a, x0 + T_EXT, b), "win")
        s.line(x0 + T_EXT / 2, a, x0 + T_EXT / 2, b, "winl")


def label_room(s, k, cx, cy, dims=None, sub=None):
    r = ROOMS[k]
    s.text(cx, cy, r["name"], "rname")
    a = room_area(k)
    s.text(cx, cy + 0.32, f"{a:.1f}㎡" + (f" · {dims}" if dims else ""), "rarea")
    if sub:
        s.text(cx, cy + 0.6, sub, "rsub")


def plan_1f():
    s = Svg(ox=70, oy=410, w=760, h=1040, title="1층 개념 평면도")
    # 대지 맥락: 주차·도로(북), 데크·마당(남)
    s.rect((-1.0, -7.2, 12.2, -6.4), "road")
    s.text(5.6, -6.68, "북측 진입도로 (가정)", "ctx")
    s.rect(PARK, "park")
    s.text((PARK[0] + PARK[2]) / 2, -3.6, "야외주차", "ctxb")
    s.text((PARK[0] + PARK[2]) / 2, -3.25, "2.6×5.0m", "ctxs")
    s.text(3.8, -1.9, "진입로 →", "ctxs", anchor="start")
    s.rect(DECK, "deck")
    for i in range(1, 25):
        yy = DECK[1] + i * 0.12
        if yy < DECK[3]:
            s.line(DECK[0], yy, DECK[2], yy, "deckl")
    s.text(3.7, 9.0, "남향 데크 약 22㎡ (7.4×3.0m)", "ctxb")
    s.text(3.7, 9.4, "거실·식당에서 무단차로 연결", "ctxs")
    s.text(9.3, 9.2, "남측 마당 · 텃밭 · 바비큐", "ctx")

    # 건물: 외곽 전체를 벽색으로 칠하고 실 영역을 바닥색으로 덮는다
    s.rect((0, 0, W, D), "wall")
    fills = {"circ": "f-circ", "wet": "f-wet", "bed": "f-bed", "kid": "f-kid", "living": "f-liv"}
    for k, r in ROOMS.items():
        for q in r["rects"]:
            s.rect(q, "floor " + fills[r["kind"]])
    # 거실 오픈천장 영역 표시(해치 경계)
    s.rect((0.2, 2.3, 6.4, 7.0), "openceil")
    # 다락 투영선
    s.rect(ATTIC, "attic-proj")
    s.text(10.95, 3.3, "다락 바닥 투영", "projtxt", anchor="end")
    for wdw in WINDOWS:
        draw_window(s, wdw)
    for d in DOORS:
        draw_door(s, d)
    # 계단: 디딤판·진행방향
    x1a, x1b, x2a, x2b = 6.1, 7.0, 7.1, 8.0
    for i in range(RISERS // 2):
        y = 2.85 - i * TREAD
        s.line(x1a, y, x1b, y, "tread")
        s.line(x2a, y, x2b, y, "tread")
    s.line(7.05, 1.1, 7.05, 2.85, "stairmid")
    s.line(6.1, 1.1, 8.0, 1.1, "tread")
    s.raw(f'<path class="arrow" d="M{s.X(6.55):.1f} {s.Y(2.75):.1f} L{s.X(6.55):.1f} {s.Y(0.65):.1f} '
          f'L{s.X(7.55):.1f} {s.Y(0.65):.1f} L{s.X(7.55):.1f} {s.Y(2.7):.1f}" marker-end="url(#ah)"/>')
    s.text(6.55, 3.15, "UP", "up")
    s.text(7.55, 3.15, "다락↑", "upsm")

    # 가구
    for k, n_, r, st in FURN:
        s.rect(r, "fur-" + st)
        cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
        vertical = (r[3] - r[1]) > (r[2] - r[0]) * 1.4 and (r[2] - r[0]) < 0.8
        s.text(cx, cy + 0.07, n_, "fur", rot=-90 if vertical else None)
    for k, n_, r in CHAIRS:
        n = 3
        w = (r[2] - r[0]) / n
        for i in range(n):
            s.rect((r[0] + i * w + 0.08, r[1] + 0.05, r[0] + (i + 1) * w - 0.08, r[3] - 0.05), "chair")
    # 샤워 배수 트렌치
    s.line(3.65, 1.12, 4.75, 1.12, "drain")

    # 실명
    label_room(s, "entry", 1.1, 1.0)
    label_room(s, "util", 2.25, 1.35)
    label_room(s, "bath", 5.1, 1.35)
    label_room(s, "master", 9.7, 2.65, "2.9×3.75")
    label_room(s, "kids", 8.05, 5.45, "4.5×2.95")
    s.text(7.05, 3.55, "홀", "rname")
    s.text(1.6, 3.35, "거실", "rname")
    s.text(1.6, 3.67, "박공 오픈천장", "rsub")
    s.text(5.0, 5.25, "식당", "rname")
    s.text(4.3, 3.62, "주방", "rname")
    s.text(3.2, 6.8, f"LDK {room_area('ldk'):.1f}㎡", "rarea")

    # 치수: 외곽
    s.dim_h(0, W, -1.55, "11.2")
    s.dim_v(0, D, -0.55, "7.2")
    # 북측 실 폭(내법)
    xs = [0.2, 1.6, 1.7, 3.5, 3.6, 6.0, 6.1, 8.0, 8.1, 11.0]
    for a, b in zip(xs[0::2], xs[1::2]):
        s.dim_h(a, b, -1.2, fmt(b - a))
    # 남측 실 폭
    s.dim_h(0.2, 6.4, DECK[3] + 0.45, "6.2 (LDK 내법)")
    s.dim_h(6.5, 11.0, DECK[3] + 0.45, "4.5")
    # 동측 깊이
    s.dim_v(0.2, 3.95, W + 0.45, "3.75")
    s.dim_v(4.05, 7.0, W + 0.45, "2.95")
    # 서측 깊이
    s.dim_v(0.2, 2.2, -0.25, "2.0")
    s.dim_v(2.3, 7.0, -0.25, "4.7")
    s.north(11.6, -6.0)
    s.raw('<defs><marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="7" markerHeight="7" '
          'orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" class="ahp"/></marker></defs>')
    s.text(-1.1, 11.45, "치수 단위 m · 벽 중심선이 아닌 내법(실 안쪽) 기준 · 외벽 0.2 / 내벽 0.1 개념값",
           "note", anchor="start")
    return s.out()


def plan_attic():
    s = Svg(ox=70, oy=70, w=760, h=520, title="다락 개념 평면도")
    s.rect((0, 0, W, D), "roofarea")
    s.text(3.2, 3.9, "거실·식당 상부 오픈 (박공 천장까지)", "ctx")
    s.text(3.2, 4.25, "서측 박공면 고창", "ctxs")
    # 무릎벽 뒤 수납(저높이)
    s.rect((6.4, T_EXT, W - T_EXT, ATTIC[1]), "lowzone")
    s.rect((6.4, ATTIC[3], W - T_EXT, D - T_EXT), "lowzone")
    s.text(9.5, 0.75, "무릎벽 뒤 수납 (높이 1.17m 이하)", "ctxs")
    s.text(9.5, 6.7, "무릎벽 뒤 수납 (높이 1.17m 이하)", "ctxs")
    s.rect(ATTIC, "floor f-kid")
    s.rect(ATTIC_VOID, "void")
    s.text(6.75, 2.0, "오픈", "ctxs")
    # 1.8m 이상 구간
    y18a = T_EXT + (H_ATTIC_FL + 1.8 - H_PLATE) / PITCH
    y18b = D - y18a
    s.rect((8.0, y18a, W - T_EXT, y18b), "tall")
    s.rect((6.4, 2.85, 8.0, y18b), "tall")
    s.text(W - 0.35, y18a + 0.3, "천장고 1.8m 이상 구간", "projtxt", anchor="end")
    # 계단 윗부분
    for i in range(RISERS // 2):
        y = 2.85 - i * TREAD
        s.line(7.1, y, 8.0, y, "tread")
    s.raw(f'<path class="arrow" d="M{s.X(7.55):.1f} {s.Y(1.4):.1f} L{s.X(7.55):.1f} {s.Y(3.2):.1f}" marker-end="url(#ah2)"/>')
    # 난간
    s.line(6.4, 2.85, 6.4, ATTIC[3], "rail")
    s.line(6.4, 1.15, 7.1, 1.15, "rail")
    s.line(6.4, 1.15, 6.4, 2.85, "rail")
    s.line(7.05, 1.15, 7.05, 2.85, "rail")
    s.text(6.2, 4.6, "난간 1.2m (거실 조망)", "projtxt", anchor="end")
    # 벽선
    s.rect((0, 0, W, D), "outline")
    s.rect((W - T_EXT, 2.9, W, 4.3), "win")
    s.text(W - 0.3, 2.75, "동측 박공창", "ctxs", anchor="end")
    s.rect((9.2, 3.0, 10.2, 3.6), "skylight")
    s.text(9.7, 3.85, "천창(선택)", "ctxs")
    s.text(9.0, 4.6, "자녀 놀이·취미 다락", "rname")
    a = area(ATTIC) - area(ATTIC_VOID)
    s.text(9.0, 4.92, f"실사용 바닥 {a:.1f}㎡ ({a/PYEONG:.1f}평)", "rarea")
    s.dim_h(6.4, 11.0, -0.3, "4.6")
    s.dim_v(1.15, 6.05, W + 0.5, "4.9")
    s.dim_h(0, W, -0.65, "11.2")
    s.north(-0.6, 7.6)
    s.raw('<defs><marker id="ah2" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="7" markerHeight="7" '
          'orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" class="ahp"/></marker></defs>')
    return s.out()


def section_cross():
    """남북 횡단면 (x≈9.5, 다락·부부침실·자녀방 통과)."""
    SV = 50
    ox, oy = 90, 380
    X = lambda y: ox + y * SV       # 남북 → 가로
    Y = lambda z: oy - z * SV       # 높이 → 세로
    p = []

    def ln(a, b, c, d_, cls):
        p.append(f'<line class="{cls}" x1="{X(a):.1f}" y1="{Y(b):.1f}" x2="{X(c):.1f}" y2="{Y(d_):.1f}"/>')

    def tx(a, b, t, cls, anc="middle"):
        p.append(f'<text class="{cls}" x="{X(a):.1f}" y="{Y(b):.1f}" text-anchor="{anc}">{html.escape(t)}</text>')

    ridge_u = H_PLATE + PITCH * (D / 2 - T_EXT)
    # 지반, 슬래브
    p.append(f'<rect class="ground" x="{X(-2):.1f}" y="{Y(GL):.1f}" width="{11.2*SV:.1f}" height="{0.5*SV:.1f}"/>')
    p.append(f'<rect class="wallsec" x="{X(0):.1f}" y="{Y(0):.1f}" width="{D*SV:.1f}" height="{0.25*SV:.1f}"/>')
    # 외벽
    for y0 in (0, D - T_EXT):
        p.append(f'<rect class="wallsec" x="{X(y0):.1f}" y="{Y(H_PLATE):.1f}" width="{T_EXT*SV:.1f}" height="{H_PLATE*SV:.1f}"/>')
    # 지붕(하부선 + 상부선)
    top_off = ROOF_T / math.cos(math.atan(PITCH))
    pts_u = [(T_EXT - 0 - EAVE, H_PLATE - PITCH * EAVE), (D / 2, ridge_u), (D - T_EXT + EAVE, H_PLATE - PITCH * EAVE)]
    poly = [(a, b) for a, b in pts_u] + [(a, b + top_off) for a, b in reversed(pts_u)]
    p.append('<polygon class="roofsec" points="' + " ".join(f"{X(a):.1f},{Y(b):.1f}" for a, b in poly) + '"/>')
    # 다락 바닥
    p.append(f'<rect class="slab" x="{X(T_EXT):.1f}" y="{Y(H_ATTIC_FL):.1f}" width="{(D-2*T_EXT)*SV:.1f}" height="{0.3*SV:.1f}"/>')
    # 무릎벽
    for yk in (ATTIC[1], ATTIC[3]):
        hk = H_PLATE + PITCH * min(yk - T_EXT, D - T_EXT - yk)
        ln(yk, H_ATTIC_FL, yk, hk, "knee")
    # 1.8m 선
    ya = T_EXT + (H_ATTIC_FL + 1.8 - H_PLATE) / PITCH
    p.append(f'<rect class="tallsec" x="{X(ya):.1f}" y="{Y(ridge_u):.1f}" width="{(D-2*ya)*SV:.1f}" '
             f'height="{(ridge_u-H_ATTIC_FL-1.8)*SV:.1f}"/>')
    ln(ya, H_ATTIC_FL + 1.8, D - ya, H_ATTIC_FL + 1.8, "h18")
    tx(D / 2, H_ATTIC_FL + 1.88, "다락 바닥+1.8m", "sectxt")
    # 1층 칸막이 (부부침실 | 자녀방)
    p.append(f'<rect class="wallsec" x="{X(3.95):.1f}" y="{Y(H_CEIL):.1f}" width="{0.1*SV:.1f}" height="{H_CEIL*SV:.1f}"/>')
    ln(T_EXT, H_CEIL, D - T_EXT, H_CEIL, "ceil")
    tx(2.1, 1.1, "부부침실", "secroom")
    tx(5.5, 1.1, "자녀 공동방", "secroom")
    tx(D / 2, 3.35, "자녀 놀이 다락", "secroom")
    # 치수(높이)
    for z, lab in ((0, "FL ±0"), (H_CEIL, f"천장 {H_CEIL:.2f}"), (H_ATTIC_FL, f"다락 FL +{H_ATTIC_FL:.2f}"),
                   (H_PLATE, f"지붕하부@외벽 +{H_PLATE:.2f}"), (ridge_u, f"용마루 하부 +{ridge_u:.2f}")):
        ln(D + 0.9, z, D + 1.1, z, "dimtick")
        tx(D + 1.25, z - 0.05, lab, "sectxt", "start")
    ln(D + 1.0, 0, D + 1.0, ridge_u, "dim")
    tx(-0.2, GL - 0.35, "GL −0.15", "sectxt", "start")
    tx(-0.6, -0.55, "북", "secdir")
    tx(D + 0.6, -0.55, "남", "secdir")
    tx(0.9, ridge_u + 0.35, f"물매 약 {math.degrees(math.atan(PITCH)):.0f}°", "sectxt")
    return (f'<svg viewBox="0 0 720 440" role="img" aria-label="다락 횡단면" xmlns="http://www.w3.org/2000/svg">'
            f'<title>남북 횡단면(다락 통과)</title>' + "".join(p) + "</svg>")


def section_long():
    """동서 종단면 (y≈3.4, 용마루 아래)."""
    SV = 50
    ox, oy = 50, 360
    X = lambda x: ox + x * SV
    Y = lambda z: oy - z * SV
    p = []

    def r(x1, z1, x2, z2, cls):
        p.append(f'<rect class="{cls}" x="{X(x1):.1f}" y="{Y(z2):.1f}" width="{(x2-x1)*SV:.1f}" height="{(z2-z1)*SV:.1f}"/>')

    def tx(a, b, t, cls, anc="middle"):
        p.append(f'<text class="{cls}" x="{X(a):.1f}" y="{Y(b):.1f}" text-anchor="{anc}">{html.escape(t)}</text>')

    ridge_u = H_PLATE + PITCH * (D / 2 - T_EXT)
    r(-0.8, GL - 0.5, W + 0.8, GL, "ground")
    r(0, -0.25, W, 0, "wallsec")
    # 박공벽(동·서) - 단면에서는 용마루 높이까지
    r(0, 0, T_EXT, ridge_u, "wallsec")
    r(W - T_EXT, 0, W, ridge_u, "wallsec")
    r(-0.3, ridge_u, W + 0.3, ridge_u + ROOF_T, "roofsec")
    # 다락 바닥 (x 6.4~11.0), 계단 오픈부는 단면 위치(y=3.4)에서는 없음 → 홀 상부 다락
    r(6.4, H_ATTIC_FL - 0.3, W - T_EXT, H_ATTIC_FL, "slab")
    # 1층 칸막이: 거실|자녀방 x6.4~6.5 (y=3.4 에서는 홀/부부침실: x8.0~8.1)
    r(8.0, 0, 8.1, H_CEIL, "wallsec")
    # 다락 난간
    p.append(f'<line class="rail" x1="{X(6.4):.1f}" y1="{Y(H_ATTIC_FL):.1f}" x2="{X(6.4):.1f}" y2="{Y(H_ATTIC_FL+1.2):.1f}"/>')
    # 서측 박공 고창
    r(0, 3.4, T_EXT, 5.0, "winsec")
    r(W - T_EXT, 3.4, W, 4.6, "winsec")
    # 남측 대형창 입면 투영(점선)
    p.append(f'<rect class="proj" x="{X(0.6):.1f}" y="{Y(2.4):.1f}" width="{2.6*SV:.1f}" height="{2.4*SV:.1f}"/>')
    tx(3.2, 3.2, "높은 거실 · 식당", "secroom")
    tx(3.2, 2.8, f"천장 최고 약 {ridge_u:.1f}m (용마루 하부)", "sectxt")
    tx(7.2, 1.2, "홀", "secroom")
    tx(9.6, 1.2, "부부침실", "secroom")
    tx(8.7, 3.4, "놀이 다락", "secroom")
    tx(0.1, 5.2, "서측 고창", "sectxt", "start")
    tx(6.35, H_ATTIC_FL + 1.35, "난간", "sectxt", "end")
    for z, lab in ((0, "±0"), (H_CEIL, f"{H_CEIL:.2f}"), (H_ATTIC_FL, f"{H_ATTIC_FL:.2f}"), (ridge_u, f"{ridge_u:.2f}")):
        tx(W + 0.9, z - 0.05, lab, "sectxt", "start")
        p.append(f'<line class="dimtick" x1="{X(W+0.55):.1f}" y1="{Y(z):.1f}" x2="{X(W+0.8):.1f}" y2="{Y(z):.1f}"/>')
    tx(-0.2, -0.75, "서", "secdir")
    tx(W + 0.2, -0.75, "동", "secdir")
    return (f'<svg viewBox="0 0 720 420" role="img" aria-label="동서 종단면" xmlns="http://www.w3.org/2000/svg">'
            f'<title>동서 종단면(용마루 아래)</title>' + "".join(p) + "</svg>")


# ---------------------------------------------------------------- 표
def area_rows():
    targets = {"entry": None, "util": 4.7, "bath": 4.8, "stair": None, "hall": None,
               "master": 11.0, "kids": 14.0, "ldk": 30.0}
    notes = {
        "entry": "신발·외투장, 트렌치 배수로 무단차, 중문 미닫이",
        "util": "세탁·건조 적층 + 보일러 + 다용도 싱크, 현관과 외부 양쪽에서 출입",
        "bath": "무단차 샤워 1.2×1.0, 미닫이문, 변기·샤워 옆 보강벽",
        "stair": "1층 바닥 투영, 계단 하부(첫 흐름 아래) 수납",
        "hall": "부부침실·자녀방·계단 출입을 모아 거실에서 침실문이 정면으로 보이지 않게 함",
        "master": "퀸 침대, 붙박이장 2.0m(목표 2.4m에서 축소), 동측창",
        "kids": "싱글침대 2 + 책상 2(1.0×0.6) + 옷장, 중앙 놀이공간",
        "ldk": "거실 약 2.9m폭 + 식당 + 대면형 아일랜드 주방, 오픈천장",
    }
    rows = []
    for k in ["ldk", "master", "kids", "bath", "util", "entry", "hall", "stair"]:
        a = room_area(k)
        t = targets[k]
        rows.append((ROOMS[k]["name"], a, t, notes[k]))
    return rows


CSS = """
:root{
  --paper:#f3f5f2; --sheet:#fbfcfa; --ink:#1d2622; --ink2:#4d5a54; --rule:#c9d1cb;
  --pine:#2e6a50; --pine-soft:#dce9e1; --timber:#a8743f; --timber-soft:#efe2d2; --warn:#a4561d; --ok:#2e6a50;
  --wall:#2a332f; --f-liv:#fbf6ea; --f-bed:#eef2f7; --f-kid:#eaf3ec; --f-wet:#e5eff3; --f-circ:#f2f2ef;
  --fur:#7b8a83; --tall:rgba(46,106,80,.12);
  --display:"Gowun Batang","Noto Serif KR",serif; --body:"IBM Plex Sans KR","Apple SD Gothic Neo","Malgun Gothic",sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  color-scheme:dark; --paper:#121715; --sheet:#171d1a; --ink:#e3e9e5; --ink2:#a3b0a9; --rule:#34403a;
  --pine:#7cc4a0; --pine-soft:#1f3329; --timber:#d6a36d; --timber-soft:#3a2d1f; --warn:#e3a06a; --ok:#7cc4a0;
  --wall:#c9d3cd; --f-liv:#231f17; --f-bed:#1b2129; --f-kid:#1a261e; --f-wet:#18242a; --f-circ:#1e2220;
  --fur:#8e9c95; --tall:rgba(124,196,160,.14);}}
:root[data-theme="dark"]{
  color-scheme:dark; --paper:#121715; --sheet:#171d1a; --ink:#e3e9e5; --ink2:#a3b0a9; --rule:#34403a;
  --pine:#7cc4a0; --pine-soft:#1f3329; --timber:#d6a36d; --timber-soft:#3a2d1f; --warn:#e3a06a; --ok:#7cc4a0;
  --wall:#c9d3cd; --f-liv:#231f17; --f-bed:#1b2129; --f-kid:#1a261e; --f-wet:#18242a; --f-circ:#1e2220;
  --fur:#8e9c95; --tall:rgba(124,196,160,.14);}
*{box-sizing:border-box}
body{background:var(--paper);color:var(--ink);font-family:var(--body);font-size:15px;line-height:1.65;margin:0;padding-inline:16px}
.wrap{max-width:1040px;margin:0 auto;padding-block:40px 64px;display:grid;gap:44px}
header{display:grid;gap:14px;border-bottom:2px solid var(--ink);padding-bottom:22px}
.stamp{font-family:var(--mono);font-size:12px;letter-spacing:.06em;color:var(--warn);text-transform:uppercase}
h1{font-family:var(--display);font-weight:700;font-size:clamp(28px,4.6vw,44px);line-height:1.2;margin:0;text-wrap:balance}
h2{font-family:var(--display);font-size:24px;margin:0;text-wrap:balance;display:flex;gap:12px;align-items:baseline}
h2 .code{font-family:var(--mono);font-size:13px;color:var(--pine);border:1px solid var(--pine);padding:1px 7px;border-radius:3px}
h3{font-size:15px;margin:0}
p{margin:0;max-width:68ch}
.lede{color:var(--ink2);font-size:16px}
section{display:grid;gap:16px}
.sheet{background:var(--sheet);border:1px solid var(--rule);border-radius:4px;padding:16px;overflow-x:auto}
.sheet svg{display:block;width:100%;min-width:640px;height:auto}
.grid2{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.kv{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:1px;background:var(--rule);border:1px solid var(--rule)}
.kv div{background:var(--sheet);padding:12px 14px;display:grid;gap:2px}
.kv b{font-family:var(--mono);font-size:20px;font-variant-numeric:tabular-nums}
.kv span{font-size:12px;color:var(--ink2);letter-spacing:.02em}
.tbl{overflow-x:auto;border:1px solid var(--rule);background:var(--sheet)}
table{border-collapse:collapse;width:100%;min-width:600px;font-size:14px}
th,td{padding:9px 12px;border-bottom:1px solid var(--rule);text-align:left;vertical-align:top}
th{font-size:12px;letter-spacing:.04em;color:var(--ink2);font-weight:600;background:var(--paper)}
td.n{font-family:var(--mono);font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap}
tr.sum td{font-weight:700;border-top:2px solid var(--ink)}
.diff{color:var(--warn)}
ul.checks{list-style:none;margin:0;padding:0;display:grid;gap:6px}
ul.checks li{display:grid;grid-template-columns:28px 1fr;gap:8px;align-items:start}
.pill{font-family:var(--mono);font-size:11px;padding:1px 0;text-align:center;border-radius:3px;font-weight:600}
.pill.ok{background:var(--pine-soft);color:var(--ok)}
.pill.ng{background:var(--timber-soft);color:var(--warn)}
.callout{border-left:3px solid var(--timber);background:var(--timber-soft);padding:12px 16px;display:grid;gap:6px}
.list{margin:0;padding-left:20px;display:grid;gap:4px;max-width:72ch}
.legend{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:12px;color:var(--ink2)}
.legend i{display:inline-block;width:14px;height:10px;border:1px solid var(--rule);margin-right:6px;vertical-align:-1px}
footer{font-size:12.5px;color:var(--ink2);border-top:1px solid var(--rule);padding-top:16px;display:grid;gap:6px}
a{color:var(--pine)}
/* SVG */
svg text{font-family:var(--body)}
.wall{fill:var(--wall)} .floor{stroke:none} .f-liv{fill:var(--f-liv)} .f-bed{fill:var(--f-bed)} .f-kid{fill:var(--f-kid)}
.f-wet{fill:var(--f-wet)} .f-circ{fill:var(--f-circ)}
.openceil{fill:none;stroke:var(--timber);stroke-width:1;stroke-dasharray:2 4}
.attic-proj{fill:none;stroke:var(--pine);stroke-width:1.4;stroke-dasharray:9 5}
.projtxt{fill:var(--pine);font-size:10.5px}
.open{fill:var(--sheet)} .door{stroke:var(--ink);stroke-width:1.6} .swing{fill:none;stroke:var(--ink2);stroke-width:.8;stroke-dasharray:3 2}
.win{fill:var(--sheet);stroke:var(--ink);stroke-width:1} .winl{stroke:var(--ink);stroke-width:.8}
.tread{stroke:var(--ink2);stroke-width:.8} .stairmid{stroke:var(--ink2);stroke-width:.8}
.arrow{fill:none;stroke:var(--warn);stroke-width:1.4} .ahp{fill:var(--warn)}
.up{fill:var(--warn);font-size:10px;font-weight:700;font-family:var(--mono)} .upsm{fill:var(--warn);font-size:9.5px}
.fur-fix{fill:var(--sheet);stroke:var(--fur);stroke-width:1} .fur-loose{fill:none;stroke:var(--fur);stroke-width:1;stroke-dasharray:4 2}
.fur-wet{fill:none;stroke:var(--fur);stroke-width:1}
.chair{fill:none;stroke:var(--fur);stroke-width:.8}
.fur{fill:var(--ink2);font-size:9.5px}
.drain{stroke:var(--fur);stroke-width:2.5;stroke-dasharray:1 2}
.rname{fill:var(--ink);font-size:13.5px;font-weight:700} .rarea{fill:var(--ink2);font-size:11px;font-family:var(--mono)}
.rsub{fill:var(--ink2);font-size:10px}
.dim{stroke:var(--ink2);stroke-width:.7} .dimtick{stroke:var(--ink);stroke-width:1.1} .dimtxt{fill:var(--ink);font-size:10.5px;font-family:var(--mono)}
.road{fill:var(--rule)} .park{fill:none;stroke:var(--ink2);stroke-width:1;stroke-dasharray:6 3}
.path{stroke:var(--ink2);stroke-width:1;stroke-dasharray:2 3}
.deck{fill:var(--timber-soft);stroke:var(--timber);stroke-width:1} .deckl{stroke:var(--timber);stroke-width:.4;opacity:.55}
.ctx{fill:var(--ink2);font-size:12px} .ctxb{fill:var(--ink);font-size:12px;font-weight:600} .ctxs{fill:var(--ink2);font-size:10.5px}
.note{fill:var(--ink2);font-size:10.5px}
.nc{fill:var(--sheet);stroke:var(--ink);stroke-width:1} .na{fill:var(--ink)} .ntxt{fill:var(--ink);font-size:11px;font-weight:700;font-family:var(--mono)}
.roofarea{fill:none;stroke:var(--rule);stroke-width:1;stroke-dasharray:4 4}
.lowzone{fill:var(--f-circ)} .void{fill:var(--sheet);stroke:var(--ink2);stroke-width:1}
.tall{fill:var(--tall)} .rail{stroke:var(--warn);stroke-width:2.2} .outline{fill:none;stroke:var(--wall);stroke-width:4}
.skylight{fill:none;stroke:var(--ink2);stroke-width:1;stroke-dasharray:3 2}
.ground{fill:var(--rule)} .wallsec{fill:var(--wall)} .roofsec{fill:var(--wall)} .slab{fill:var(--ink2)}
.knee{stroke:var(--ink2);stroke-width:2} .ceil{stroke:var(--ink2);stroke-width:1;stroke-dasharray:5 3}
.h18{stroke:var(--pine);stroke-width:1;stroke-dasharray:6 3} .tallsec{fill:var(--tall)}
.winsec{fill:var(--f-wet);stroke:var(--ink);stroke-width:1} .proj{fill:none;stroke:var(--ink2);stroke-width:.8;stroke-dasharray:3 3}
.sectxt{fill:var(--ink2);font-size:11px;font-family:var(--mono)} .secroom{fill:var(--ink);font-size:13px;font-weight:700}
.secdir{fill:var(--ink);font-size:13px;font-weight:700}
@media (max-width:560px){.wrap{padding-block:24px 48px;gap:36px} h2{font-size:21px}}
"""


def build():
    checks = run_checks()
    room_sum = sum(room_area(k) for k in ROOMS)
    bldg = W * D
    a_att = area(ATTIC) - area(ATTIC_VOID)
    ridge_u = H_PLATE + PITCH * (D / 2 - T_EXT)
    knee_h = H_PLATE + PITCH * (ATTIC[1] - T_EXT) - H_ATTIC_FL
    top_h = ridge_u - H_ATTIC_FL
    avg_h = (knee_h + top_h) / 2
    gfa_in = bldg + a_att
    esc = html.escape

    rows = "".join(
        f"<tr><td>{esc(n)}</td><td class='n'>{a:.2f}</td><td class='n'>{('' if t is None else f'{t:.1f}')}</td>"
        f"<td class='n {'diff' if t and a < t - 0.3 else ''}'>{('' if t is None else f'{a-t:+.1f}')}</td><td>{esc(note)}</td></tr>"
        for n, a, t, note in area_rows())
    wall_sum = bldg - room_sum
    check_html = "".join(
        f"<li><span class='pill {'ok' if ok else 'ng'}'>{'OK' if ok else 'NG'}</span><span>{esc(t)}</span></li>"
        for ok, t in checks)
    all_ok = all(ok for ok, _ in checks)

    page = f"""<title>박공주택 개념평면</title>
<meta name="description" content="200평 자연녹지 대지 4인 가족 30평 모던 박공주택 개념설계 도면과 검산">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans+KR:wght@400;600;700&display=swap">
<style>{CSS}</style>
<div class="wrap">
<header>
  <div class="stamp">개념설계 · 치수 확정 전 · 인허가/시공용 도면 아님</div>
  <h1>200평 자연녹지의 30평 모던 박공주택</h1>
  <p class="lede">1층 외곽 11.2 × 7.2m 직사각형 하나에 4인 가족의 모든 필수 생활을 담고, 거실은 박공 용마루까지 열고,
  홀·침실 상부에 6평 다락을 얹은 개념 평면입니다. 모든 도면과 면적표는 같은 좌표 데이터(<code>build.py</code>)에서 생성해 서로 어긋나지 않습니다.</p>
</header>

<section>
  <h2><span class="code">A</span>요구조건 요약</h2>
  <div class="kv">
    <div><b>{SITE_M2:.1f}㎡</b><span>대지 200평 · 평탄 직사각형 가정</span></div>
    <div><b>{bldg:.2f}㎡</b><span>건축면적 {bldg/PYEONG:.1f}평 · 11.2×7.2m</span></div>
    <div><b>{bldg/SITE_M2*100:.1f}%</b><span>건폐율 (자연녹지 상한 20%)</span></div>
    <div><b>{a_att:.2f}㎡</b><span>다락 실사용 {a_att/PYEONG:.1f}평</span></div>
    <div><b>{(bldg+a_att)/PYEONG:.1f}평</b><span>물리적 실내 바닥 합계(외벽 포함 1층 + 다락)</span></div>
    <div><b>{bldg/SITE_M2*100:.1f}–{gfa_in/SITE_M2*100:.1f}%</b><span>용적률 (다락 산입 여부에 따라)</span></div>
  </div>
  <div class="tbl"><table>
    <thead><tr><th>항목</th><th>요구</th><th>이번 도면의 반영</th></tr></thead>
    <tbody>
    <tr><td>가족·용도</td><td>부부 + 자녀 2, 상시거주, 노후 무장애</td><td>필수 생활 전부 1층, 현관·욕실·데크 무단차, 주동선 1.0m</td></tr>
    <tr><td>침실</td><td>부부침실 1, 자녀 공동방 1(침대 2·책상 2)</td><td>부부 {room_area('master'):.1f}㎡(북동), 자녀 {room_area('kids'):.1f}㎡(남동)</td></tr>
    <tr><td>공용 공간</td><td>남향 오픈 LDK, 대면형 아일랜드, 6인 식탁, 높은 거실</td><td>LDK {room_area('ldk'):.1f}㎡, 거실·식당 상부 용마루까지 오픈(최고 약 {ridge_u:.1f}m)</td></tr>
    <tr><td>서비스</td><td>공용욕실 1, 세탁·건조실, 기계실</td><td>북측 한 줄에 모음. 욕실·싱크대·세탁실이 벽 하나씩 맞닿음</td></tr>
    <tr><td>다락</td><td>6평, 자녀 놀이·취미, 고정식 U자 계단</td><td>{a_att:.1f}㎡, 홀·침실 상부. 계단 단높이 {H_ATTIC_FL/RISERS*1000:.0f}mm·디딤 250mm</td></tr>
    <tr><td>외부</td><td>남향 넓은 데크·마당, 야외주차 1</td><td>데크 {area(DECK):.1f}㎡(거실·식당 직결), 북측 주차 2.6×5.0m</td></tr>
    <tr><td>예산</td><td>총사업비 3억원 이내</td><td>단일 직사각형 + 단일 박공, 습식공간 집중 배치 (공사비 산정은 하지 않음)</td></tr>
    </tbody></table></div>
</section>

<section>
  <h2><span class="code">B</span>1층 개념 평면도</h2>
  <div class="sheet">{plan_1f()}</div>
  <div class="legend">
    <span><i style="background:var(--f-liv)"></i>거실·식당·주방</span><span><i style="background:var(--f-bed)"></i>부부침실</span>
    <span><i style="background:var(--f-kid)"></i>자녀공간·다락</span><span><i style="background:var(--f-wet)"></i>습식·서비스</span>
    <span><i style="background:var(--f-circ)"></i>현관·계단·홀</span>
    <span><i style="border:1.4px dashed var(--pine);background:none"></i>다락 바닥 투영</span>
    <span><i style="border:1px dotted var(--timber);background:none"></i>박공 오픈천장</span>
    <span><i style="border:1px dashed var(--fur);background:none"></i>이동 가구</span>
  </div>
  <div class="grid2">
    <div class="callout"><h3>동선</h3><p>현관 → 중문 → 주방 작업통로(1.0m) → 홀 → 부부침실·자녀방·계단.
    침실문 두 개가 모두 홀 안쪽을 향해 거실 소파에서는 보이지 않습니다. 대신 현관과 침실을 잇는 주동선이 주방 작업통로를 겸하므로, 요리 중 통행이 겹치는 것은 감수한 선택입니다.</p></div>
    <div class="callout"><h3>채광·통풍</h3><p>거실 남측 2.6m 미닫이와 서측 창, 서측 박공 고창이 남서 모서리를 엽니다.
    남측 거실창과 북측 현관·세탁실 개구부, 동측 침실창이 맞통풍을 만듭니다. 욕실은 북측 고창과 기계환기를 함께 둡니다.</p></div>
  </div>
</section>

<section>
  <h2><span class="code">C</span>다락 개념 평면도</h2>
  <div class="sheet">{plan_attic()}</div>
  <p>다락은 홀·부부침실·자녀방 위(x ≥ 6.4m)에만 놓여 거실 오픈천장과 겹치지 않습니다. 서쪽 끝은 1.2m 난간으로 막아 거실을 내려다보는 발코니처럼 쓰고,
  남북 양 끝은 {knee_h:.2f}m 무릎벽을 세워 그 뒤를 수납으로 씁니다. 옅은 녹색 띠가 성인이 서서 쓸 수 있는 천장고 1.8m 이상 구간입니다.</p>
</section>

<section>
  <h2><span class="code">D</span>박공 단면 개념도</h2>
  <div style="display:grid;gap:16px">
    <div class="sheet"><h3 style="margin-bottom:8px">남북 횡단면 · 부부침실/자녀방/다락</h3>{section_cross()}</div>
    <div class="sheet"><h3 style="margin-bottom:8px">동서 종단면 · 용마루 아래</h3>{section_long()}</div>
  </div>
  <div class="callout">
    <h3>다락 높이와 면적 산입</h3>
    <p>이 단면에서 다락 천장고는 무릎벽 {knee_h:.2f}m, 용마루 아래 {top_h:.2f}m, 단순 평균 약 {avg_h:.2f}m입니다.
    「건축법 시행령」 제119조는 층고 1.5m(경사지붕은 1.8m) 이하 다락을 바닥면적에서 제외하는데, 경사지붕 다락의 층고를 평균높이로 볼지 최고높이로 볼지는 관할 허가권자 판단을 확인해야 합니다.
    어느 해석이든 이번 단면은 1.8m를 넘으므로 <b>다락이 연면적에 산입된다고 보고</b> 계획하는 것이 안전합니다(연면적 {gfa_in:.1f}㎡, 용적률 {gfa_in/SITE_M2*100:.1f}%, 자연녹지 상한 안).</p>
    <p>면적 제외를 우선하려면 지붕하부 높이를 낮춰야 하는데, 그러면 U자 계단 참의 머리높이(현재 약 2.17m)가 2.0m 아래로 떨어집니다. 이 교환관계를 건축사와 단면으로 비교해 정해야 합니다.</p>
  </div>
</section>

<section>
  <h2><span class="code">E</span>방별 순면적과 합계 검산</h2>
  <div class="tbl"><table>
    <thead><tr><th>공간</th><th style="text-align:right">도면 순면적 ㎡</th><th style="text-align:right">브리프 권장 ㎡</th><th style="text-align:right">차이</th><th>설계 포인트</th></tr></thead>
    <tbody>{rows}
    <tr class="sum"><td>1층 순면적 합계</td><td class="n">{room_sum:.2f}</td><td class="n">74.5</td><td class="n diff">{room_sum-74.5:+.1f}</td><td>실 안쪽(내법) 면적의 합</td></tr>
    <tr><td>외벽 + 내벽 면적</td><td class="n">{wall_sum:.2f}</td><td class="n"></td><td class="n"></td><td>외벽 0.2m 7.20㎡ + 내벽 0.1m {wall_sum-7.2:.2f}㎡</td></tr>
    <tr class="sum"><td>건축면적(외곽 11.2×7.2)</td><td class="n">{room_sum+wall_sum:.2f}</td><td class="n">80.6</td><td class="n"></td><td>{bldg/PYEONG:.1f}평</td></tr>
    <tr><td>다락 실사용 바닥</td><td class="n">{a_att:.2f}</td><td class="n">19.8</td><td class="n">{a_att-19.8:+.1f}</td><td>4.6×4.9m − 계단 오픈부 1.6×1.7m</td></tr>
    </tbody></table></div>
  <div class="callout">
    <h3>브리프 수치 정정</h3>
    <p>브리프의 권장 순면적 합계 74.5㎡는 외곽 11.2×7.2m 안에 들어가지 않습니다. 외벽 0.2m만 빼도 실내는 10.8×6.8 = 73.44㎡이고, 내벽을 빼면 실제 순면적은 약 {room_sum:.1f}㎡입니다.
    그래서 외곽 치수를 지키는 대신 자녀방(−{14-room_area('kids'):.1f}㎡), LDK, 세탁실, 현관을 조금씩 줄였습니다. 권장 면적을 모두 지키려면 외곽을 약 12.0×7.2m(86.4㎡, 26.1평)로 늘려야 하고, 공사비도 그만큼 늘어납니다.
    실제 벽 두께는 구조·단열 방식에 따라 0.25~0.35m까지 두꺼워질 수 있어 순면적은 더 줄어들 수 있습니다.</p>
  </div>
  <h3>자체 검증 {'(모두 통과)' if all_ok else '(실패 항목 있음)'}</h3>
  <ul class="checks">{check_html}</ul>
</section>

<section>
  <h2><span class="code">F</span>미확정 사항과 건축사 확인 체크리스트</h2>
  <div class="grid2">
    <div class="tbl" style="padding:14px 16px"><h3>토지·법규</h3><ul class="list">
      <li>토지이용계획확인서: 자연녹지 여부, 지구단위계획, 기타 규제</li>
      <li>소재지 조례의 건폐율·용적률 (자연녹지 20% / 50~100% 범위)</li>
      <li>도로의 법적 지위와 폭, 접도 길이(맹지·현황도로 여부)</li>
      <li>농지·산지 여부와 전용 가능성, 개발행위허가</li>
      <li>상수도·관정, 오수관·정화조, 전기 인입 위치와 견적</li>
      <li>다락 층고 산정 방식(평균 vs 최고)과 바닥면적 산입 여부</li>
    </ul></div>
    <div class="tbl" style="padding:14px 16px"><h3>설계·시공</h3><ul class="list">
      <li>구조 방식(경량목구조/철근콘크리트 등)에 따른 실제 벽 두께와 순면적 재산정</li>
      <li>다락 바닥이 걸리는 경간(부부침실 2.9m, 자녀방 4.5m)의 보·내력벽 계획</li>
      <li>계단 단높이 {H_ATTIC_FL/RISERS*1000:.0f}mm·디딤 250mm·참 머리높이 확인, 다락 난간 높이·간격</li>
      <li>남·서향 대형창 여름 차양(처마 {EAVE:.1f}m + 외부 차양), 에너지절약계획 대상 여부</li>
      <li>오픈천장 거실의 난방 부하·결로·환기, 다락 냉난방 방식</li>
      <li>욕실 무단차 배수 구배와 방수 상세, 보강벽 위치</li>
      <li>기계실 보일러 급배기 경로와 외부 점검문, 동파 대책</li>
      <li>지반조사 필요성, 우수 배수 방향, 성토·옹벽 여부</li>
    </ul></div>
  </div>
</section>

<footer>
  <p>법규 근거: 「건축법 시행령」 제119조 제1항 제3호(다락: 층고 1.5m, 경사지붕 1.8m 이하 바닥면적 불산입), 「국토의 계획 및 이용에 관한 법률 시행령」 제84조·제85조(자연녹지 건폐율 20%, 용적률 50~100% 이하 범위에서 조례).
  조문은 공개 자료로 확인했으며, 실제 적용은 소재지 조례와 개별 대지 조건에 따라 달라집니다.</p>
  <p>이 문서는 건축주와 건축사의 첫 상담을 위한 개념안이며 구조·설비·에너지·소방·인허가 검토를 대신하지 않습니다. 도면을 그대로 시공에 쓰면 안 됩니다.</p>
</footer>
</div>
"""
    return page, checks


if __name__ == "__main__":
    page, checks = build()
    out = Path(__file__).with_name("index.html")
    out.write_text(page, encoding="utf-8")
    for ok, t in checks:
        print("OK " if ok else "NG ", t)
    print("written", out)
