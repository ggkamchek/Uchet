from django import template

register = template.Library()

@register.filter
def dir_money(value, decimals=2):
    if value is None or value == '':
        return '—'
    try:
        n = float(value)
    except (TypeError, ValueError):
        return str(value)
    neg = n < 0
    n = abs(n)
    d = int(decimals) if decimals is not None else 2
    d = max(0, min(d, 6))
    s = f'{n:.{d}f}'
    whole, frac = s.split('.')
    rev = whole[::-1]
    chunks = [rev[i : i + 3] for i in range(0, len(rev), 3)]
    whole_spaced = ' '.join(c[::-1] for c in reversed(chunks))
    out = f'{whole_spaced},{frac}'
    return ('−' if neg else '') + out
