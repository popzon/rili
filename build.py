#!/usr/bin/env python3
"""Build api/getallconfig.ashx for the modified 点滴日历 (日历) app.

The app expects the old 51wnl config server format:
  {"status":1,"r":"<update tag>","msg":{"Vocation_ZH_CN":"<base64 json>","Festival_ZH_CN":"<base64 json>"}}
Vocation_ZH_CN: {"yyyyMMdd": 1 (休) | 2 (班) | 3 (美国联邦假日 休)}
Festival_ZH_CN: S/L/W rules + Y (exact yyyyMMdd, used for US holidays; needs app v1.2.2 US build)
Holiday data comes from https://github.com/NateScarlet/holiday-cn
"""
import base64, datetime, json, os, sys, urllib.request

SRC = 'https://raw.githubusercontent.com/NateScarlet/holiday-cn/master/{}.json'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api', 'getallconfig.ashx')


def load_year(y, local_dir=None):
    if local_dir:
        p = os.path.join(local_dir, '%d.json' % y)
        if not os.path.exists(p):
            return None
        return json.load(open(p, encoding='utf-8'))
    try:
        with urllib.request.urlopen(SRC.format(y), timeout=30) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        print('skip', y, e, file=sys.stderr)
        return None


def vocation(local_dir=None):
    v = {}
    last = datetime.date.today().year + 1
    for y in range(2007, last + 1):
        d = load_year(y, local_dir)
        if not d:
            continue
        for day in d.get('days', []):
            v[day['date'].replace('-', '')] = 1 if day['isOffDay'] else 2
    return dict(sorted(v.items()))


# Festival names shown in the month grid (p >= 3 is shown in the cell).
# S = solar MMdd, L = lunar MMdd (R prefix = leap month), W = month + nth + weekday(0=Sun)
FEST = {
    'S': {
        '0101': ['元旦', 5], '0214': ['情人节', 4], '0308': ['妇女节', 4], '0312': ['植树节', 4],
        '0401': ['愚人节', 3], '0501': ['劳动节', 5], '0504': ['青年节', 4], '0601': ['儿童节', 4],
        '0701': ['建党节', 4], '0801': ['建军节', 4], '0910': ['教师节', 4], '1001': ['国庆节', 5],
        '1031': ['万圣夜', 3], '1224': ['平安夜', 4], '1225': ['圣诞节', 4],
    },
    'L': {
        '0101': ['春节', 6], '0115': ['元宵节', 5], '0202': ['龙抬头', 4], '0505': ['端午节', 6],
        '0707': ['七夕', 5], '0715': ['中元节', 4], '0815': ['中秋节', 6], '0909': ['重阳节', 5],
        '1208': ['腊八节', 4], '1223': ['小年', 4], '1230': ['除夕', 6],
    },
    'W': {
        '0520': ['母亲节', 4], '0630': ['父亲节', 4], '1144': ['感恩节', 4],
    },
}


def _nth_weekday(y, m, wd, n):
    """n-th weekday (Mon=0) of month; n=-1 = last."""
    if n > 0:
        d = datetime.date(y, m, 1)
        d += datetime.timedelta(days=(wd - d.weekday()) % 7 + 7 * (n - 1))
        return d
    nxt = datetime.date(y + (m == 12), m % 12 + 1, 1)
    d = nxt - datetime.timedelta(days=1)
    return d - datetime.timedelta(days=(d.weekday() - wd) % 7)


def _easter(y):
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4
    f = (b + 8) // 25; g = (b - f + 1) // 3; h = (19 * a + b - d - g + 15) % 30
    i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31; day = (h + l - 7 * m + 114) % 31 + 1
    return datetime.date(y, month, day)


# US holidays (Y table: exact yyyyMMdd per year). Short names fit the month grid.
def us_holidays(y):
    MON, THU = 0, 3
    h = []
    if y >= 1986: h.append((_nth_weekday(y, 1, MON, 3), '金恩日', 5))           # Martin Luther King Jr. Day
    h.append((_nth_weekday(y, 2, MON, 3), '总统日', 5))                         # Presidents' Day
    h.append((_easter(y), '复活节', 4))                                          # Easter
    h.append((_nth_weekday(y, 5, MON, -1), '阵亡将士', 5))                      # Memorial Day
    if y >= 2021: h.append((datetime.date(y, 6, 19), '六月节', 5))              # Juneteenth
    h.append((datetime.date(y, 7, 4), '独立日', 5))                             # Independence Day
    h.append((_nth_weekday(y, 9, MON, 1), '劳工节', 5))                         # Labor Day
    h.append((_nth_weekday(y, 10, MON, 2), '哥伦布日', 5))                      # Columbus / Indigenous Peoples' Day
    h.append((datetime.date(y, 11, 11), '老兵节', 5))                           # Veterans Day
    h.append((_nth_weekday(y, 11, THU, 4) + datetime.timedelta(days=1), '黑五', 3))  # Black Friday
    return h


def festival():
    out = {}
    for t, m in FEST.items():
        out[t] = {k: [{'V': n, 'a': n, 'b': p, 'c': 1900, 'P': p, 'Y': 1900}] for k, (n, p) in m.items()}
    yt = {}
    for y in range(2000, 2061):
        for d, n, p in us_holidays(y):
            yt.setdefault(d.strftime('%Y%m%d'), []).append({'V': n, 'a': n, 'b': p, 'c': 1900, 'P': p, 'Y': 1900, 'K': 'US'})
    out['Y'] = yt
    # Thanksgiving is US-only: tag it so the app colors it like other US holidays
    for e in out['W'].get('1144', []):
        e['K'] = 'US'
    return out


# US federal holidays -> Vocation value 3 (US 休, drawn as a lavender outline mark).
# Fixed-date holidays falling on Sat/Sun also mark the observed Fri/Mon.
def us_federal_days(y):
    MON, THU = 0, 3
    days = [datetime.date(y, 1, 1), _nth_weekday(y, 2, MON, 3), _nth_weekday(y, 5, MON, -1),
            datetime.date(y, 7, 4), _nth_weekday(y, 9, MON, 1), _nth_weekday(y, 10, MON, 2),
            datetime.date(y, 11, 11), _nth_weekday(y, 11, THU, 4), datetime.date(y, 12, 25)]
    if y >= 1986: days.append(_nth_weekday(y, 1, MON, 3))
    if y >= 2021: days.append(datetime.date(y, 6, 19))
    out = set()
    for d in days:
        out.add(d)
        if d.weekday() == 5: out.add(d - datetime.timedelta(days=1))
        elif d.weekday() == 6: out.add(d + datetime.timedelta(days=1))
    return out


def add_us_rest(v):
    for y in range(2000, 2061):
        for d in us_federal_days(y):
            k = d.strftime('%Y%m%d')
            if k not in v:  # Chinese 休/班 wins when both apply
                v[k] = 3
    return dict(sorted(v.items()))


def b64(o):
    return base64.b64encode(json.dumps(o, ensure_ascii=False, separators=(',', ':')).encode('utf-8')).decode()


def main():
    local = sys.argv[1] if len(sys.argv) > 1 else None
    v = vocation(local)
    if len(v) < 100:
        sys.exit('holiday data looks empty, not writing')
    v = add_us_rest(v)
    body = {
        'status': 1,
        'r': datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S'),
        'msg': {'Vocation_ZH_CN': b64(v), 'Festival_ZH_CN': b64(festival())},
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(body, f, separators=(',', ':'))
    print('wrote', OUT, len(v), 'days, last', max(v))


if __name__ == '__main__':
    main()
