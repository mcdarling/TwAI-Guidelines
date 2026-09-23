#!/usr/bin/env python3
"""Generate the dictionary's LaTeX entries and Sphinx pages from its YAML data.

The YAML files in dictionary/ are the single source of truth. This script
checks them and writes:

  entries/<domain>.tex        LaTeX entries, \\input by twai-dictionary.tex
  docs/generated/*.md         MyST Markdown pages for the Sphinx site

Definition, note and alias text uses a small neutral markup that both outputs
understand: *emphasis*, “curly quotes”, and $inline math$.

Usage: python3 tools/build.py [latex|site|all]
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml
from pybtex.database import parse_file

ROOT = Path(__file__).resolve().parent.parent
DOMAINS = ['ai', 'ml', 'trustworthy']

# The organisation behind each source, by bibliography key prefix. Anything
# unmatched is academic literature.
BODIES = [
    ('nist-', 'NIST'),
    ('iso-', 'ISO/IEC'),
    ('eu-ai-act', 'EU AI Act'),
    ('hleg-', 'EU HLEG'),
    ('oecd-', 'OECD'),
    ('ieee-', 'IEEE'),
    ('unesco-', 'UNESCO'),
    ('coe-', 'Council of Europe'),
    ('owasp-', 'OWASP'),
]
ACADEMIC = 'Academic'


def body_of(key):
    for prefix, body in BODIES:
        if key.startswith(prefix):
            return body
    return ACADEMIC


def body_class(body):
    return 'body-' + re.sub(r'[^a-z]+', '-', body.lower()).strip('-')


# --- Loading and validation -------------------------------------------------

def load_sources():
    bib = parse_file(ROOT / 'references.bib', bib_format='bibtex')
    return {key: Source(key, entry) for key, entry in bib.entries.items()}


def unbrace(text):
    text = re.sub(r'[{}]', '', text).replace('---', '—').replace('--', '–')
    return text.replace('~', '\u00a0')


class Source:
    def __init__(self, key, entry):
        self.key = key
        self.type = entry.type
        self.fields = {k.lower(): unbrace(v) for k, v in entry.fields.items()}
        role = 'author' if 'author' in entry.persons else 'editor'
        self.people = [self._name(p) for p in entry.persons.get(role, [])]
        self.editors = role == 'editor'
        self.body = body_of(key)

    @staticmethod
    def _name(person):
        last = unbrace(' '.join(person.prelast_names + person.last_names))
        first = unbrace(' '.join(person.first_names + person.middle_names))
        return last, first

    @property
    def year(self):
        return self.fields.get('year') or self.fields.get('date', '')[:4]

    @property
    def label(self):
        """Short label, matching biblatex authoryear or the shorthand."""
        if 'shorthand' in self.fields:
            return self.fields['shorthand']
        lasts = [last for last, _ in self.people]
        if len(lasts) == 1:
            names = lasts[0]
        elif len(lasts) == 2 and lasts[1] != 'others':
            names = f'{lasts[0]} and {lasts[1]}'
        else:
            names = f'{lasts[0]} et al.'
        return f'{names} {self.year}'

    def reference(self):
        """Full reference as Markdown."""
        f = self.fields
        people = []
        for last, first in self.people:
            people.append('et al.' if last == 'others'
                          else (f'{last}, {first}' if first else last))
        who = '; '.join(people) + (' (eds.)' if self.editors else '')
        parts = [f'{who} ({self.year}).', f'*{f["title"]}*.']
        venue = (f.get('journal') or f.get('booktitle') or f.get('institution')
                 or f.get('publisher') or f.get('organization')
                 or f.get('howpublished'))
        if venue:
            extra = [venue]
            if f.get('number') and self.type != 'article':
                extra.append(f['number'])
            if f.get('volume'):
                extra.append(f'vol. {f["volume"]}')
            if f.get('howpublished') and f.get('howpublished') != venue:
                extra.append(f['howpublished'])
            parts.append(', '.join(extra) + '.')
        if f.get('eprint'):
            parts.append(f'[arXiv:{f["eprint"]}](https://arxiv.org/abs/{f["eprint"]})')
        if f.get('doi'):
            parts.append(f'[doi:{f["doi"]}](https://doi.org/{f["doi"]})')
        elif f.get('url'):
            parts.append(f'<{f["url"]}>')
        return ' '.join(parts)


def load_domains(sources):
    domains, errors, seen = [], [], {}
    for name in DOMAINS:
        data = yaml.safe_load((ROOT / f'dictionary/{name}.yaml').read_text())
        terms = data['terms']
        names = [t['term'].lower() for t in terms]
        if names != sorted(names):
            errors.append(f'{name}.yaml: terms are not in alphabetical order')
        for t in terms:
            if t['key'] in seen:
                errors.append(f'duplicate key {t["key"]!r}')
            seen[t['key']] = name
            if len(t['definitions']) < 2:
                errors.append(f'{t["key"]}: fewer than two definitions')
            for d in t['definitions']:
                if d['source'] not in sources:
                    errors.append(f'{t["key"]}: unknown source {d["source"]!r}')
        domains.append({'name': name, 'title': data['domain'], 'terms': terms})
    for dom in domains:
        for t in dom['terms']:
            for r in t.get('related', []):
                if r not in seen:
                    errors.append(f'{t["key"]}: related key {r!r} does not exist')
    if errors:
        sys.exit('dictionary data errors:\n  ' + '\n  '.join(errors))
    return domains, seen


# --- Markup conversion ------------------------------------------------------

MATH = re.compile(r'(\$[^$]+\$)')


def to_latex(text):
    out = []
    for part in MATH.split(text):
        if part.startswith('$'):
            out.append(part)
            continue
        part = re.sub(r'([&%#_])', r'\\\1', part)
        part = re.sub(r'\*([^*]+)\*', r'\\emph{\1}', part)
        while re.search(r'“[^“”]*”', part):
            part = re.sub(r'“([^“”]*)”', r'\\enquote{\1}', part)
        part = part.replace('—', '---').replace('\u00a0', '~')
        out.append(part)
    return ''.join(out)


def to_md(text):
    return text


# --- LaTeX output -----------------------------------------------------------

def write_latex(domains):
    (ROOT / 'entries').mkdir(exist_ok=True)
    for dom in domains:
        lines = [f'% Generated by tools/build.py from dictionary/{dom["name"]}.yaml.',
                 '% Do not edit: change the YAML and rebuild.',
                 f'\\domain{{{dom["title"]}}}', '']
        for t in dom['terms']:
            alias = f'[{to_latex(t["alias"])}]' if t.get('alias') else ''
            lines.append(f'\\begin{{entry}}{{{t["key"]}}}{{{t["term"]}}}{alias}')
            for d in t['definitions']:
                star = '*' if d.get('quote') else ''
                at = f'[{to_latex(d["at"])}]' if d.get('at') else ''
                lines.append(f'  \\defn{star}{at}{{{d["source"]}}}{{{to_latex(d["text"])}}}')
            if t.get('note'):
                lines.append(f'  \\note{{{to_latex(t["note"])}}}')
            if t.get('related'):
                lines.append(f'  \\related{{{",".join(t["related"])}}}')
            lines += ['\\end{entry}', '']
        (ROOT / f'entries/{dom["name"]}.tex').write_text('\n'.join(lines))


# --- Sphinx output ----------------------------------------------------------

def term_ref(t):
    return f'{{ref}}`{t["term"]} <term-{t["key"]}>`'


def write_site(domains, sources, domain_of):
    out = ROOT / 'docs/generated'
    out.mkdir(parents=True, exist_ok=True)
    by_key = {t['key']: t for dom in domains for t in dom['terms']}
    cited_by = defaultdict(list)

    for dom in domains:
        lines = [f'# {dom["title"]}', '']
        for t in dom['terms']:
            lines += [f'(term-{t["key"]})=', f'## {t["term"]}', '']
            if t.get('alias'):
                lines += ['{.term-alias}', f'Also: {to_md(t["alias"])}', '']
            lines.append('{.defs}')
            for i, d in enumerate(t['definitions'], 1):
                src = sources[d['source']]
                cited_by[src.key].append(t)
                text = to_md(d['text'])
                if d.get('quote'):
                    text = f'“{text}”'
                where = f', {d["at"]}' if d.get('at') else ''
                kind = ('[quoted]{.kind .kind-quoted}' if d.get('quote')
                        else '[adapted]{.kind}')
                lines.append(
                    f'{i}. {text} '
                    f'[{{ref}}`{src.label} <src-{src.key}>`{where}]'
                    f'{{.src .{body_class(src.body)}}} {kind}')
            lines.append('')
            if t.get('note'):
                lines += [':::{admonition} How these definitions differ',
                          ':class: note', to_md(t['note']), ':::', '']
            if t.get('related'):
                links = ' · '.join(term_ref(by_key[r]) for r in t['related'])
                lines += ['{.see-also}', f'See also: {links}', '']
        (out / f'{dom["name"]}.md').write_text('\n'.join(lines))

    # A–Z list of every term.
    everything = sorted(by_key.values(), key=lambda t: t['term'].lower())
    titles = {dom['name']: dom['title'] for dom in domains}
    lines = ['# All Terms A–Z', '']
    letter = None
    for t in everything:
        if t['term'][0].upper() != letter:
            letter = t['term'][0].upper()
            lines += ['', f'## {letter}', '']
        dom = domain_of[t['key']]
        alias = f' ({t["alias"]})' if t.get('alias') else ''
        lines.append(f'- {term_ref(t)}{alias} '
                     f'[{titles[dom]}]{{.chip .chip-{dom}}}')
    (out / 'a-z.md').write_text('\n'.join(lines) + '\n')

    # Which organisations define which terms.
    bodies = [b for _, b in BODIES if b != 'OWASP'] + ['OWASP', ACADEMIC]
    used = {sources[d['source']].body for t in everything for d in t['definitions']}
    bodies = [b for b in bodies if b in used]
    lines = ['# Coverage by Source', '',
             'Which organisations’ definitions each term includes. '
             'The number is how many definitions come from that organisation.', '']
    for dom in domains:
        lines += [f'## {dom["title"]}', '',
                  '| Term | ' + ' | '.join(bodies) + ' |',
                  '|---|' + '---|' * len(bodies)]
        for t in dom['terms']:
            counts = defaultdict(int)
            for d in t['definitions']:
                counts[sources[d['source']].body] += 1
            cells = [str(counts[b]) if counts[b] else '' for b in bodies]
            lines.append(f'| {term_ref(t)} | ' + ' | '.join(cells) + ' |')
        lines.append('')
    (out / 'coverage.md').write_text('\n'.join(lines))

    # Sources, with the terms that cite each one.
    groups = [('Standards, Regulation, and Policy',
               [s for s in sources.values() if s.body != ACADEMIC]),
              ('Books and Papers',
               [s for s in sources.values() if s.body == ACADEMIC])]
    lines = ['# Sources', '']
    for title, group in groups:
        lines += [f'## {title}', '']
        for s in sorted(group, key=lambda s: s.label.lower()):
            if not cited_by[s.key]:
                continue
            terms = sorted({t['key']: t for t in cited_by[s.key]}.values(),
                           key=lambda t: t['term'].lower())
            lines += [f'(src-{s.key})=',
                      f'**{s.label}** — {s.reference()}',
                      '',
                      '{.cited-by}',
                      'Cited in: ' + ' · '.join(term_ref(t) for t in terms),
                      '']
    (out / 'sources.md').write_text('\n'.join(lines))


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else 'all'
    sources = load_sources()
    domains, domain_of = load_domains(sources)
    if target in ('latex', 'all'):
        write_latex(domains)
    if target in ('site', 'all'):
        write_site(domains, sources, domain_of)
    n = sum(len(d['terms']) for d in domains)
    print(f'{n} terms from {len(domains)} domains -> {target}')


if __name__ == '__main__':
    main()
