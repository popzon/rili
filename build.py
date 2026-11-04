#!/usr/bin/env python3
"""Build api/getallconfig.ashx for the modified 点滴日历 (日历) app.

The app expects the old 51wnl config server format:
  {"status":1,"r":"<update tag>","msg":{"Vocation_ZH_CN":"<base64 json>","Festival_ZH_CN":"<base64 json>"}}
Vocation_ZH_CN: {"yyyyMMdd": 1 (休) | 2 (班)}
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


def festival():
    out = {}
    for t, m in FEST.items():
        out[t] = {k: [{'V': n, 'a': n, 'b': p, 'c': 1900}] for k, (n, p) in m.items()}
    return out


def b64(o):
    return base64.b64encode(json.dumps(o, ensure_ascii=False, separators=(',', ':')).encode('utf-8')).decode()


def main():
    local = sys.argv[1] if len(sys.argv) > 1 else None
    v = vocation(local)
    if len(v) < 100:
        sys.exit('holiday data looks empty, not writing')
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
