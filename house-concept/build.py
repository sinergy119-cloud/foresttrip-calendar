"""200평 자연녹지 모던 박공주택 개념설계 2차안 도면 생성기.

좌표계: 미터, 원점 = 건물 외벽 북서쪽 모서리. x 동쪽(+), y 남쪽(+).
평면·단면·면적표·검증은 모두 아래 데이터 하나에서 나온다.
실행: python3 build.py  →  index.html 생성 + 검증 결과 출력
(1차안 11.2×7.2m 은 git 이력에 남아 있다)
"""
from __future__ import annotations

import html
import math
from pathlib import Path

HERE = Path(__file__).parent

# ---------------------------------------------------------------- 기본 치수
W, D = 11.6, 7.8          # 외곽(외벽 외측) 동서 × 남북  (1차안 11.2 × 7.2)
T_EXT, T_INT = 0.2, 0.1
PYEONG = 3.305785
SITE_M2 = 200 * PYEONG

H_CEIL = 2.40      # 평천장(북측 서비스열·홀·침실)
H_ATTIC_FL = 2.70  # 다락 바닥
H_PLATE = 3.20     # 외벽 내측면의 지붕 하부 높이
PITCH = 0.70       # 물매 tan ≈ 35°
ROOF_T = 0.35
EAVE = 0.60
GL = -0.15
RISERS = 16
TREAD = 0.25
IX0, IX1, IY0, IY1 = T_EXT, W - T_EXT, T_EXT, D - T_EXT   # 실내 경계

# ---------------------------------------------------------------- 실
ROOMS = {
    "util":   dict(name="다용도(세탁·기계)", short="다용도", rects=[(0.2, 0.2, 2.0, 2.2)], kind="wet"),
    "bath":   dict(name="공용욕실", rects=[(2.1, 0.2, 4.5, 2.2)], kind="wet"),
    "entry":  dict(name="현관", rects=[(4.6, 0.2, 6.2, 2.2)], kind="circ"),
    "stair":  dict(name="U자 계단", rects=[(6.3, 0.2, 8.2, 2.85)], kind="circ"),
    "hall":   dict(name="홀", rects=[(3.7, 2.3, 6.2, 3.95), (6.2, 2.85, 8.2, 3.95)], kind="circ"),
    "master": dict(name="부부침실", rects=[(8.3, 0.2, 11.4, 3.95)], kind="bed"),
    "kids":   dict(name="자녀 공동방", rects=[(7.3, 4.05, 11.4, 7.6)], kind="kid"),
    "ldk":    dict(name="거실·식당·주방", rects=[(0.2, 2.3, 3.6, 7.6), (3.6, 4.05, 7.2, 7.6)], kind="living"),
}
INT_WALLS = [
    (0.2, 2.2, 6.2, 2.3),     # 북측 서비스열 남측벽
    (2.0, 0.2, 2.1, 2.2),     # 다용도|욕실
    (4.5, 0.2, 4.6, 2.2),     # 욕실|현관
    (6.2, 0.2, 6.3, 2.85),    # 현관·홀|계단
    (8.2, 0.2, 8.3, 3.95),    # 계단·홀|부부침실
    (3.6, 2.3, 3.7, 3.95),    # 주방|홀 (개구부 있음)
    (3.6, 3.95, 11.4, 4.05),  # 홀·부부침실|거실·자녀방
    (7.2, 4.05, 7.3, 7.6),    # 거실|자녀방
]
FURN = [
    ("util", "세탁·건조", (0.25, 0.25, 0.95, 0.95), "fix"),
    ("util", "보일러", (1.5, 0.3, 2.0, 0.8), "fix"),
    ("util", "팬트리", (1.6, 1.0, 2.0, 2.2), "fix"),
    ("bath", "무단차 샤워", (2.1, 0.2, 3.3, 1.2), "wet"),
    ("bath", "세면대", (3.45, 0.2, 4.45, 0.7), "fix"),
    ("bath", "변기", (2.2, 1.45, 2.65, 2.2), "fix"),
    ("entry", "신발장", (4.6, 0.8, 5.0, 2.2), "fix"),
    ("hall", "외투 수납", (4.8, 3.35, 6.2, 3.95), "fix"),
    ("ldk", "싱크대", (1.2, 2.3, 2.8, 2.9), "fix"),
    ("ldk", "냉장고", (2.8, 2.3, 3.6, 3.0), "fix"),
    ("ldk", "아일랜드(쿡탑)", (1.1, 3.9, 3.1, 4.8), "fix"),
    ("ldk", "6인 식탁", (0.9, 5.6, 2.7, 6.5), "loose"),
    ("ldk", "소파", (3.8, 4.6, 4.7, 6.8), "loose"),
    ("ldk", "TV", (6.75, 4.9, 7.2, 6.5), "fix"),
    ("master", "퀸 침대", (9.1, 0.2, 10.6, 2.2), "loose"),
    ("master", "붙박이장", (9.2, 3.35, 11.4, 3.95), "fix"),
    ("kids", "싱글침대", (9.4, 4.05, 11.4, 5.05), "loose"),
    ("kids", "싱글침대", (9.4, 6.6, 11.4, 7.6), "loose"),
    ("kids", "책상", (7.35, 7.0, 8.35, 7.6), "loose"),
    ("kids", "책상", (8.35, 7.0, 9.35, 7.6), "loose"),
    ("kids", "옷장", (7.3, 4.95, 7.9, 6.35), "fix"),
]
CHAIRS = [("ldk", "의자열(북)", (0.9, 5.05, 2.7, 5.6)), ("ldk", "의자열(남)", (0.9, 6.5, 2.7, 7.05)),
          ("kids", "책상 의자", (7.45, 6.45, 9.25, 7.0))]
DOORS = [
    dict(name="현관문", x=4.9, y=0.0, w=1.0, wall="h", side=-1, kind="swing"),
    dict(name="현관 중문", x=4.75, y=2.2, w=1.3, wall="h", side=1, kind="slide"),
    dict(name="다용도 외부문", x=0.95, y=0.0, w=0.8, wall="h", side=-1, kind="swing"),
    dict(name="다용도→주방", x=0.3, y=2.2, w=0.85, wall="h", side=1, kind="slide"),
    dict(name="욕실문", x=3.7, y=2.2, w=0.8, wall="h", side=1, kind="slide"),
    dict(name="부부침실문", x=8.2, y=2.95, w=0.85, wall="v", side=1, kind="swing"),
    dict(name="자녀방문", x=7.35, y=3.95, w=0.85, wall="h", side=1, kind="swing"),
]
OPENINGS = [(3.6, 2.95, 3.7, 3.95), (3.7, 3.95, 4.7, 4.05)]  # 홀→주방, 홀→거실 (문 없는 개구부)
WINDOWS = [
    ("N", 2.3, 3.1, "고창"), ("N", 6.6, 7.9, "계단창"), ("N", 9.4, 10.4, "고창"),
    ("E", 1.2, 2.6, "창"), ("E", 5.3, 6.3, "창"),
    ("S", 0.5, 3.0, "창"), ("S", 3.9, 7.0, "대형 미닫이"), ("S", 7.6, 9.2, "창"),
    ("W", 3.2, 4.4, "창"), ("W", 5.4, 6.8, "창"),
]
ATTIC_X0 = 7.3
ATTIC_K = 1.12                        # 외벽 내측면에서 무릎벽까지
ATTIC = (ATTIC_X0, IY0 + ATTIC_K, IX1, IY1 - ATTIC_K)
ATTIC_VOID = (ATTIC_X0, ATTIC[1], 8.2, 2.85)
DECK = (0.0, D, 7.6, D + 3.0)
PARK = (4.2, -7.3, 6.8, -2.3)


# ---------------------------------------------------------------- 계산 헬퍼
def area(r):
    return (r[2] - r[0]) * (r[3] - r[1])


def room_area(k):
    return sum(area(r) for r in ROOMS[k]["rects"])


def overlap(a, b):
    return min(a[2], b[2]) - max(a[0], b[0]) > 1e-6 and min(a[3], b[3]) - max(a[1], b[1]) > 1e-6


def inside(r, rects, step=0.05):
    x = r[0] + step / 2
    while x < r[2]:
        y = r[1] + step / 2
        while y < r[3]:
            if not any(q[0] <= x <= q[2] and q[1] <= y <= q[3] for q in rects):
                return False
            y += step
        x += step
    return True


def is_ext(d):
    return d["wall"] == "h" and d["y"] == 0.0


def door_zone(d):
    w = d["w"]
    t = T_EXT if is_ext(d) else T_INT
    if d["wall"] == "h":
        if d["side"] > 0:
            y0 = d["y"] + t
            return (d["x"], y0, d["x"] + w, y0 + (w if d["kind"] == "swing" else 0.6))
        return (d["x"], d["y"] - w, d["x"] + w, d["y"])
    x0 = d["x"] + t
    return (x0, d["y"], x0 + (w if d["kind"] == "swing" else 0.6), d["y"] + w)


def roof_under(y):
    return H_PLATE + PITCH * min(y - IY0, IY1 - y)


RIDGE_U = H_PLATE + PITCH * ((IY1 - IY0) / 2)
F: dict[str, list] = {}
for _k, _n, _r, _ in FURN:
    F.setdefault(_n, []).append(_r)


def win_len(side, lo, hi):
    return sum(max(0.0, min(b, hi) - max(a, lo)) for s_, a, b, _ in WINDOWS if s_ == side)


# ---------------------------------------------------------------- 검증
def run_checks():
    res = []

    def add(ok, text):
        res.append((ok, text))

    rects = [(0, 0, W, T_EXT), (0, D - T_EXT, W, D), (0, T_EXT, T_EXT, D - T_EXT), (W - T_EXT, T_EXT, W, D - T_EXT)]
    rects += INT_WALLS
    for k in ROOMS:
        rects += ROOMS[k]["rects"]
    step, bad, n = 0.05, 0, 0
    for i in range(int(round(W / step))):
        for j in range(int(round(D / step))):
            x, y = (i + 0.5) * step, (j + 0.5) * step
            c = sum(1 for r in rects if r[0] <= x <= r[2] and r[1] <= y <= r[3])
            n += 1
            bad += c != 1
    add(bad == 0, f"실 + 벽체가 {W}×{D}m 외곽을 빈틈·중복 없이 채움 (5cm 격자 {n}칸 중 오류 {bad}칸)")
    room_sum = sum(room_area(k) for k in ROOMS)
    wall_sum = sum(area(r) for r in INT_WALLS) + (W * D - (IX1 - IX0) * (IY1 - IY0))
    add(abs(room_sum + wall_sum - W * D) < 1e-6, f"순면적 {room_sum:.2f}㎡ + 벽체 {wall_sum:.2f}㎡ = 건축면적 {W*D:.2f}㎡")

    items = [(k, n_, r) for k, n_, r, _ in FURN] + CHAIRS
    out = [n_ for k, n_, r in items if not inside(r, ROOMS[k]["rects"])]
    add(not out, "모든 가구가 해당 실 경계 안" + (f" (벗어남: {out})" if out else ""))
    clash = [(a[1], b[1]) for i, a in enumerate(items) for b in items[i + 1:]
             if a[0] == b[0] and overlap(a[2], b[2]) and {a[1], b[1]} != {"책상", "책상 의자"}]
    add(not clash, "가구끼리 겹침 없음" + (f" {clash}" if clash else ""))
    dclash = [(d["name"], n_) for d in DOORS for k, n_, r in items if overlap(door_zone(d), r)]
    add(not dclash, "문 개폐 영역에 가구 없음" + (f" {dclash}" if dclash else ""))

    isl, sink, sofa, table = F["아일랜드(쿡탑)"][0], F["싱크대"][0], F["소파"][0], F["6인 식탁"][0]
    add(isl[1] - sink[3] >= 1.0, f"주방 작업통로 {isl[1]-sink[3]:.2f}m, 현관·침실 동선이 지나가지 않음")
    add(isl[0] - IX0 >= 0.9, f"아일랜드 서측 통로 {isl[0]-IX0:.2f}m")
    add(table[1] - isl[3] >= 0.75, f"아일랜드~식탁 {table[1]-isl[3]:.2f}m (착석 공간)")
    tv = F["TV"][0]
    add(tv[0] - sofa[2] >= 2.0, f"TV~소파 시청거리 {tv[0]-sofa[2]:.2f}m (1차안 1.45m)")
    add(sofa[0] - table[2] >= 0.9, f"식탁 끝~소파 등 통로 {sofa[0]-table[2]:.2f}m")
    h1 = ROOMS["hall"]["rects"][0]
    coat = F["외투 수납"][0]
    add(coat[1] - h1[1] >= 1.0, f"홀 유효폭 {coat[1]-h1[1]:.2f}m (외투 수납 제외)")
    bed, ward = F["퀸 침대"][0], F["붙박이장"][0]
    m = ROOMS["master"]["rects"][0]
    side = min(bed[0] - m[0], m[2] - bed[2])
    add(ward[1] - bed[3] >= 0.9 and side >= 0.7, f"부부침실 침대 발치 {ward[1]-bed[3]:.2f}m, 침대 옆 {side:.2f}m")
    kb = F["싱글침대"]
    add(kb[1][1] - kb[0][3] >= 0.9, f"자녀방 침대 사이 {kb[1][1]-kb[0][3]:.2f}m")

    fr = F["냉장고"][0]
    s_ = ((sink[0] + sink[2]) / 2, sink[3])
    f_ = ((fr[0] + fr[2]) / 2, fr[3])
    c_ = ((isl[0] + isl[2]) / 2, isl[1])
    tri = math.dist(s_, f_) + math.dist(f_, c_) + math.dist(c_, s_)
    add(3.6 <= tri <= 6.6, f"주방 작업삼각형 합 {tri:.2f}m (권장 3.6~6.6m)")

    for k, pieces in (("master", [("E", 0.2, 3.95), ("N", 8.3, 11.4)]),
                      ("kids", [("S", 7.3, 11.4), ("E", 4.05, 7.6)]),
                      ("ldk", [("S", 0.2, 7.2), ("W", 2.3, 7.6)])):
        g = sum(win_len(sd, lo, hi) for sd, lo, hi in pieces) * 1.2
        a = room_area(k)
        add(g >= a / 10, f"{ROOMS[k]['name']} 채광창 약 {g:.1f}㎡ ≥ 바닥 1/10 ({a/10:.1f}㎡), 창 높이 1.2m 가정")

    rise = H_ATTIC_FL / RISERS
    add(abs(0.9 + (RISERS // 2 - 1) * TREAD - 2.65) < 1e-6,
        f"U자 계단 단높이 {rise*1000:.0f}mm × {RISERS}단, 디딤 {TREAD*1000:.0f}mm, 유효폭 0.90m")
    land_h = rise * RISERS / 2
    add(roof_under(0.65) - land_h >= 2.0, f"계단참 머리높이 {roof_under(0.65)-land_h:.2f}m")
    add(roof_under(2.6) - (H_ATTIC_FL - rise) >= 2.0, f"계단 상부 머리높이 {roof_under(2.6)-(H_ATTIC_FL-rise):.2f}m")
    a_att = area(ATTIC) - area(ATTIC_VOID)
    add(abs(a_att - 19.83) < 0.15, f"다락 실사용 바닥 {a_att:.2f}㎡ = {a_att/PYEONG:.2f}평")
    add(ATTIC_X0 >= 7.2, f"다락(x≥{ATTIC_X0}m)은 홀·침실 상부에만, LDK 오픈천장(x≤7.2m)과 겹치지 않음")
    return res, tri


# ---------------------------------------------------------------- 건축계획 기준 점검표
def criteria(room_sum, tri):
    return [
        ("조닝", "공적(LDK)·사적(침실)·서비스(욕실·세탁) 영역을 나누고, 현관에서 각 영역으로 바로 갈라져야 한다",
         "ng", "현관 → 주방 → 홀 → 침실. 침실 가는 길이 주방을 관통",
         "ok", "현관 → 홀에서 LDK·욕실·침실·계단으로 바로 분기"),
        ("동선 교차", "가족 동선(출입·침실)과 가사 동선(조리·세탁)이 겹치지 않아야 한다",
         "ng", "주방 작업통로가 현관~침실 주동선을 겸함",
         "ok", "주방 통로는 조리 전용. 세탁은 주방 뒤 다용도실에서 끝남"),
        ("욕실 접근", "침실에서 공적 공간을 거치지 않고 욕실에 가야 한다",
         "ng", "욕실문이 LDK 쪽으로 열림",
         "ok", "욕실문이 홀로 열림: 침실 → 홀 → 욕실"),
        ("현관 시선", "현관문을 열었을 때 거실 내부가 바로 보이지 않아야 한다",
         "mid", "중문 너머가 곧 거실·주방",
         "ok", "중문 앞은 홀. 거실은 홀 모서리 개구부로 비켜서 연결"),
        ("가사 동선", "주방과 다용도실이 붙고, 다용도실에서 밖으로 나갈 수 있어야 한다",
         "mid", "세탁실이 현관 옆, 주방과 떨어짐",
         "ok", "다용도실 → 주방 미닫이 직결 + 북측 외부문(쓰레기·보일러 점검)"),
        ("거실 치수", "TV~소파 2.0m 이상, 거실 한 변 3.5m 안팎",
         "ng", "거실 폭 약 2.9m, 시청거리 1.45m",
         "ok", "거실 3.6 × 3.55m, 시청거리 2.05m"),
        ("침실 소음", "침실 사이, 거실과 침실 사이에 수납 등 완충을 둔다",
         "mid", "일부만 완충",
         "ok", "부부침실 붙박이장은 자녀방 쪽 벽, 자녀방 옷장은 거실 TV 쪽 벽"),
        ("주방 작업삼각형", "싱크·냉장고·가열대 세 변의 합 3.6~6.6m",
         "ok", "약 5.8m",
         "ok", f"{tri:.1f}m (하한 근처, 동선 짧음)"),
        ("1인당 면적", "건축계획 교재에 흔히 인용되는 표준 약 16㎡/인 (4인 64㎡)",
         "ok", "순면적 71.1㎡ = 17.8㎡/인",
         "ok", f"순면적 {room_sum:.1f}㎡ = {room_sum/4:.1f}㎡/인"),
        ("최저주거기준", "4인 가구: 방 3개(거실 겸용 포함) + 부엌 겸 식당, 43㎡ 이상 (2011 국토부)",
         "ok", "침실 2 + 거실",
         "ok", "침실 2 + 거실"),
        ("자녀 침실 분리", "만 8세 이상 이성 자녀는 침실 분리 (최저주거기준 침실 기준으로 알려져 있음, 원문 확인 필요)",
         "mid", "공동방 1개, 자녀 성별·나이 미확인",
         "mid", "공동방 유지. 이성 자녀라면 다락을 한 명의 방으로 쓰는 안 등 검토 필요"),
        ("무장애", "주동선 0.9~1.2m, 문 유효폭 0.8m 이상, 무단차",
         "ok", "주동선 1.0m",
         "ok", "홀 유효폭 1.05m, 문 0.8~0.85m, 전 구간 무단차"),
    ]


# ---------------------------------------------------------------- SVG
S = 52


def fmt(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


class Svg:
    def __init__(self, ox, oy, w, h, title):
        self.ox, self.oy, self.w, self.h, self.title = ox, oy, w, h, title
        self.parts = []

    def X(self, x):
        return self.ox + x * S

    def Y(self, y):
        return self.oy + y * S

    def rect(self, r, cls):
        self.parts.append(f'<rect class="{cls}" x="{self.X(r[0]):.1f}" y="{self.Y(r[1]):.1f}" '
                          f'width="{(r[2]-r[0])*S:.1f}" height="{(r[3]-r[1])*S:.1f}"/>')

    def line(self, x1, y1, x2, y2, cls):
        self.parts.append(f'<line class="{cls}" x1="{self.X(x1):.1f}" y1="{self.Y(y1):.1f}" '
                          f'x2="{self.X(x2):.1f}" y2="{self.Y(y2):.1f}"/>')

    def poly(self, pts, cls, marker=None):
        d = "M" + " L".join(f"{self.X(a):.1f} {self.Y(b):.1f}" for a, b in pts)
        m = f' marker-end="url(#{marker})"' if marker else ""
        self.parts.append(f'<path class="{cls}" d="{d}"{m}/>')

    def text(self, x, y, s, cls, anchor="middle", rot=None):
        tr = f' transform="rotate({rot} {self.X(x):.1f} {self.Y(y):.1f})"' if rot else ""
        self.parts.append(f'<text class="{cls}" x="{self.X(x):.1f}" y="{self.Y(y):.1f}" '
                          f'text-anchor="{anchor}"{tr}>{html.escape(s)}</text>')

    def raw(self, s):
        self.parts.append(s)

    def dim_h(self, x1, x2, y, label=None, t=0.12):
        self.line(x1, y, x2, y, "dim")
        for x in (x1, x2):
            self.line(x - t / 2, y + t / 2, x + t / 2, y - t / 2, "dimtick")
        self.text((x1 + x2) / 2, y - 0.08, label or fmt(x2 - x1), "dimtxt")

    def dim_v(self, y1, y2, x, label=None, t=0.12):
        self.line(x, y1, x, y2, "dim")
        for y in (y1, y2):
            self.line(x - t / 2, y + t / 2, x + t / 2, y - t / 2, "dimtick")
        self.text(x - 0.08, (y1 + y2) / 2, label or fmt(y2 - y1), "dimtxt", rot=-90)

    def north(self, x, y):
        cx, cy = self.X(x), self.Y(y)
        self.raw(f'<g><circle cx="{cx}" cy="{cy}" r="17" class="nc"/>'
                 f'<path d="M{cx} {cy-14} L{cx+7} {cy+9} L{cx} {cy+4} L{cx-7} {cy+9} Z" class="na"/>'
                 f'<text x="{cx}" y="{cy-21}" text-anchor="middle" class="ntxt">N</text></g>')

    def out(self):
        mk = lambda i, c, sz: (f'<marker id="{i}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="{sz}" '
                               f'markerHeight="{sz}" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" class="{c}"/></marker>')
        defs = "<defs>" + mk("ah", "ahp", 7) + mk("ahg", "ahg", 6) + mk("ahk", "ahk", 6) + "</defs>"
        return (f'<svg viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{html.escape(self.title)}" '
                f'xmlns="http://www.w3.org/2000/svg"><title>{html.escape(self.title)}</title>{defs}'
                + "".join(self.parts) + "</svg>")


def draw_door(s, d):
    w = d["w"]
    t = T_EXT if is_ext(d) else T_INT
    if d["kind"] == "slide":
        if d["wall"] == "h":
            s.rect((d["x"], d["y"], d["x"] + w, d["y"] + t), "open")
            s.line(d["x"], d["y"] + 0.03, d["x"] + w * 0.6, d["y"] + 0.03, "door")
            s.line(d["x"] + w * 0.4, d["y"] + 0.07, d["x"] + w, d["y"] + 0.07, "door")
        else:
            s.rect((d["x"], d["y"], d["x"] + t, d["y"] + w), "open")
            s.line(d["x"] + 0.03, d["y"], d["x"] + 0.03, d["y"] + w * 0.6, "door")
            s.line(d["x"] + 0.07, d["y"] + w * 0.4, d["x"] + 0.07, d["y"] + w, "door")
        return
    if d["wall"] == "h":
        s.rect((d["x"], d["y"], d["x"] + w, d["y"] + t), "open")
        yb = d["y"] + (t if d["side"] > 0 else 0)
        yl = yb + d["side"] * w
        s.line(d["x"], yb, d["x"], yl, "door")
        s.raw(f'<path class="swing" d="M{s.X(d["x"]):.1f} {s.Y(yl):.1f} A{w*S:.1f} {w*S:.1f} 0 0 '
              f'{0 if d["side"] > 0 else 1} {s.X(d["x"]+w):.1f} {s.Y(yb):.1f}"/>')
    else:
        s.rect((d["x"], d["y"], d["x"] + t, d["y"] + w), "open")
        xb = d["x"] + t
        s.line(xb, d["y"], xb + w, d["y"], "door")
        s.raw(f'<path class="swing" d="M{s.X(xb+w):.1f} {s.Y(d["y"]):.1f} A{w*S:.1f} {w*S:.1f} 0 0 1 '
              f'{s.X(xb):.1f} {s.Y(d["y"]+w):.1f}"/>')


def draw_window(s, wdw):
    side, a, b, _ = wdw
    if side in "NS":
        y0 = 0 if side == "N" else D - T_EXT
        s.rect((a, y0, b, y0 + T_EXT), "win")
        s.line(a, y0 + T_EXT / 2, b, y0 + T_EXT / 2, "winl")
    else:
        x0 = 0 if side == "W" else W - T_EXT
        s.rect((x0, a, x0 + T_EXT, b), "win")
        s.line(x0 + T_EXT / 2, a, x0 + T_EXT / 2, b, "winl")


def label(s, k, cx, cy, dims=None):
    s.text(cx, cy, ROOMS[k].get("short", ROOMS[k]["name"]), "rname")
    s.text(cx, cy + 0.32, f"{room_area(k):.1f}㎡" + (f" · {dims}" if dims else ""), "rarea")


def plan_1f():
    s = Svg(ox=70, oy=470, w=780, h=1110, title="2차안 1층 개념 평면도")
    s.rect((-1.0, -8.3, W + 1.0, -7.5), "road")
    s.text(W / 2, -7.78, "북측 진입도로 (가정)", "ctx")
    s.rect(PARK, "park")
    s.text((PARK[0] + PARK[2]) / 2, -4.9, "야외주차", "ctxb")
    s.text((PARK[0] + PARK[2]) / 2, -4.55, "2.6×5.0m", "ctxs")
    s.rect(DECK, "deck")
    y = DECK[1] + 0.12
    while y < DECK[3]:
        s.line(DECK[0], y, DECK[2], y, "deckl")
        y += 0.12
    s.text(3.8, D + 1.5, f"남향 데크 약 {area(DECK):.0f}㎡ (7.6×3.0m)", "ctxb")
    s.text(3.8, D + 1.9, "식당·거실에서 무단차로 연결", "ctxs")
    s.text(9.6, D + 1.7, "남측 마당 · 텃밭", "ctx")

    s.rect((0, 0, W, D), "wall")
    fills = {"circ": "f-circ", "wet": "f-wet", "bed": "f-bed", "kid": "f-kid", "living": "f-liv"}
    for k, r in ROOMS.items():
        for q in r["rects"]:
            s.rect(q, "floor " + fills[r["kind"]])
    for o in OPENINGS:
        s.rect(o, "floor f-circ")
    s.rect((IX0, 2.3, 7.2, IY1), "openceil")
    s.rect(ATTIC, "attic-proj")
    s.text(IX1 - 0.1, ATTIC[1] + 1.95, "다락 바닥 투영", "projtxt", anchor="end")
    for w_ in WINDOWS:
        draw_window(s, w_)
    for d in DOORS:
        draw_door(s, d)
    for i in range(RISERS // 2):
        yy = 2.85 - i * TREAD
        s.line(6.3, yy, 7.2, yy, "tread")
        s.line(7.3, yy, 8.2, yy, "tread")
    s.line(6.3, 1.1, 8.2, 1.1, "tread")
    s.line(7.25, 1.1, 7.25, 2.85, "stairmid")
    s.poly([(6.75, 2.75), (6.75, 0.65), (7.75, 0.65), (7.75, 2.7)], "arrow", "ah")
    s.text(6.75, 3.15, "UP", "up")
    for k, n_, r, st in FURN:
        s.rect(r, "fur-" + st)
        cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
        vertical = (r[3] - r[1]) > (r[2] - r[0]) * 1.4 and (r[2] - r[0]) < 0.8
        s.text(cx, cy + 0.07, n_, "fur", rot=-90 if vertical else None)
    for k, n_, r in CHAIRS[:2]:
        w_ = (r[2] - r[0]) / 3
        for i in range(3):
            s.rect((r[0] + i * w_ + 0.08, r[1] + 0.05, r[0] + (i + 1) * w_ - 0.08, r[3] - 0.05), "chair")
    for x0 in (7.6, 8.6):
        s.rect((x0, 6.5, x0 + 0.5, 6.95), "chair")
    s.line(2.15, 1.12, 3.25, 1.12, "drain")
    # 동선
    s.poly([(5.4, -2.1), (5.4, 3.0), (7.9, 3.0), (7.9, 3.4), (8.8, 3.4)], "flow", "ahg")
    s.poly([(7.9, 3.4), (7.9, 4.6)], "flow", "ahg")
    s.poly([(5.4, 3.0), (4.1, 3.0), (4.1, 2.45)], "flow", "ahg")
    s.poly([(4.35, 3.05), (4.35, 4.45)], "flow", "ahg")
    s.poly([(0.6, 1.3), (0.6, 3.4), (1.8, 3.4)], "flowk", "ahk")
    s.poly([(1.35, 1.1), (1.35, -0.6)], "flowk", "ahk")

    label(s, "util", 1.0, 1.65)
    label(s, "bath", 3.55, 1.6)
    s.text(5.85, 1.05, "현관", "rname")
    s.text(5.85, 1.37, f"{room_area('entry'):.1f}㎡", "rarea")
    label(s, "master", 9.95, 2.6, "3.1×3.75")
    label(s, "kids", 8.65, 5.55)
    s.text(4.75, 2.7, "홀", "rname")
    s.text(5.4, 2.7, f"{room_area('hall'):.1f}㎡", "rarea")
    s.text(1.8, 5.35, "식당", "rname")
    s.text(2.6, 3.55, "주방", "rname")
    s.text(5.75, 4.45, "거실", "rname")
    s.text(5.75, 7.35, "3.6×3.55 · 박공 오픈천장", "rsub")
    s.text(1.8, 7.35, f"LDK 합계 {room_area('ldk'):.1f}㎡", "rarea")

    s.dim_h(0, W, -1.6, fmt(W))
    for a, b in [(0.2, 2.0), (2.1, 4.5), (4.6, 6.2), (6.3, 8.2), (8.3, 11.4)]:
        s.dim_h(a, b, -1.2, fmt(b - a))
    for a, b in [(0.2, 3.6), (3.6, 7.2), (7.3, 11.4)]:
        s.dim_h(a, b, DECK[3] + 0.45, fmt(b - a))
    s.dim_v(0, D, -0.6, fmt(D))
    s.dim_v(0.2, 2.2, -0.25, "2.0")
    s.dim_v(2.3, 7.6, -0.25, "5.3")
    s.dim_v(0.2, 3.95, W + 0.45, "3.75")
    s.dim_v(4.05, 7.6, W + 0.45, "3.55")
    s.north(W + 0.2, -6.6)
    s.text(-1.1, DECK[3] + 1.05, "치수 m · 내법 기준 · 외벽 0.2 / 내벽 0.1 개념값", "note", anchor="start")
    return s.out()


def plan_attic():
    s = Svg(ox=70, oy=70, w=780, h=560, title="2차안 다락 개념 평면도")
    s.rect((0, 0, W, D), "roofarea")
    s.text(3.6, 4.0, "주방·식당·거실 상부 오픈 (박공 천장까지)", "ctx")
    s.text(3.6, 4.35, "서측 박공면 고창", "ctxs")
    s.rect((ATTIC_X0, IY0, IX1, ATTIC[1]), "lowzone")
    s.rect((ATTIC_X0, ATTIC[3], IX1, IY1), "lowzone")
    kh = roof_under(ATTIC[1]) - H_ATTIC_FL
    s.text(9.8, 0.85, f"무릎벽 뒤 수납 (높이 {kh:.2f}m 이하)", "ctxs")
    s.text(9.8, 7.05, f"무릎벽 뒤 수납 (높이 {kh:.2f}m 이하)", "ctxs")
    s.rect(ATTIC, "floor f-kid")
    s.rect(ATTIC_VOID, "void")
    y18a = IY0 + (H_ATTIC_FL + 1.8 - H_PLATE) / PITCH
    y18b = IY1 - (y18a - IY0)
    s.rect((8.2, y18a, IX1, y18b), "tall")
    s.rect((ATTIC_X0, 2.85, 8.2, y18b), "tall")
    s.text(IX1 - 0.3, y18a + 0.35, "천장고 1.8m 이상 구간", "projtxt", anchor="end")
    for i in range(RISERS // 2):
        yy = 2.85 - i * TREAD
        s.line(7.3, yy, 8.2, yy, "tread")
    s.poly([(7.75, 1.5), (7.75, 3.3)], "arrow", "ah")
    s.line(ATTIC_X0, ATTIC[1], ATTIC_X0, ATTIC[3], "rail")
    s.line(8.2, ATTIC[1], 8.2, 2.85, "rail")
    s.line(ATTIC_X0, ATTIC[1], 8.2, ATTIC[1], "rail")
    s.text(ATTIC_X0 - 0.2, 5.0, "난간 1.2m (거실 조망)", "projtxt", anchor="end")
    s.rect((0, 0, W, D), "outline")
    s.rect((W - T_EXT, 3.2, W, 4.6), "win")
    s.text(IX1 - 0.3, 3.05, "동측 박공창", "ctxs", anchor="end")
    s.rect((9.6, 3.3, 10.6, 3.9), "skylight")
    s.text(10.1, 4.15, "천창(선택)", "ctxs")
    a = area(ATTIC) - area(ATTIC_VOID)
    s.text(9.4, 5.2, "자녀 놀이·취미 다락", "rname")
    s.text(9.4, 5.52, f"실사용 바닥 {a:.1f}㎡ ({a/PYEONG:.1f}평)", "rarea")
    s.dim_h(ATTIC_X0, IX1, -0.3, fmt(IX1 - ATTIC_X0))
    s.dim_v(ATTIC[1], ATTIC[3], W + 0.5, fmt(ATTIC[3] - ATTIC[1]))
    s.dim_h(0, W, -0.65, fmt(W))
    s.north(-0.6, D + 0.5)
    return s.out()


def section_cross():
    SV = 48
    ox, oy = 80, 400
    X = lambda y: ox + y * SV
    Y = lambda z: oy - z * SV
    p = []

    def ln(a, b, c, d_, cls):
        p.append(f'<line class="{cls}" x1="{X(a):.1f}" y1="{Y(b):.1f}" x2="{X(c):.1f}" y2="{Y(d_):.1f}"/>')

    def rc(y1, z1, y2, z2, cls):
        p.append(f'<rect class="{cls}" x="{X(y1):.1f}" y="{Y(z2):.1f}" width="{(y2-y1)*SV:.1f}" height="{(z2-z1)*SV:.1f}"/>')

    def tx(a, b, t, cls, anc="middle"):
        p.append(f'<text class="{cls}" x="{X(a):.1f}" y="{Y(b):.1f}" text-anchor="{anc}">{html.escape(t)}</text>')

    rc(-1.4, GL - 0.5, D + 1.4, GL, "ground")
    rc(0, -0.25, D, 0, "wallsec")
    rc(0, 0, T_EXT, H_PLATE, "wallsec")
    rc(D - T_EXT, 0, D, H_PLATE, "wallsec")
    top = ROOF_T / math.cos(math.atan(PITCH))
    pts = [(IY0 - EAVE, H_PLATE - PITCH * EAVE), (D / 2, RIDGE_U), (IY1 + EAVE, H_PLATE - PITCH * EAVE)]
    poly = pts + [(a, b + top) for a, b in reversed(pts)]
    p.append('<polygon class="roofsec" points="' + " ".join(f"{X(a):.1f},{Y(b):.1f}" for a, b in poly) + '"/>')
    rc(IY0, H_ATTIC_FL - 0.3, IY1, H_ATTIC_FL, "slab")
    for yk in (ATTIC[1], ATTIC[3]):
        ln(yk, H_ATTIC_FL, yk, roof_under(yk), "knee")
    ya = IY0 + (H_ATTIC_FL + 1.8 - H_PLATE) / PITCH
    rc(ya, H_ATTIC_FL + 1.8, D - ya, RIDGE_U, "tallsec")
    ln(ya, H_ATTIC_FL + 1.8, D - ya, H_ATTIC_FL + 1.8, "h18")
    tx(D / 2, H_ATTIC_FL + 1.88, "다락 바닥+1.8m", "sectxt")
    rc(3.95, 0, 4.05, H_CEIL, "wallsec")
    rc(3.35, 0, 3.95, 2.1, "proj")
    tx(1.9, 1.1, "부부침실", "secroom")
    tx(5.8, 1.1, "자녀 공동방", "secroom")
    tx(3.65, 2.2, "장", "sectxt")
    tx(D / 2, 3.4, "자녀 놀이 다락", "secroom")
    for z, lab in ((0, "FL ±0"), (H_CEIL, f"천장 {H_CEIL:.2f}"), (H_ATTIC_FL, f"다락 FL +{H_ATTIC_FL:.2f}"),
                   (H_PLATE, f"지붕 하부@외벽 +{H_PLATE:.2f}"), (RIDGE_U, f"용마루 하부 +{RIDGE_U:.2f}")):
        ln(D + 0.9, z, D + 1.1, z, "dimtick")
        tx(D + 1.25, z - 0.05, lab, "sectxt", "start")
    ln(D + 1.0, 0, D + 1.0, RIDGE_U, "dim")
    tx(-0.6, -0.6, "북", "secdir")
    tx(D + 0.6, -0.6, "남", "secdir")
    tx(1.0, RIDGE_U + 0.3, f"물매 약 {math.degrees(math.atan(PITCH)):.0f}°", "sectxt")
    return (f'<svg viewBox="0 0 720 470" role="img" aria-label="남북 횡단면" xmlns="http://www.w3.org/2000/svg">'
            f'<title>남북 횡단면(다락 통과)</title>' + "".join(p) + "</svg>")


def section_long():
    SV = 48
    ox, oy = 45, 380
    X = lambda x: ox + x * SV
    Y = lambda z: oy - z * SV
    p = []

    def rc(x1, z1, x2, z2, cls):
        p.append(f'<rect class="{cls}" x="{X(x1):.1f}" y="{Y(z2):.1f}" width="{(x2-x1)*SV:.1f}" height="{(z2-z1)*SV:.1f}"/>')

    def tx(a, b, t, cls, anc="middle"):
        p.append(f'<text class="{cls}" x="{X(a):.1f}" y="{Y(b):.1f}" text-anchor="{anc}">{html.escape(t)}</text>')

    rc(-0.6, GL - 0.5, W + 0.6, GL, "ground")
    rc(0, -0.25, W, 0, "wallsec")
    rc(0, 0, T_EXT, RIDGE_U, "wallsec")
    rc(W - T_EXT, 0, W, RIDGE_U, "wallsec")
    rc(-0.3, RIDGE_U, W + 0.3, RIDGE_U + ROOF_T, "roofsec")
    rc(ATTIC_X0, H_ATTIC_FL - 0.3, IX1, H_ATTIC_FL, "slab")
    rc(8.2, 0, 8.3, H_CEIL, "wallsec")
    p.append(f'<line class="rail" x1="{X(ATTIC_X0):.1f}" y1="{Y(H_ATTIC_FL):.1f}" x2="{X(ATTIC_X0):.1f}" y2="{Y(H_ATTIC_FL+1.2):.1f}"/>')
    rc(0, 3.4, T_EXT, 5.2, "winsec")
    rc(W - T_EXT, 3.4, W, 4.8, "winsec")
    tx(3.6, 3.3, "주방 · 식당 · 거실 (오픈천장)", "secroom")
    tx(3.6, 2.9, f"천장 최고 약 {RIDGE_U:.1f}m", "sectxt")
    tx(7.7, 1.2, "홀", "secroom")
    tx(9.85, 1.2, "부부침실", "secroom")
    tx(9.4, 3.4, "놀이 다락", "secroom")
    tx(0.3, 5.45, "서측 고창", "sectxt", "start")
    tx(ATTIC_X0 - 0.1, H_ATTIC_FL + 1.35, "난간", "sectxt", "end")
    for z, lab in ((0, "±0"), (H_CEIL, f"{H_CEIL:.2f}"), (H_ATTIC_FL, f"{H_ATTIC_FL:.2f}"), (RIDGE_U, f"{RIDGE_U:.2f}")):
        tx(W + 0.9, z - 0.05, lab, "sectxt", "start")
        p.append(f'<line class="dimtick" x1="{X(W+0.55):.1f}" y1="{Y(z):.1f}" x2="{X(W+0.8):.1f}" y2="{Y(z):.1f}"/>')
    tx(-0.2, -0.75, "서", "secdir")
    tx(W + 0.2, -0.75, "동", "secdir")
    return (f'<svg viewBox="0 0 720 440" role="img" aria-label="동서 종단면" xmlns="http://www.w3.org/2000/svg">'
            f'<title>동서 종단면(용마루 아래)</title>' + "".join(p) + "</svg>")


# ---------------------------------------------------------------- 페이지
def build():
    checks, tri = run_checks()
    esc = html.escape
    bldg = W * D
    room_sum = sum(room_area(k) for k in ROOMS)
    wall_sum = bldg - room_sum
    a_att = area(ATTIC) - area(ATTIC_VOID)
    knee = roof_under(ATTIC[1]) - H_ATTIC_FL
    top = RIDGE_U - H_ATTIC_FL
    gfa = bldg + a_att
    v1_bldg, v1_net = 80.64, 71.06

    tagname = {"ok": "충족", "ng": "미흡", "mid": "보완 필요"}
    crit_rows = "".join(
        f"<tr><td><b>{esc(n)}</b></td><td>{esc(rule)}</td>"
        f"<td class='v'><span class='tag {s1}'>{tagname[s1]}</span></td><td>{esc(t1)}</td>"
        f"<td class='v'><span class='tag {s2}'>{tagname[s2]}</span></td><td>{esc(t2)}</td></tr>"
        for n, rule, s1, t1, s2, t2 in criteria(room_sum, tri))

    target = {"ldk": 30.0, "master": 11.0, "kids": 14.0, "bath": 4.8, "util": 4.7}
    v1a = {"ldk": 28.59, "master": 10.88, "kids": 13.28, "bath": 4.8, "util": 3.6, "entry": 2.8, "hall": 2.09, "stair": 5.04}
    notes = {
        "ldk": "주방·식당 3.4×5.3 + 거실 3.6×3.55, 전체 박공 오픈천장",
        "master": "퀸 침대, 붙박이장 2.2m를 자녀방 쪽 벽에",
        "kids": "싱글침대 2(남·북 벽), 책상 2(창가), 옷장을 거실 쪽 벽에",
        "bath": "홀에서 출입, 무단차 샤워, 보강벽, 미닫이",
        "util": "주방 직결 미닫이 + 북측 외부문, 세탁·건조·보일러·팬트리",
        "entry": "중문 앞이 홀, 신발장",
        "hall": "현관에서 모든 영역으로 분기, 외투 수납 포함",
        "stair": "홀에서 오름, 첫 흐름 아래 수납",
    }
    rows = ""
    for k in ["ldk", "master", "kids", "bath", "util", "entry", "hall", "stair"]:
        t = target.get(k)
        rows += (f"<tr><td>{esc(ROOMS[k]['name'])}</td><td class='n'>{v1a[k]:.1f}</td>"
                 f"<td class='n'><b>{room_area(k):.2f}</b></td><td class='n'>{'' if t is None else f'{t:.1f}'}</td>"
                 f"<td>{esc(notes[k])}</td></tr>")
    check_html = "".join(
        f"<li><span class='pill {'ok' if ok else 'ng'}'>{'OK' if ok else 'NG'}</span><span>{esc(t)}</span></li>"
        for ok, t in checks)
    all_ok = all(ok for ok, _ in checks)
    css = (HERE / "style.css").read_text(encoding="utf-8")

    page = f"""<title>박공주택 개념평면</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans+KR:wght@400;600;700&display=swap">
<style>{css}</style>
<div class="wrap">
<header>
  <div class="stamp">2차 개선안 · 개념설계 · 인허가/시공용 도면 아님</div>
  <h1>200평 자연녹지의 모던 박공주택</h1>
  <p class="lede">1차안을 주거 건축계획의 기본 기준(조닝, 동선 분리, 실 치수)으로 점검하고, 미흡한 점을 고친 안입니다.
  핵심 변경은 현관을 가운데로 옮겨 <b>현관에서 홀로 들어가 거실·욕실·침실로 바로 갈라지게</b> 한 것입니다.
  그 대신 외곽이 {v1_bldg:.1f}㎡(11.2×7.2m)에서 <b>{bldg:.1f}㎡({W}×{D}m)</b>로 커졌습니다.</p>
</header>

<section>
  <h2><span class="code">1</span>건축계획 기준 점검: 1차안 → 2차안</h2>
  <p>주거 건축계획 교재에서 기본으로 다루는 원칙과 국토교통부 최저주거기준을 기준으로 삼았습니다. 특정 교재 한 권의 원문을 옮긴 것이 아니므로, 수치 기준은 설계자와 다시 확인하시기 바랍니다.</p>
  <div class="tbl"><table>
    <thead><tr><th>항목</th><th>기준</th><th colspan="2">1차안</th><th colspan="2">2차안</th></tr></thead>
    <tbody>{crit_rows}</tbody></table></div>
</section>

<section>
  <h2><span class="code">B</span>1층 개념 평면도 (2차안)</h2>
  <div class="sheet">{plan_1f()}</div>
  <div class="legend">
    <span><i style="background:none;border:0;border-top:2.4px solid var(--pine);height:0"></i>가족 동선: 현관 → 홀 → 각 실</span>
    <span><i style="background:none;border:0;border-top:2.4px dashed var(--timber);height:0"></i>가사 동선: 다용도 ↔ 주방, 외부문</span>
    <span><i style="background:var(--f-liv)"></i>거실·식당·주방</span><span><i style="background:var(--f-bed)"></i>부부침실</span>
    <span><i style="background:var(--f-kid)"></i>자녀공간·다락</span><span><i style="background:var(--f-wet)"></i>습식·서비스</span>
    <span><i style="background:var(--f-circ)"></i>현관·홀·계단</span>
    <span><i style="border:1.4px dashed var(--pine);background:none"></i>다락 바닥 투영</span>
  </div>
  <div class="grid2">
    <div class="callout"><h3>무엇이 바뀌었나</h3><p>북측 줄 순서를 다용도 · 욕실 · 현관 · 계단 · 부부침실로 바꿨습니다.
    중문을 열면 홀이고, 홀에서 욕실·부부침실·자녀방·계단·거실·주방으로 각각 들어갑니다. 주방 통로는 요리하는 사람만 씁니다.</p></div>
    <div class="callout"><h3>왜 외곽이 커졌나</h3><p>7.2m 깊이에서는 북측 서비스 줄을 빼면 LDK 깊이가 4.7m뿐이어서, 주방·식탁·거실을 넣으면 거실 폭이 2.9m까지 줄었습니다.
    깊이를 7.8m로 늘려 주방·식당을 5.3m 깊이로 세로 배치하고, 거실은 그 옆에 3.6m 폭으로 따로 확보했습니다.</p></div>
  </div>
</section>

<section>
  <h2><span class="code">C</span>다락 개념 평면도</h2>
  <div class="sheet">{plan_attic()}</div>
  <p>다락은 홀·부부침실·자녀방 위(x ≥ {ATTIC_X0}m)에만 있습니다. 서쪽 끝 1.2m 난간에서 오픈천장 아래 거실을 내려다봅니다.
  무릎벽 높이는 {knee:.2f}m이고, 옅은 녹색 띠가 천장고 1.8m 이상인 구간입니다.</p>
</section>

<section>
  <h2><span class="code">D</span>박공 단면 개념도</h2>
  <div style="display:grid;gap:16px">
    <div class="sheet"><h3 style="margin-bottom:8px">남북 횡단면 · 부부침실/자녀방/다락</h3>{section_cross()}</div>
    <div class="sheet"><h3 style="margin-bottom:8px">동서 종단면 · 용마루 아래</h3>{section_long()}</div>
  </div>
  <div class="callout"><h3>다락 면적 산입</h3>
  <p>다락 천장고는 무릎벽 {knee:.2f}m, 용마루 아래 {top:.2f}m, 단순 평균 약 {(knee+top)/2:.2f}m입니다. 「건축법 시행령」 제119조의 경사지붕 다락 기준(층고 1.8m 이하)을 넘으므로
  연면적에 산입된다고 보고 계획했습니다. 연면적 {gfa:.1f}㎡({gfa/PYEONG:.1f}평), 용적률 {gfa/SITE_M2*100:.1f}%로 자연녹지 상한 안입니다.</p></div>
</section>

<section>
  <h2><span class="code">E</span>면적 비교와 검산</h2>
  <div class="kv">
    <div><b>{bldg:.2f}㎡</b><span>건축면적 {bldg/PYEONG:.1f}평 (1차안 {v1_bldg:.1f}㎡ · 24.4평)</span></div>
    <div><b>{bldg/SITE_M2*100:.1f}%</b><span>건폐율 (자연녹지 상한 20%)</span></div>
    <div><b>{room_sum:.1f}㎡</b><span>1층 순면적 (1차안 {v1_net:.1f}㎡)</span></div>
    <div><b>{gfa/PYEONG:.1f}평</b><span>1층 + 다락 (1차안 30.4평)</span></div>
  </div>
  <div class="tbl"><table>
    <thead><tr><th>공간</th><th style="text-align:right">1차안 ㎡</th><th style="text-align:right">2차안 ㎡</th><th style="text-align:right">브리프 권장 ㎡</th><th>설계 포인트</th></tr></thead>
    <tbody>{rows}
    <tr class="sum"><td>1층 순면적 합계</td><td class="n">{v1_net:.1f}</td><td class="n">{room_sum:.2f}</td><td class="n">74.5</td><td>내법 면적의 합</td></tr>
    <tr><td>벽체</td><td class="n">9.6</td><td class="n">{wall_sum:.2f}</td><td class="n"></td><td>외벽 0.2m + 내벽 0.1m</td></tr>
    <tr class="sum"><td>건축면적</td><td class="n">{v1_bldg:.1f}</td><td class="n">{bldg:.2f}</td><td class="n">80.6</td><td>{W}×{D}m</td></tr>
    <tr><td>다락 실사용</td><td class="n">19.8</td><td class="n">{a_att:.2f}</td><td class="n">19.8</td><td>{fmt(IX1-ATTIC_X0)}×{fmt(ATTIC[3]-ATTIC[1])}m − 계단 오픈부</td></tr>
    </tbody></table></div>
  <div class="callout"><h3>공사비 영향</h3><p>1층이 {bldg-v1_bldg:.1f}㎡({(bldg-v1_bldg)/PYEONG:.1f}평) 늘어, 본체 공사비도 대략 그 비율(약 {(bldg/v1_bldg-1)*100:.0f}%)만큼 오른다고 보는 것이 안전합니다.
  평당 단가를 넣은 금액 산정은 하지 않았습니다. 3억원 안에 맞추려면 데크·조경 단계 시공, 다락 마감 후시공 같은 조정을 함께 봐야 합니다.</p></div>
  <h3>자체 검증 {'(모두 통과)' if all_ok else '(실패 항목 있음)'}</h3>
  <ul class="checks">{check_html}</ul>
</section>

<section>
  <h2><span class="code">F</span>건축주 확인이 필요한 것</h2>
  <div class="grid2">
    <div class="tbl" style="padding:14px 16px"><h3>결정해 주셔야 할 것</h3><ul class="list">
      <li>자녀 두 명의 성별과 나이. 이성이고 8세 이상이면 방을 나눠야 하는지 판단해야 합니다</li>
      <li>외곽 {W}×{D}m({bldg/PYEONG:.1f}평) 확장을 받아들일지, 1차안 크기로 돌아가고 거실 폭을 포기할지</li>
      <li>욕실 1개로 충분한지(4인 가족 아침 혼잡). 홀에 세면대를 하나 더 두는 방법이 있습니다</li>
      <li>거실에 TV를 둘지. 두지 않으면 소파를 정원 쪽으로 돌릴 수 있습니다</li>
    </ul></div>
    <div class="tbl" style="padding:14px 16px"><h3>건축사·토지 확인</h3><ul class="list">
      <li>토지이용계획확인서, 조례 건폐율·용적률, 도로 법적 지위, 농지·산지 전용</li>
      <li>상하수도·정화조·전기 인입 견적</li>
      <li>다락 층고 산정 방식과 연면적 산입 여부</li>
      <li>구조 방식에 따른 실제 벽 두께, 7.8m 경간 지붕 구조</li>
      <li>오픈천장 LDK의 난방·결로·환기, 남서 대형창 차양</li>
    </ul></div>
  </div>
</section>

<footer>
  <p>기준 출처: 주거 건축계획 일반 원칙(조닝·동선·실 치수), 국토교통부 최저주거기준(2011), 「건축법 시행령」 제119조, 「국토의 계획 및 이용에 관한 법률 시행령」 제84조·제85조.
  1인당 면적 표준(약 16㎡/인)과 자녀 침실 분리 조건은 교재·공고 원문으로 다시 확인이 필요합니다.</p>
  <p>이 문서는 건축주와 건축사의 첫 상담을 위한 개념안이며 구조·설비·에너지·소방·인허가 검토를 대신하지 않습니다.</p>
</footer>
</div>
"""
    return page, checks


if __name__ == "__main__":
    page, checks = build()
    (HERE / "index.html").write_text(page, encoding="utf-8")
    for ok, t in checks:
        print("OK " if ok else "NG ", t)
