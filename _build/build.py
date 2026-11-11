#!/usr/bin/env python3
"""CL Partners static site builder.

Assembles _build/pages/*.html bodies into full pages in site/ with a shared
header, footer, modals and SEO head. Run:  python3 _build/build.py
Tokens available inside page bodies:
  {{icon:name}}          inline Lucide icon
  {{img:PHOTO_ID:W}}     Unsplash image URL at width W
  {{curve}} {{curve:alt|mist|dark}}   signature flowing curve divider
  {{dots}} {{dots:class}}             orange dot cluster from the logo
  {{form:contact}} {{form:careers}}   form markup
"""
import re, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_build" / "pages"
OUT = ROOT / "site"
SITE_URL = "https://www.cl-partners.ch"

ICONS = {
    "arrow-right": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "play": '<polygon points="6 3 20 12 6 21 6 3"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/>',
    "mail": '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "map-pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "linkedin": '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect width="4" height="12" x="2" y="9"/><circle cx="4" cy="4" r="2"/>',
    "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    "menu": '<line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/>',
    "chevron-down": '<path d="m6 9 6 6 6-6"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "building": '<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/>',
    "flask": '<path d="M10 2v7.527a2 2 0 0 1-.211.896L4.72 20.55a1 1 0 0 0 .9 1.45h12.76a1 1 0 0 0 .9-1.45l-5.069-10.127A2 2 0 0 1 14 9.527V2"/><path d="M8.5 2h7"/><path d="M7 16h10"/>',
    "trending-up": '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "compass": '<circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>',
    "home": '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "lock": '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
    "message": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "layers": '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>',
    "refresh": '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',
    "pen": '<path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
    "check-square": '<path d="m9 11 3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
    "pencil": '<path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
    "circle-check": '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    "eye": '<path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
    "sparkle": '<path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/>',
    "heart": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
    "award": '<circle cx="12" cy="8" r="6"/><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/>',
    "send": '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
    "triangle": '<path d="M13.73 4a2 2 0 0 0-3.46 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
}

def icon(name, cls="icon"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{ICONS[name]}</svg>'

def img(pid, w):
    return f"https://images.unsplash.com/photo-{pid}?auto=format&fit=crop&w={w}&q=80"

# Dot cluster traced from the logo (orange particles)
DOTS = [(606,16,16),(729,63,19),(549,81,16),(511,122,16),(642,129,19),(874,118,22),(597,164,19),(755,184,23),(1070,191,26),(670,230,22),(882,250,26),(716,305,26),(998,361,23),(738,401,22),(842,384,23),(734,487,19),(809,491,20),(940,497,19),(706,575,16),(775,590,16),(894,612,16)]
def dots(cls=""):
    circles = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" style="animation-delay:-{(i*0.37)%7:.2f}s"/>' for i,(x,y,r) in enumerate(DOTS))
    return f'<svg class="{cls}" viewBox="490 0 610 640" aria-hidden="true" focusable="false"><g fill="#FF9900">{circles}</g></svg>'

def mark(cls=""):
    """White CL symbol, used solid and sparingly on dark surfaces."""
    return f'<img class="cl-mark {cls}" src="assets/img/cl-mark-white.png" alt="" aria-hidden="true" width="400" height="308" loading="lazy">'

def trail(cls=""):
    """Four orange dots rising in one direction, echoing the logo's particles."""
    pts = [(8, 92, 5), (34, 66, 7), (62, 40, 9.5), (94, 12, 12)]
    c = "".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in pts)
    return f'<svg class="dot-trail {cls}" viewBox="0 0 108 104" aria-hidden="true" focusable="false"><g fill="#FF9900">{c}</g></svg>'

RES = [
    ("efn", "executive-field-notes.html", "Executive Field Notes", "Free download", "Practical one-page tools for key leadership moments: seven questions, three traps and a short exercise.", "3 notes · more coming", "file", ""),
    ("tek", "team-effectiveness-toolkit.html", "Team Effectiveness Conversations", "Toolkit 01", "A team check-in and 45 exercises across Leading Self, Leading Teams and Leading Organization.", "Interactive check-in", "users", "assets/img/toolkit.jpg"),
    ("tbk", "team-building-toolkit.html", "Team Building Activities", "Toolkit 02", "45 shared experiences in 5 activity families to build trust, connection and positive energy.", "5 families · 45 activities", "sparkle", "assets/img/toolkit-teambuilding.jpg"),
    ("persp", "perspectives.html", "Perspectives", "Point of view", "Points of view that help leaders see a business situation differently: what we observe, what is often misunderstood and which decisions matter.", "First articles in preparation", "pen", ""),
]

def res_media(key, im):
    if key == "efn":
        sheets = "".join(f'<img class="efn-sheet s{n}" src="assets/img/efn0{n}-cover.jpg" alt="" loading="lazy" width="520" height="735">' for n in (3, 2, 1))
        return f'<div class="res-media res-efn">{sheets}'
    if key == "persp":
        return (f'<div class="res-media res-persp"><span class="pq" aria-hidden="true">“</span>'
                f'<span class="pq-lines" aria-hidden="true"><i></i><i></i><i></i></span>{mark("pq-mark")}')
    return f'<div class="res-media res-photo"><img src="{im}" alt="" loading="lazy" width="1254" height="1254">'

def res_card(r, i=0):
    key, href, title, kicker, desc, meta, ic, im = r
    return (f'<a class="res-card reveal" style="--d:{i*80}ms" href="{href}">'
            f'{res_media(key, im)}<span class="res-kicker">{kicker}</span></div>'
            f'<div class="res-body"><div class="icon-chip">{icon(ic)}</div><h3>{title}</h3><p>{desc}</p>'
            f'<div class="res-foot"><span class="res-meta">{meta}</span><span class="link-arrow">Open {icon("arrow-right")}</span></div></div></a>')

def reshub():
    return '<div class="res-grid">' + "".join(res_card(r, i) for i, r in enumerate(RES)) + '</div>'

def morres(current):
    others = [r for r in RES if r[0] != current]
    return ('<section class="section section-tight" aria-labelledby="more-res-title"><div class="container">'
            '<div class="section-head reveal" style="margin-bottom:var(--s4)"><p class="eyebrow">More resources</p>'
            '<h2 id="more-res-title" style="font-size:var(--fs-xl)">Keep exploring</h2></div>'
            '<div class="res-grid res-grid-3">' + "".join(res_card(r, i) for i, r in enumerate(others)) + '</div></div></section>')

def curve(variant=""):
    cls = f"curve to-{variant}" if variant else "curve"
    return (f'<svg class="{cls}" viewBox="0 0 1440 160" preserveAspectRatio="none" aria-hidden="true" focusable="false">'
            '<path class="fill" d="M0 160V104C320 158 760 46 1440 78V160Z"/>'
            '<path class="c-cyan" d="M0 104C320 158 760 46 1440 78"/>'
            '<path class="c-orange" d="M980 52C1150 30 1310 30 1440 46"/></svg>')

def field(name, label, type_="text", required=True, autocomplete=None, placeholder="", hint="", fid=None, extra=""):
    fid = fid or f"f-{name}"
    req = ' required' if required else ''
    mark = '<span class="req" aria-hidden="true">*</span>' if required else ' <span class="opt">(optional)</span>'
    ac = f' autocomplete="{autocomplete}"' if autocomplete else ''
    ph = f' placeholder="{placeholder}"' if placeholder else ''
    desc = f"{fid}-err" + (f" {fid}-hint" if hint else "")
    hint_html = f'<span class="field-hint" id="{fid}-hint">{hint}</span>' if hint else ''
    if type_ == "textarea":
        ctrl = f'<textarea class="textarea" id="{fid}" name="{name}"{req}{ph} aria-describedby="{desc}"{extra}></textarea>'
    else:
        ctrl = f'<input class="input" id="{fid}" name="{name}" type="{type_}"{req}{ac}{ph} aria-describedby="{desc}"{extra}>'
    return f'<div class="field"><label for="{fid}">{label}{mark}</label>{ctrl}{hint_html}<span class="field-error" id="{fid}-err" role="alert"></span></div>'

def consent(fid, text):
    return (f'<div class="check-field field"><label class="check" for="{fid}"><input type="checkbox" id="{fid}" name="consent" required aria-describedby="{fid}-err">'
            f'<span>{text}</span></label><span class="field-error" id="{fid}-err" role="alert"></span></div>')

HONEYPOT = '<div class="sr-only" aria-hidden="true"><label for="{id}">Leave empty</label><input id="{id}" name="website" tabindex="-1" autocomplete="off"></div>'

def submit_btn(label):
    return f'<button type="submit" class="btn btn-orange"><span class="spinner" aria-hidden="true"></span>{label}<span class="btn-arrow">{icon("arrow-right")}</span></button>'

FORMS = {
"contact": f'''<div class="form-wrap">
<form class="form" data-form="contact" novalidate>
  <div class="error-summary" tabindex="-1" role="alert"></div>
  <div class="form-row">{field("name","Name",autocomplete="name")}{field("company","Company",autocomplete="organization")}</div>
  <div class="form-row">{field("role","Role",autocomplete="organization-title")}{field("email","Email","email",autocomplete="email")}</div>
  {field("phone","Phone","tel",required=False,autocomplete="tel")}
  {field("message","Briefly describe your business situation","textarea",placeholder="What needs to change, what is getting in the way, and who is involved?")}
  {consent("c-consent", 'I agree that CL Partners may use these details to respond to my enquiry, as described in the <a href="privacy.html">privacy notice</a>.')}
  {HONEYPOT.format(id="c-hp")}
  <div class="btn-row">{submit_btn("Send your message")}</div>
</form>
<div class="form-success" aria-live="polite">
  <div class="success-mark">{icon("check")}</div>
  <h3>Thank you, your message is on its way.</h3>
  <p class="muted measure mx-auto">We will come back to you to explore whether a conversation would be useful.</p>
</div></div>''',
"careers": f'''<div class="form-wrap">
<form class="form" data-form="careers" novalidate>
  <div class="error-summary" tabindex="-1" role="alert"></div>
  <div class="form-row">{field("name","Full name",autocomplete="name",fid="j-name")}{field("email","Email","email",autocomplete="email",fid="j-email")}</div>
  <div class="form-row">
    <div class="field"><label for="j-interest">I am interested in<span class="req" aria-hidden="true">*</span></label>
      <select class="select input" id="j-interest" name="interest" required aria-describedby="j-interest-err">
        <option value="">Select…</option><option>Senior Partner</option><option>Consultant</option><option>Associate / Interim expertise</option><option>Something else</option>
      </select><span class="field-error" id="j-interest-err" role="alert"></span></div>
    {field("linkedin","LinkedIn profile","url",required=False,autocomplete="url",placeholder="https://linkedin.com/in/…",fid="j-linkedin")}
  </div>
  {field("message","What would you bring to CL Partners?","textarea",placeholder="Your expertise, the leaders and situations you work best with, and why CL Partners.",fid="j-message")}
  <p class="form-note">You are welcome to email your CV to <a href="mailto:welcome@cl-partners.ch">welcome@cl-partners.ch</a> after sending this form.</p>
  {consent("j-consent", 'I agree that CL Partners may keep these details to consider my application, as described in the <a href="privacy.html">privacy notice</a>.')}
  {HONEYPOT.format(id="j-hp")}
  <div class="btn-row">{submit_btn("Send application")}</div>
</form>
<div class="form-success" aria-live="polite">
  <div class="success-mark">{icon("check")}</div>
  <h3>Thank you for reaching out.</h3>
  <p class="muted measure mx-auto">We read every message personally and will be in touch if there is a fit with how CL Partners is growing.</p>
</div></div>''',
}

NAV = [
    ("expertise", "Expertise", None),
    ("how-we-work", "How We Work", "how-we-work.html"),
    ("cases", "Cases", "cases.html"),
    ("resources", "Resources", "resources.html"),
    ("about", "About", "about.html"),
]

def header(active):
    def cur(k): return ' aria-current="page"' if k == active else ''
    exp_active = ' is-active' if active in ("oe", "lte") else ''
    items = [f'''<li><button class="nav-link{exp_active}" type="button" data-dropdown aria-expanded="false" aria-controls="dd-expertise">Expertise {icon("chevron-down")}</button>
      <div class="dropdown" id="dd-expertise">
        <a href="organization-effectiveness.html"{cur("oe")}><strong>Organization Effectiveness</strong><span>Governance, operating model, M&amp;A integration and PE value creation</span></a>
        <a href="leadership-team-effectiveness.html"{cur("lte")}><strong>Leadership &amp; Team Effectiveness</strong><span>Executive team alignment, change leadership and transitions</span></a>
      </div></li>''']
    res_keys = ("resources", "efn", "tek", "tbk", "persp")
    for key, label, href in NAV[1:]:
        if key == "resources":
            ra = ' is-active' if active in res_keys else ''
            links = f'<a href="resources.html"{cur("resources")}><strong>All resources</strong><span>Overview of our free tools for leaders</span></a>' + "".join(
                f'<a href="{r[1]}"{cur(r[0])}><strong>{r[2]}</strong><span>{r[5]}</span></a>' for r in RES)
            items.append(f'''<li><button class="nav-link{ra}" type="button" data-dropdown aria-expanded="false" aria-controls="dd-resources">Resources {icon("chevron-down")}</button>
      <div class="dropdown" id="dd-resources">{links}</div></li>''')
        else:
            items.append(f'<li><a class="nav-link" href="{href}"{cur(key)}>{label}</a></li>')
    mobile = [("organization-effectiveness.html","Organization Effectiveness","oe",True),("leadership-team-effectiveness.html","Leadership &amp; Team Effectiveness","lte",True),
              ("how-we-work.html","How We Work","how-we-work",False),("cases.html","Cases","cases",False),("resources.html","Resources","resources",False),
              ("executive-field-notes.html","Executive Field Notes","efn",True),("team-effectiveness-toolkit.html","Team Effectiveness Conversations","tek",True),
              ("team-building-toolkit.html","Team Building Activities","tbk",True),("perspectives.html","Perspectives","persp",True),
              ("about.html","About","about",False),("join-our-team.html","Join our team","join",False),("contact.html","Contact","contact",False)]
    sub_cls = ' class="sub"'
    mob = "".join(f'<a href="{h}"{sub_cls if s else ""}{cur(k)}>{l}{icon("arrow-right")}</a>' for h,l,k,s in mobile)
    return f'''<a class="skip-link" href="#main">Skip to main content</a>
<header class="site-header">
  <div class="container">
    <div class="nav-shell">
      <a class="brand" href="index.html" aria-label="CL Partners home"><img src="assets/img/logo.png" alt="CL Partners" width="180" height="93"></a>
      <nav aria-label="Primary"><ul class="nav-primary">{"".join(items)}</ul></nav>
      <div class="nav-cta">
        <a class="btn btn-sm" href="contact.html"{cur("contact")}>Start a conversation {icon("arrow-right")}</a>
        <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="Open menu">{icon("menu")}</button>
      </div>
    </div>
  </div>
</header>
<div class="mobile-menu" id="mobile-menu" aria-hidden="true" role="dialog" aria-modal="true" aria-label="Menu">
  <div class="mobile-menu-top"><a class="brand" href="index.html"><img src="assets/img/logo.png" alt="CL Partners home" width="140" height="72"></a>
  <button class="menu-close" type="button" aria-label="Close menu">{icon("x")}</button></div>
  <nav aria-label="Mobile"><p class="mm-label">Expertise</p>{mob}</nav>
  <a class="btn btn-orange btn-block" href="contact.html">Start a conversation {icon("arrow-right")}</a>
  <div class="mobile-menu-contact">Rue Rothschild 50, 1202 Geneva<br><a href="mailto:welcome@cl-partners.ch">welcome@cl-partners.ch</a></div>
</div>'''

FOOTER = f'''<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="assets/img/logo.png" alt="CL Partners" width="124" height="64" loading="lazy">
        <p>Executive Business Skippers for growth, integration and transformation. Based in Geneva, working with international leaders.</p>
        <div class="footer-social"><a class="social-btn" href="https://www.linkedin.com/company/cl-partners-ch/" target="_blank" rel="noopener" aria-label="CL Partners on LinkedIn">{icon("linkedin")}</a>
        <a class="social-btn" href="mailto:welcome@cl-partners.ch" aria-label="Email CL Partners">{icon("mail")}</a></div>
      </div>
      <div class="footer-col"><h2>Expertise</h2><ul>
        <li><a href="organization-effectiveness.html">Organization Effectiveness</a></li>
        <li><a href="organization-effectiveness.html#mna">M&amp;A integration</a></li>
        <li><a href="organization-effectiveness.html#pe">PE value creation</a></li>
        <li><a href="leadership-team-effectiveness.html">Leadership &amp; Team Effectiveness</a></li></ul></div>
      <div class="footer-col"><h2>Firm</h2><ul>
        <li><a href="how-we-work.html">How We Work</a></li>
        <li><a href="cases.html">Cases</a></li>
        <li><a href="about.html">About</a></li>
        <li><a href="join-our-team.html">Join our team</a></li></ul></div>
      <div class="footer-col"><h2>Resources</h2><ul>
        <li><a href="executive-field-notes.html">Executive Field Notes</a></li>
        <li><a href="team-effectiveness-toolkit.html">Team Effectiveness Toolkit</a></li>
        <li><a href="team-building-toolkit.html">Team Building Toolkit</a></li>
        <li><a href="perspectives.html">Perspectives</a></li></ul></div>
      <div class="footer-col"><h2>Contact</h2>
        <address>CL Partners Sàrl<br>Rue Rothschild 50<br>1202 Geneva, Switzerland<br>
        <a href="mailto:welcome@cl-partners.ch">welcome@cl-partners.ch</a></address></div>
    </div>
    <div class="footer-bottom"><span>© <span data-year>2026</span> CL Partners Sàrl. All rights reserved.</span>
      <span><a href="privacy.html">Privacy notice</a> · <a href="contact.html">Contact</a></span></div>
  </div>
</footer>'''

LEAD_MODAL = f'''<div class="modal" id="lead-modal" aria-hidden="true" role="dialog" aria-modal="true" aria-labelledby="lead-title">
  <div class="modal-backdrop" data-close></div>
  <div class="modal-dialog">
    <button class="modal-close" type="button" data-close aria-label="Close">{icon("x")}</button>
    <div class="modal-aside">
      <span class="no" data-res-no>Executive Field Note</span>
      <h2 id="lead-title" data-res-title>Executive Field Note</h2>
      <p data-res-sub></p>
      <ul><li>Seven questions to ask before you act</li><li>Three traps to avoid</li><li>A short exercise to use with your team</li><li>A real-world example from life sciences</li></ul>
      <img class="modal-mark" src="assets/img/cl-mark-white.png" alt="" aria-hidden="true" width="120" height="92">
    </div>
    <div class="modal-main">
      <form class="form" novalidate>
        <div><h3>Get your free copy</h3><p class="muted" style="font-size:var(--fs-sm)">Tell us who you are and the PDF downloads straight away.</p></div>
        <div class="error-summary" tabindex="-1" role="alert"></div>
        {field("name","Full name",autocomplete="name",fid="l-name",extra=" data-autofocus")}
        {field("company","Company",autocomplete="organization",fid="l-company")}
        {field("email","Work email","email",autocomplete="email",fid="l-email")}
        <label class="check" for="l-updates"><input type="checkbox" id="l-updates" name="updates" value="yes"><span>Notify me when a new Executive Field Note is published.</span></label>
        {consent("l-consent", 'I agree to the <a href="privacy.html">privacy notice</a>.')}
        {HONEYPOT.format(id="l-hp")}
        {submit_btn("Download the Field Note")}
      </form>
      <div class="form-success" aria-live="polite">
        <div class="success-mark">{icon("check")}</div>
        <h3>Thank you<span data-success-name-wrap>, <span data-success-name></span></span>. Your download has started.</h3>
        <p class="muted">If it did not start, use the button below.</p>
        <a class="btn" href="#" data-res-link download>{icon("download")} Download PDF</a>
      </div>
    </div>
  </div>
</div>'''

VIDEO_MODAL = f'''<div class="modal modal-video" id="video-modal" aria-hidden="true" role="dialog" aria-modal="true" aria-label="CL Partners presentation video">
  <div class="modal-backdrop" data-close></div>
  <div class="modal-dialog">
    <button class="modal-close" type="button" data-close aria-label="Close video">{icon("x")}</button>
    <video controls playsinline preload="none" src="assets/video/cl-partners-presentation.mp4"></video>
  </div>
</div>'''

def head(title, desc, slug, og_image):
    url = f"{SITE_URL}/{'' if slug=='index' else slug + '.html'}"
    return f'''<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:site_name" content="CL Partners">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#035397">
<link rel="icon" type="image/png" href="assets/img/favicon.png">
<link rel="preconnect" href="https://images.unsplash.com" crossorigin>
<link rel="stylesheet" href="css/styles.css">
'''

ORG_LD = {
    "@context": "https://schema.org", "@type": "ProfessionalService", "name": "CL Partners Sàrl",
    "url": SITE_URL, "logo": f"{SITE_URL}/assets/img/logo.png", "email": "welcome@cl-partners.ch",
    "address": {"@type": "PostalAddress", "streetAddress": "Rue Rothschild 50", "postalCode": "1202", "addressLocality": "Geneva", "addressCountry": "CH"},
    "founder": {"@type": "Person", "name": "Christian Lefèvre", "jobTitle": "Founder & Managing Partner", "sameAs": "https://www.linkedin.com/in/christianlefevre/"},
    "areaServed": ["Switzerland", "EMEA"],
    "knowsAbout": ["Organization effectiveness", "Operating model design", "Post-merger integration", "Carve-outs and separations", "Executive team effectiveness", "Leadership transitions", "Life sciences"],
    "sameAs": ["https://www.linkedin.com/company/cl-partners-ch/"],
}

PAGES = [
    # slug, title, description, active, hero image id (og)
    ("index", "CL Partners | Executive Business Skippers for growth, integration and transformation",
     "Geneva-based advisory and implementation firm. CL Partners works alongside CEOs and executive teams on organization effectiveness, M&A integration and leadership team effectiveness.", "home", "1633022326182-1b36700bc49a"),
    ("organization-effectiveness", "Organization Effectiveness, M&A Integration & PE Value Creation | CL Partners",
     "Build the organization your strategy needs: governance, decision rights, operating model, M&A integration, carve-outs and PE portfolio value creation. Geneva, Switzerland and EMEA.", "oe", "1714974528693-f77f6fcc56af"),
    ("leadership-team-effectiveness", "Leadership & Team Effectiveness | CL Partners",
     "From capable individuals to a leadership team that delivers. Executive team alignment, High Impact Leadership Team journeys, change leadership and leadership transitions.", "lte", "1758518731706-be5d5230e5a5"),
    ("how-we-work", "How We Work: The Executive Business Skipper approach | CL Partners",
     "An experienced peer who listens, challenges constructively and works alongside leaders to turn decisions into action. How CL Partners engages.", "how-we-work", "1758873269035-aae0e1fd3422"),
    ("cases", "Cases: Integration, separation and change leadership | CL Partners",
     "Business stories from CL Partners mandates and our founder's executive experience in international life sciences: post-acquisition integration, separation and change leadership.", "cases", "1630959305790-4c956ce6c0b6"),
    ("about", "About CL Partners and Christian Lefèvre | Geneva",
     "CL Partners is a Geneva-based advisory and implementation firm founded by Christian Lefèvre, former executive at Pfizer/Wyeth, UCB and Novartis.", "about", "1584200463394-bba4b2117e4d"),
    ("resources", "Resources: Executive Field Notes & Team Toolkits | CL Partners",
     "Practical resources for leaders: Executive Field Notes, the Team Effectiveness Conversations and Team Building Activities toolkits, and Perspectives on organization, leadership and change.", "resources", "1758873269811-4e62e346b4b7"),
    ("executive-field-notes", "Executive Field Notes: free one-page guides for leaders | CL Partners",
     "Free one-page Executive Field Notes: seven questions, three traps and a short exercise for key leadership moments. New notes published regularly.", "efn", "1714974528737-3e6c7e4d11af"),
    ("team-effectiveness-toolkit", "Team Effectiveness Conversations toolkit | CL Partners",
     "An open toolkit to grow together: interactive team check-in, 3 leadership perspectives and 45 exercises for leadership teams.", "tek", "1758873269035-aae0e1fd3422"),
    ("team-building-toolkit", "Team Building Activities toolkit | CL Partners",
     "Shared experiences, stronger teams: 5 activity families, 15 themes and 45 team building activities with a facilitation guide.", "tbk", "1758518731706-be5d5230e5a5"),
    ("perspectives", "Perspectives on organization, leadership and change | CL Partners",
     "Practical perspectives for leaders on the organization and leadership choices behind growth, integration, restructuring and change.", "persp", "1714974528718-b3b52f91c334"),
    ("contact", "Contact CL Partners | Start a confidential conversation",
     "Tell us what needs to change. CL Partners Sàrl, Rue Rothschild 50, 1202 Geneva.", "contact", "1663789529247-974d4d08ce3a"),
    ("join-our-team", "Join our team | CL Partners",
     "Open to conversations with senior partners, consultants, coaches and interim leaders who want to build something with CL Partners in Geneva.", "join", "1758873269811-4e62e346b4b7"),
    ("privacy", "Privacy notice | CL Partners", "How CL Partners handles personal data submitted through this website.", "privacy", "1633022326182-1b36700bc49a"),
]

def render_tokens(s):
    s = re.sub(r"\{\{icon:([\w-]+)\}\}", lambda m: icon(m.group(1)), s)
    s = re.sub(r"\{\{img:([\w-]+):(\d+)\}\}", lambda m: img(m.group(1), m.group(2)), s)
    s = re.sub(r"\{\{curve(?::(\w+))?\}\}", lambda m: curve(m.group(1) or ""), s)
    s = re.sub(r"\{\{dots(?::([\w -]+))?\}\}", lambda m: dots(m.group(1) or ""), s)
    s = re.sub(r"\{\{mark(?::([\w -]+))?\}\}", lambda m: mark(m.group(1) or ""), s)
    s = re.sub(r"\{\{trail(?::([\w -]+))?\}\}", lambda m: trail(m.group(1) or ""), s)
    s = s.replace("{{reshub}}", reshub())
    s = re.sub(r"\{\{morres:(\w+)\}\}", lambda m: morres(m.group(1)), s)
    s = re.sub(r"\{\{form:(\w+)\}\}", lambda m: FORMS[m.group(1)], s)
    return s

def build():
    for slug, title, desc, active, og in PAGES:
        body = render_tokens((SRC / f"{slug}.html").read_text(encoding="utf-8"))
        ld = ""
        if slug == "index":
            ld = f'<script type="application/ld+json">{json.dumps(ORG_LD, ensure_ascii=False)}</script>\n'
        html = (head(title, desc, slug, img(og, 1200)) + ld + "</head>\n<body>\n" + header(active)
                + '\n<main id="main">\n' + body + "\n</main>\n" + FOOTER + "\n" + LEAD_MODAL + "\n" + VIDEO_MODAL
                + '\n<script src="js/main.js" defer></script>\n</body>\n</html>\n')
        (OUT / f"{slug}.html").write_text(html, encoding="utf-8")
        print("built", slug)
    # sitemap + robots
    urls = "".join(f"<url><loc>{SITE_URL}/{'' if s=='index' else s+'.html'}</loc></url>" for s,*_ in PAGES)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")

if __name__ == "__main__":
    build()
