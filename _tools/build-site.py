# -*- coding: utf-8 -*-
"""Site sayfalarını kabuk + CSS ile üretir. Üretilen (GENERATED) bloklara dokunmaz.

Kullanım: python3 _tools/build-site.py [_preview | .]
- Anasayfa kaynağı _src/index.html + _src/index-en.html (elle yazılır; kök index.html ÜRETİLİR, elle düzenleme).
- Belge sayfaları kökteki dosyalardan okunur: head, h1, alt başlık ve GENERATED blok korunur, kabuk yenilenir.
- Uygulama tarafındaki generate-website-*.mjs yalnız GENERATED blokları yazar; bu betikle uyumludur.
"""
import io, os, re, sys

SRC = os.path.expanduser('~/Desktop/psyagenda.github.io')
OUT = os.path.join(SRC, sys.argv[1] if len(sys.argv) > 1 else '_preview')
HOME_SRC = os.path.join(SRC, '_src')   # anasayfa kaynakları (elle yazılan)

NAV = {'tr': [('index.html','Ana Sayfa'),('guide-tr.html','Kullanım Rehberi'),('faq-tr.html','SSS'),
              ('terms-tr.html','Kullanım Koşulları'),('privacy-tr.html','Gizlilik Politikası')],
       'en': [('index-en.html','Home'),('guide-en.html','User Guide'),('faq-en.html','FAQ'),
              ('terms-en.html','Terms of Use'),('privacy-en.html','Privacy Policy')]}
FOOT = {'tr': ('Tüm hakları saklıdır.', [('privacy-tr.html','Gizlilik Politikası'),('terms-tr.html','Kullanım Koşulları'),('faq-tr.html','SSS')]),
        'en': ('All rights reserved.', [('privacy-en.html','Privacy Policy'),('terms-en.html','Terms of Use'),('faq-en.html','FAQ')])}
# Mağaza düğmeleri. href None iken pasif (aria-disabled) üretilir; mağaza yayımlanınca bağlantıyı yaz, düğme kendiliğinden aktifleşir.
STORES = [
    dict(href=None, tr=('iPhone ve iPad', 'App Store&rsquo;dan İndirin'),        en=('iPhone and iPad', 'Download on the App Store')),
    dict(href=None, tr=('Mac',            'Mac App Store&rsquo;dan İndirin'),    en=('Mac',             'Download on the Mac App Store')),
    dict(href=None, tr=('Android',        'Google Play&rsquo;den İndirin'),         en=('Android',         'Download on Google Play')),
    dict(href=None, tr=('Windows',        'Microsoft Store&rsquo;dan İndirin'),   en=('Windows',         'Download on Microsoft Store')),
]
STORE_PENDING = {'tr': 'Henüz yayımlanmadı', 'en': 'Not yet available'}

def stores(lang):
    out = []
    for st in STORES:
        dev, label = st[lang]
        inner = '<small>%s</small><strong>%s</strong>' % (dev, label)
        if st['href']:
            out.append('                <a class="store" href="%s" target="_blank" rel="noopener">%s</a>' % (st['href'], inner))
        else:
            out.append('                <span class="store" aria-disabled="true" title="%s">%s</span>' % (STORE_PENDING[lang], inner))
    return '\n'.join(out)

NOTICE_STATUS = 'pending'   # tüm mağazalarda yayımlanınca 'live' yap → nokta yeşile döner
TOC_TITLE = {'tr':'Bu sayfada','en':'On this page'}
DOC_SEARCH = {'tr': dict(ph='Bu sayfada ara...', clear='Temizle', none='Sonuç bulunamadı.', count='{n} eşleşme · {m} bölüm'),
              'en': dict(ph='Search this page...', clear='Clear', none='No results found.', count='{n} match{es} · {m} section{s}')}
ICON_X = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>'
HOME = {'tr': dict(file='index.html', alt='index-en.html', h1a='Akıllı terapist ajandası.', h1b='Hayatını kolaylaştırır.',
                   feat='Uygulamanın temel özellikleri', more='Devamını göster', less='Daha az göster',
                   notice='Yayına hazırlanıyor'),
        'en': dict(file='index-en.html', alt='index.html', h1a='Smart therapist agenda.', h1b='Ease your life.',
                   feat='Core features of the application', more='Show more', less='Show less',
                   notice='Preparing for release')}

def head_of(src): return re.search(r'<head>.*?</head>', src, re.S).group(0)

LANGS = [('tr', 'Türkçe'), ('en', 'English')]   # yeni dil: buraya satır + NAV/FOOT/HOME/TOC_* tablolarına karşılığı
LANG_UI = {'tr': dict(label='Dil', search='Dil ara', empty='Sonuç yok', aria='Dil seçimi'),
           'en': dict(label='Language', search='Search languages', empty='No results', aria='Language selection')}
ICON_GLOBE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9.2"/><path d="M2.8 12h18.4M12 2.8c2.6 2.7 3.9 5.8 3.9 9.2s-1.3 6.5-3.9 9.2c-2.6-2.7-3.9-5.8-3.9-9.2s1.3-6.5 3.9-9.2z"/></svg>'
ICON_CHEV = '<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>'
ICON_MAIL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m3.5 7 8.5 6 8.5-6"/></svg>'
ICON_SEARCH = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7.5"/><path d="m20 20-4.2-4.2"/></svg>'

def topbar(lang, active, alt):
    items = '\n'.join('                <a href="%s"%s>%s</a>' % (h, ' class="active"' if h == active else '', t) for h, t in NAV[lang])
    files = {lang: active, ('en' if lang == 'tr' else 'tr'): alt}
    U = LANG_UI[lang]
    opts = '\n'.join('                        <li><a href="%s" lang="%s" hreflang="%s"%s>%s</a></li>'
                     % (files[c], c, c, ' class="current" aria-current="true"' if c == lang else '', name) for c, name in LANGS)
    return """<header class="topbar" id="topbar">
    <div class="wrap topbar-inner">
        <a class="brand" href="%s"><img src="app-icon.png" alt=""><span>PsyAgenda</span></a>
        <div class="nav-right">
            <nav class="mainnav">
%s
            </nav>
            <div class="lang-menu" id="lang-menu">
                <button type="button" class="lang-btn" id="lang-btn" aria-haspopup="true" aria-expanded="false" aria-controls="lang-panel" aria-label="%s">%s<span>%s</span>%s</button>
                <div class="lang-panel" id="lang-panel">
                    <label class="lang-search">%s<input type="search" id="lang-search" placeholder="%s" autocomplete="off" spellcheck="false" aria-label="%s"></label>
                    <ul class="lang-list" id="lang-list">
%s
                    </ul>
                    <p class="lang-empty" id="lang-empty" hidden>%s</p>
                </div>
            </div>
        </div>
    </div>
</header>
<div class="topbar-spacer" aria-hidden="true"></div>""" % (NAV[lang][0][0], items, U['aria'], ICON_GLOBE, U['label'], ICON_CHEV, ICON_SEARCH, U['search'], U['search'], opts, U['empty'])

def footer(lang):
    rights, links = FOOT[lang]
    return """<footer class="site-footer">
    <div class="wrap">
        <span>&copy; 2026 PsyAgenda. %s</span>
        <nav>
%s
        </nav>
    </div>
</footer>""" % (rights, '\n'.join('            <a href="%s">%s</a>' % (h, t) for h, t in links))

JS = """<script>
(function () {
    /* Dil menüsü: aramalı açılır liste. Diller HTML'deki listeden okunur; JS dil bilgisi taşımaz. */
    var menu = document.getElementById('lang-menu'), btn = document.getElementById('lang-btn');
    if (!menu || !btn) return;
    var input = document.getElementById('lang-search'), empty = document.getElementById('lang-empty');
    var items = Array.prototype.slice.call(document.getElementById('lang-list').children);
    var norm = function (s) { return s.toLowerCase().replace(/ı/g, 'i').normalize('NFD').replace(/[\\u0300-\\u036f]/g, ''); };
    var visible = function () { return items.filter(function (li) { return !li.hidden; }).map(function (li) { return li.firstElementChild; }); };
    var filter = function () {
        var q = norm(input.value.trim()), n = 0;
        items.forEach(function (li) {
            var a = li.firstElementChild, hit = !q || norm(a.textContent).indexOf(q) !== -1 || a.getAttribute('lang').indexOf(q) === 0;
            li.hidden = !hit; if (hit) n++;
        });
        empty.hidden = n > 0;
    };
    var setOpen = function (open) {
        menu.classList.toggle('open', open); btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        if (open) { input.value = ''; filter(); setTimeout(function () { input.focus(); }, 0); }
    };
    btn.addEventListener('click', function () { setOpen(!menu.classList.contains('open')); });
    input.addEventListener('input', filter);
    document.addEventListener('click', function (e) { if (!menu.contains(e.target)) setOpen(false); });
    menu.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') { setOpen(false); btn.focus(); return; }
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
            var vis = visible(); if (!vis.length) return;
            var i = vis.indexOf(document.activeElement), next = e.key === 'ArrowDown' ? (i + 1) % vis.length : (i <= 0 ? vis.length - 1 : i - 1);
            vis[next].focus(); e.preventDefault();
        } else if (e.key === 'Enter' && e.target === input) { var v = visible(); if (v.length) v[0].click(); }
    });
})();
(function () {
    /* Özellik kartları: ilk cümle görünür, gerisi tıklayınca açılır. JS yoksa hepsi açık kalır. */
    var grid = document.querySelector('.feature-grid');
    if (!grid) return;
    grid.classList.add('js');
    Array.prototype.forEach.call(grid.querySelectorAll('.feature-card'), function (card) {
        var btn = card.querySelector('.acc-btn');
        if (!btn) return;
        var set = function (open) {
            card.classList.toggle('open', open);
            btn.setAttribute('aria-expanded', open ? 'true' : 'false');
            btn.firstChild.nodeValue = open ? btn.dataset.less : btn.dataset.more;
        };
        card.addEventListener('click', function (e) {
            if (e.target.closest('a')) return;
            if (window.getSelection && String(window.getSelection()).length) return; /* metin seçerken açma */
            set(!card.classList.contains('open'));
        });
    });
})();
(function () {
    /* Dar ekranda gezinme şeridi yana kayar: aktif sekmeyi görünür alana getir, sağda devam varsa kenarı soldur. */
    var nav = document.querySelector('.mainnav');
    if (nav) {
        var more = function () { nav.classList.toggle('more', nav.scrollLeft + nav.clientWidth < nav.scrollWidth - 2); };
        var act = nav.querySelector('a.active');
        var reveal = function () { if (act && nav.scrollWidth > nav.clientWidth) nav.scrollLeft = Math.max(0, act.offsetLeft - 16); more(); };
        nav.addEventListener('scroll', more, { passive: true }); window.addEventListener('resize', more); reveal();
        if (document.fonts && document.fonts.ready) document.fonts.ready.then(reveal); /* yazı tipi gelince genişlikler değişir */
    }
    var bar = document.getElementById('topbar');
    if (bar) {
        var onScroll = function () { bar.classList.toggle('stuck', window.scrollY > 8); };
        onScroll(); window.addEventListener('scroll', onScroll, { passive: true });
    }
    var rise = document.querySelectorAll('.rise');
    if ('IntersectionObserver' in window && rise.length) {
        var io = new IntersectionObserver(function (es) {
            es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
        }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
        rise.forEach(function (el) { io.observe(el); });
        /* Emniyet: gözlemci ne olursa olsun içerik 1.2 sn sonra görünür olur. */
        setTimeout(function () { rise.forEach(function (el) { el.classList.add('in'); }); }, 1200);
    } else { rise.forEach(function (el) { el.classList.add('in'); }); }

    /* Bölüm listesi sayfadaki başlıklardan üretilir — içerik iki yere yazılmaz. */
    var doc = document.querySelector('.doc'), list = document.getElementById('toc-list');
    if (!doc || !list) return;
    var sel = doc.dataset.toc || 'h2';
    var heads = doc.querySelectorAll(sel);
    if (heads.length < 3) { ['.toc-title', '.toc-list'].forEach(function (c) { var t = document.querySelector(c); if (t) t.hidden = true; }); return; }
    var links = [];
    Array.prototype.forEach.call(heads, function (h, i) {
        var target = h.tagName === 'SUMMARY' ? h.parentNode : h;
        if (!target.id) target.id = 'b' + (i + 1);
        var a = document.createElement('a'); a.href = '#' + target.id; a.textContent = h.textContent.trim();
        if (h.tagName === 'SUMMARY') a.addEventListener('click', function () { h.parentNode.open = true; });
        list.appendChild(a); links.push(a);
    });
    var tick = false;
    var spy = function () {
        tick = false; var best = 0;
        for (var i = 0; i < heads.length; i++) { if (heads[i].closest('[hidden]')) continue; if (heads[i].getBoundingClientRect().top <= 120) best = i; }
        links.forEach(function (a, i) { a.classList.toggle('current', i === best); });
    };
    window.addEventListener('scroll', function () { if (!tick) { tick = true; requestAnimationFrame(spy); } }, { passive: true });
    spy();
    /* Arama filtreledikçe bölüm listesi de daralır. */
    document.addEventListener('docsearch', function () {
        links.forEach(function (a, i) { var target = heads[i].tagName === 'SUMMARY' ? heads[i].parentNode : heads[i]; a.hidden = !!target.closest('[hidden]'); });
        spy();
    });
})();
(function () {
    /* Sayfa içi arama — uygulamadaki "Bu sayfada ara" ile aynı davranış: eşleşen bölümler açılır ve
       gösterilir, eşleşmeyenler gizlenir, kelimeler işaretlenir. Türkçe harflere ve aksana duyarsız. */
    var input = document.getElementById('doc-search'), art = document.querySelector('article.doc');
    if (!input || !art) return;
    var clearBtn = document.getElementById('doc-search-clear'), status = document.getElementById('doc-search-status');
    var fold = function (s) {
        var out = '';
        for (var i = 0; i < s.length; i++) {
            var c = s[i];
            if (c === 'ı' || c === 'İ') { out += 'i'; continue; }
            var b = c.normalize('NFD')[0] || c, l = b.toLowerCase();
            out += l.length === 1 ? l : b;
        }
        return out;
    };
    /* Birimler: h2 bir grup açar; her <details> kendi başına birim; h2 altındaki düz metin tek birim. */
    var groups = [], cur = null;
    Array.prototype.forEach.call(art.children, function (el) {
        if (el.tagName === 'H2') { cur = { head: el, items: [] }; groups.push(cur); return; }
        if (!cur) { cur = { head: null, items: [] }; groups.push(cur); }
        if (el.tagName === 'DETAILS') { cur.items.push({ nodes: [el], det: el }); return; }
        var last = cur.items[cur.items.length - 1];
        if (!last || last.det) { last = { nodes: [], det: null }; cur.items.push(last); }
        last.nodes.push(el);
    });
    var saved = null; /* arama başlamadan önceki açık/kapalı durumu */
    var textOf = function (nodes) { return nodes.map(function (n) { return n.textContent; }).join(' '); };
    var unmark = function () {
        Array.prototype.forEach.call(art.querySelectorAll('mark.hit'), function (m) { m.replaceWith(m.textContent); });
        art.normalize();
    };
    var mark = function (root, q) {
        var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT), nodes = [], n = 0;
        while (walker.nextNode()) nodes.push(walker.currentNode);
        nodes.forEach(function (t) {
            var v = t.nodeValue, f = fold(v), i = f.indexOf(q);
            if (i < 0) return;
            var frag = document.createDocumentFragment(), last = 0;
            while (i >= 0) {
                if (i > last) frag.appendChild(document.createTextNode(v.slice(last, i)));
                var m = document.createElement('mark'); m.className = 'hit'; m.textContent = v.slice(i, i + q.length); frag.appendChild(m);
                last = i + q.length; n++; i = f.indexOf(q, last);
            }
            if (last < v.length) frag.appendChild(document.createTextNode(v.slice(last)));
            t.parentNode.replaceChild(frag, t);
        });
        return n;
    };
    var setHidden = function (nodes, h) { nodes.forEach(function (n) { n.hidden = h; }); };
    var reset = function () {
        unmark();
        groups.forEach(function (g) { if (g.head) g.head.hidden = false; g.items.forEach(function (it) { setHidden(it.nodes, false); }); });
        if (saved) { saved.forEach(function (o, d) { d.open = o; }); saved = null; }
        Array.prototype.forEach.call(art.querySelectorAll('h2.first-visible'), function (h) { h.classList.remove('first-visible'); });
        status.textContent = ''; clearBtn.hidden = true;
        document.dispatchEvent(new Event('docsearch'));
    };
    var run = function () {
        var q = fold(input.value.trim());
        clearBtn.hidden = !input.value;
        if (q.length < 2) { if (saved) reset(); else { status.textContent = ''; } return; }
        if (!saved) { saved = new Map(); Array.prototype.forEach.call(art.querySelectorAll('details'), function (d) { saved.set(d, d.open); }); }
        unmark();
        var hits = 0, sections = 0;
        groups.forEach(function (g) {
            var whole = g.head && g.items.length && !g.items[0].det; /* gizlilik/koşullar: başlık + metin tek birim */
            var any = false;
            if (whole) {
                var all = [g.head].concat(g.items[0].nodes);
                any = fold(textOf(all)).indexOf(q) !== -1;
                g.head.hidden = !any; setHidden(g.items[0].nodes, !any);
                if (any) { sections++; all.forEach(function (n) { hits += mark(n, q); }); }
            } else {
                g.items.forEach(function (it) {
                    var ok = fold(textOf(it.nodes)).indexOf(q) !== -1;
                    setHidden(it.nodes, !ok);
                    if (ok) { any = true; sections++; if (it.det) it.det.open = true; it.nodes.forEach(function (n) { hits += mark(n, q); }); }
                });
                if (g.head) g.head.hidden = !any;
            }
        });
        var firstSeen = false;
        Array.prototype.forEach.call(art.querySelectorAll(':scope > h2'), function (h) { var f = !firstSeen && !h.hidden; h.classList.toggle('first-visible', f); if (f) firstSeen = true; });
        status.textContent = hits ? status.dataset.count.replace('{n}', hits).replace('{m}', sections).replace('{es}', hits === 1 ? '' : 'es').replace('{s}', sections === 1 ? '' : 's') : status.dataset.none;
        document.dispatchEvent(new Event('docsearch'));
    };
    var timer = null;
    input.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(run, 220); });
    input.addEventListener('keydown', function (e) { if (e.key === 'Escape') { input.value = ''; reset(); } });
    clearBtn.addEventListener('click', function () { input.value = ''; reset(); input.focus(); });
})();
</script>"""

def build_doc(fname, lang, alt, toc_sel):
    src = io.open(os.path.join(SRC, fname), encoding='utf-8').read()
    h1 = re.search(r'<main>.*?<h1>(.*?)</h1>', src, re.S).group(1).strip()
    m = re.search(r'<p class="subtitle">(.*?)</p>', src, re.S)
    sub = ('<p class="subtitle">%s</p>' % m.group(1).strip()) if m else ''
    gen = re.search(r'(<!-- GENERATED:.*?-END -->)', src, re.S).group(1)
    out = """<!DOCTYPE html>
<html lang="%s">
%s
<body>

%s

<main>
    <div class="wrap page-head">
        <h1>%s</h1>
        %s
    </div>
    <div class="wrap doc-layout">
        <aside class="toc">
            <div class="doc-search">
                <label class="search-box">%s<input type="search" id="doc-search" placeholder="%s" autocomplete="off" spellcheck="false" aria-label="%s"><button type="button" class="search-clear" id="doc-search-clear" aria-label="%s" hidden>%s</button></label>
                <p class="search-status" id="doc-search-status" aria-live="polite" data-none="%s" data-count="%s"></p>
            </div>
            <div class="toc-title">%s</div>
            <div class="toc-list" id="toc-list"></div>
        </aside>
        <article class="doc" data-toc="%s">
%s
        </article>
    </div>
</main>

%s

%s
</body>
</html>
""" % (lang, head_of(src), topbar(lang, fname, alt), h1, sub,
       ICON_SEARCH, DOC_SEARCH[lang]['ph'], DOC_SEARCH[lang]['ph'], DOC_SEARCH[lang]['clear'], ICON_X, DOC_SEARCH[lang]['none'], DOC_SEARCH[lang]['count'],
       TOC_TITLE[lang], toc_sel, gen, footer(lang), JS)
    io.open(os.path.join(OUT, fname), 'w', encoding='utf-8').write(out)

def split_lede(t):
    """İlk cümleyi ayırır (cümle sonu + büyük harf); kalan kısa ise bölmez."""
    m = re.search(r'\.\s+(?=[A-ZÇĞİÖŞÜ])', t)
    if not m or len(t) - m.end() < 80: return t, ''
    return t[:m.start()+1], t[m.end():]

def build_home(lang):
    C = HOME[lang]
    src = io.open(os.path.join(HOME_SRC, C['file']), encoding='utf-8').read()
    desc = re.findall(r'<p class="desc">(.*?)</p>', src, re.S)[0].strip()
    note = re.findall(r'<p class="hero-note">(.*?)</p>', src, re.S)[0].strip()
    cards = re.findall(r'<h3>(.*?)</h3>\s*<p>(.*?)</p>', src, re.S)
    tail = src.split('</div>\n\n    <h2>')[-1]
    secs = re.findall(r'<h2>(.*?)</h2>(.*?)(?=<h2>|</main>)', '<h2>' + tail, re.S)

    # Tanıtım metnini iki paragrafa böl (cümle sınırında, boşluk korunarak)
    sents = re.split(r'(?<=\.)\s+(?=[A-ZÇĞİÖŞÜ])', desc)
    paras = [' '.join(sents[:-1]), sents[-1]] if len(sents) > 1 else [desc]

    # Başlık satır başında metnin içine girer ("Sunucusuz mimari: ..."); ilk cümle hep görünür,
    # gerisi "Devamını göster" ile açılır (JS yoksa her şey açık kalır).
    card_html = []
    for h3, p in cards:
        lede, rest = split_lede(p.strip())
        card = '            <div class="feature-card rise">\n                <p><strong class="rt">%s:</strong> %s</p>' % (h3.strip(), lede)
        if rest:
            card += ('\n                <div class="acc-body"><div><p>%s</p></div></div>'
                     '\n                <button type="button" class="acc-btn" aria-expanded="false" data-more="%s" data-less="%s">%s%s</button>') % (rest, C['more'], C['less'], C['more'], ICON_CHEV)
        card_html.append(card + '\n            </div>')

    # Kapanış bandı: kartlardan ayrı bir dil — büyük harfli küçük etiket, düz metin, e-posta düğme.
    closing = []
    for h2, body in secs:
        rows = ['            <p class="eyebrow">%s</p>' % h2.strip()]
        for x in re.findall(r'<p>(.*?)</p>', body, re.S):
            x = x.strip()
            m = re.search(r'<a href="(mailto:[^"]+)">([^<]+)</a>', x)
            if m:
                lead = x[:m.start()].strip()
                if lead: rows.append('            <p>%s</p>' % lead)
                rows.append('            <a class="mail" href="%s">%s%s</a>' % (m.group(1), ICON_MAIL, m.group(2)))
            else:
                rows.append('            <p>%s</p>' % x)
        closing.append('        <div class="closing-col">\n%s\n        </div>' % '\n'.join(rows))

    out = """<!DOCTYPE html>
<html lang="%s">
%s
<body>

%s

<main>
    <section class="wrap hero">
        <div class="hero-text">
            <h1>%s <span class="soft">%s</span></h1>
%s
        </div>
        <div class="notice %s">
            <span class="dot"></span>
            <p><strong>%s</strong>; %s</p>
        </div>
        <div class="stores">
%s
        </div>
    </section>

    <section class="wrap section" id="ozellikler">
        <div class="section-head rise">
            <h2>%s</h2>
        </div>
        <div class="feature-grid">
%s
        </div>
    </section>

    <section class="wrap section closing rise">
        <div class="closing-band">
%s
        </div>
    </section>
</main>

%s

%s
</body>
</html>
""" % (lang, head_of(src), topbar(lang, C['file'], C['alt']), C['h1a'], C['h1b'],
       '\n'.join('        <p class="lede">%s</p>' % p for p in paras),
       NOTICE_STATUS, C['notice'], note, stores(lang), C['feat'], '\n'.join(card_html),
       '\n'.join(closing), footer(lang), JS)
    io.open(os.path.join(OUT, C['file']), 'w', encoding='utf-8').write(out)
    return len(cards)

os.makedirs(OUT, exist_ok=True)
for tr, en, sel in [('privacy-tr.html','privacy-en.html','h2'), ('terms-tr.html','terms-en.html','h2'),
                    ('faq-tr.html','faq-en.html','h2.faq-group'), ('guide-tr.html','guide-en.html','.guide-section > summary')]:
    build_doc(tr, 'tr', en, sel); build_doc(en, 'en', tr, sel)
n1 = build_home('tr'); n2 = build_home('en')
print('üretildi → %s (anasayfa kart: %d/%d)' % (OUT, n1, n2))
