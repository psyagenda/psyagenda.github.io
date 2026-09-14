# -*- coding: utf-8 -*-
"""Yeni bir dil için BELGE SAYFASI İSKELETLERİ üretir (guide/faq/terms/privacy).

Neden ayrı betik: `build-site.py` kabuğu üretir ama head/h1/altbaşlık'ı MEVCUT kök dosyadan
okur; `generate-website-*.mjs` ise yalnız GENERATED bloğunu yazar. Yani yeni dilde önce bu
dört dosyanın var olması gerekir. Bu betik onları bir kez açar; içerik sonra jeneratörlerden
gelir, kabuk build-site.py'den.

Kullanım: python3 _tools/new-lang-pages.py <dil> [<dil> ...]
Metinler: _tools/lang-strings.json  ({dil: {desc: {...}, sub: {...}}})
Sayfa adları ve privacyLastUpdated UYGULAMANIN sözlüğünden okunur — site ile uygulama ayrışmasın.
"""
import io, json, os, re, sys

SITE = os.path.expanduser('~/Desktop/psyagenda.github.io')
APP  = os.path.expanduser('~/Desktop/PsyAgenda')
sys.path.insert(0, os.path.join(SITE, '_tools'))

MARKER = {'guide': 'GUIDE', 'faq': 'FAQ', 'terms': 'TERMS', 'privacy': 'PRIVACY'}
OG_LOCALE = {'tr':'tr_TR','en':'en_US','es':'es_ES','de':'de_DE','fr':'fr_FR','pt':'pt_BR','it':'it_IT'}
BASE = 'https://www.psyagenda.app/'

def app_string(lang, key):
    """src/locales/<lang>/settings.ts içinden düz bir anahtarı çeker (tırnak kaçışları çözülür)."""
    p = os.path.join(APP, 'src', 'locales', lang, 'settings.ts')
    m = re.search(r'"%s":\s*"((?:[^"\\]|\\.)*)"' % re.escape(key), io.open(p, encoding='utf-8').read())
    if not m: raise SystemExit('%s: %s bulunamadı' % (lang, key))
    return json.loads('"%s"' % m.group(1))

def build(lang, labels, langs, strings):
    desc, sub = strings[lang]['desc'], strings[lang]['sub']
    subs = dict(sub)
    subs['privacy'] = app_string(lang, 'privacyLastUpdated')   # tarih/sürüm uygulamadan
    for slug, marker in MARKER.items():
        fname = ('%s-%s.html' % (slug, lang))
        # §4.2: Almanca Halbgeviertstrich (–) kullanır, Geviertstrich (—) İngilizce dizgi geleneğidir.
        dash = '–' if lang == 'de' else '—'
        title = '%s %s PsyAgenda' % (labels[slug][lang], dash)
        alts = '\n'.join('    <link rel="alternate" hreflang="%s" href="%s%s-%s.html">' % (c, BASE, slug, c)
                         for c, _ in langs)
        html = """<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{desc}">
    <link rel="canonical" href="{base}{slug}-{lang}.html">
{alts}
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="PsyAgenda">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:url" content="{base}{slug}-{lang}.html">
    <meta property="og:image" content="{base}app-icon.png">
    <meta property="og:locale" content="{oglocale}">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{desc}">
    <link rel="icon" href="app-icon.png">
    <link rel="stylesheet" href="style.css">
</head>
<body>
<main>
    <div class="wrap page-head">
        <h1>{h1}</h1>
        <p class="subtitle">{sub}</p>
    </div>
    <div class="wrap doc-layout">
        <article class="doc">
<!-- GENERATED:{marker}-START -->
<!-- GENERATED:{marker}-END -->
        </article>
    </div>
</main>
</body>
</html>
""".format(lang=lang, title=title, desc=desc[slug], base=BASE, slug=slug, alts=alts,
           oglocale=OG_LOCALE[lang], h1=labels[slug][lang], sub=subs[slug], marker=marker)
        io.open(os.path.join(SITE, fname), 'w', encoding='utf-8').write(html)
        print('   ✓', fname)

if __name__ == '__main__':
    import importlib.util
    spec = importlib.util.spec_from_file_location('bs', os.path.join(SITE, '_tools', 'build-site.py'))
    bs = importlib.util.module_from_spec(spec)
    sys.argv = [sys.argv[0], '_preview']          # build-site içe aktarılırken OUT'u bozmasın
    spec.loader.exec_module(bs)
    strings = json.load(io.open(os.path.join(SITE, '_tools', 'lang-strings.json'), encoding='utf-8'))
    for lang in [a for a in os.environ.get('LANGS', '').split() if a] or ['it']:
        print(lang + ':'); build(lang, bs.PAGE_LABEL, bs.LANGS, strings)
