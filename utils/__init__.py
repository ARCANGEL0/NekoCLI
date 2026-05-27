# coded by:
# ┏━┃┏━┃┏━┛┏━┃┏━ ┏━┛┏━┛┃  ┏━┃
# ┏━┃┏┏┛┃  ┏━┃┃ ┃┃ ┃┏━┛┃  ┃ ┃
# ┛ ┛┛ ┛━━┛┛ ┛┛ ┛━━┛━━┛━━┛━━┛
#------------------------------------------

import sys
import re
import shutil
import subprocess
from textwrap import wrap
from colorama import Fore, Style, init
from utils.spinner import spinner_start, spinner_stop

init(autoreset=True)

try:
    import unicodeit as _unicodeit
    _HAS_UNICODEIT = True
except ImportError:
    _HAS_UNICODEIT = False

_SYMBOLS = {
    r'\to': '→', r'\rightarrow': '→', r'\leftarrow': '←', r'\leftrightarrow': '↔',
    r'\Rightarrow': '⇒', r'\Leftarrow': '⇐', r'\Leftrightarrow': '⟺',
    r'\uparrow': '↑', r'\downarrow': '↓', r'\nearrow': '↗', r'\searrow': '↘',
    r'\infty': '∞', r'\partial': '∂', r'\nabla': '∇', r'\hbar': 'ℏ', r'\ell': 'ℓ',
    r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ', r'\delta': 'δ',
    r'\epsilon': 'ε', r'\varepsilon': 'ε', r'\zeta': 'ζ', r'\eta': 'η',
    r'\theta': 'θ', r'\vartheta': 'θ', r'\iota': 'ι', r'\kappa': 'κ',
    r'\lambda': 'λ', r'\mu': 'μ', r'\nu': 'ν', r'\xi': 'ξ',
    r'\pi': 'π', r'\varpi': 'π', r'\rho': 'ρ', r'\varrho': 'ρ',
    r'\sigma': 'σ', r'\varsigma': 'ς', r'\tau': 'τ', r'\upsilon': 'υ',
    r'\phi': 'φ', r'\varphi': 'φ', r'\chi': 'χ', r'\psi': 'ψ', r'\omega': 'ω',
    r'\Gamma': 'Γ', r'\Delta': 'Δ', r'\Theta': 'Θ', r'\Lambda': 'Λ',
    r'\Xi': 'Ξ', r'\Pi': 'Π', r'\Sigma': 'Σ', r'\Upsilon': 'Υ',
    r'\Phi': 'Φ', r'\Psi': 'Ψ', r'\Omega': 'Ω',
    r'\pm': '±', r'\mp': '∓', r'\times': '×', r'\div': '÷',
    r'\cdot': '·', r'\circ': '∘', r'\bullet': '•',
    r'\leq': '≤', r'\le': '≤', r'\geq': '≥', r'\ge': '≥',
    r'\neq': '≠', r'\ne': '≠', r'\approx': '≈', r'\equiv': '≡',
    r'\sim': '∼', r'\simeq': '≃', r'\cong': '≅', r'\propto': '∝',
    r'\forall': '∀', r'\exists': '∃', r'\nexists': '∄',
    r'\in': '∈', r'\notin': '∉', r'\ni': '∋',
    r'\subset': '⊂', r'\supset': '⊃', r'\subseteq': '⊆', r'\supseteq': '⊇',
    r'\cup': '∪', r'\cap': '∩', r'\emptyset': '∅', r'\varnothing': '∅',
    r'\int': '∫', r'\iint': '∬', r'\iiint': '∭', r'\oint': '∮',
    r'\sum': '∑', r'\prod': '∏', r'\coprod': '∐',
    r'\ldots': '…', r'\cdots': '⋯', r'\vdots': '⋮', r'\ddots': '⋱',
    r'\land': '∧', r'\lor': '∨', r'\lnot': '¬', r'\neg': '¬',
    r'\mid': '|', r'\nmid': '∤', r'\perp': '⊥', r'\parallel': '∥',
    r'\angle': '∠', r'\triangle': '△', r'\therefore': '∴', r'\because': '∵',
    r'\Re': 'ℜ', r'\Im': 'ℑ', r'\aleph': 'ℵ',
    r'\oplus': '⊕', r'\otimes': '⊗', r'\odot': '⊙',
    r'\langle': '⟨', r'\rangle': '⟩', r'\lfloor': '⌊', r'\rfloor': '⌋',
    r'\lceil': '⌈', r'\rceil': '⌉',
    r'\quad': '  ', r'\qquad': '    ', r'\,': ' ', r'\;': ' ', r'\ ': ' ',
}

_MATHBB = {'R':'ℝ','N':'ℕ','Z':'ℤ','Q':'ℚ','C':'ℂ','P':'ℙ','F':'𝔽','H':'ℍ'}

_MATH_RE = re.compile(
    r'\\(?:frac|sqrt|lim|int|sum|prod|to|infty|alpha|beta|gamma|delta|'
    r'epsilon|theta|lambda|mu|nu|pi|sigma|tau|phi|psi|omega|partial|nabla|'
    r'times|pm|leq|geq|neq|approx|equiv|in|forall|exists|begin|end|'
    r'mathbb|text|[a-zA-Z]+)|_\{|\^\{'
)

_CODE_LANGS = {
    'python','py','bash','sh','javascript','js','typescript','ts',
    'java','c','cpp','rust','go','ruby','php','sql','html','css',
    'json','yaml','toml','xml','dockerfile','makefile','r','julia',
}

_SUB_CHARS = {
    '0':'₀','1':'₁','2':'₂','3':'₃','4':'₄','5':'₅','6':'₆','7':'₇','8':'₈','9':'₉',
    '+':'₊','-':'₋','=':'₌','(':'₍',')':'₎',
    'a':'ₐ','e':'ₑ','h':'ₕ','i':'ᵢ','j':'ⱼ','k':'ₖ','l':'ₗ','m':'ₘ','n':'ₙ',
    'o':'ₒ','p':'ₚ','r':'ᵣ','s':'ₛ','t':'ₜ','u':'ᵤ','v':'ᵥ','x':'ₓ',
}
_SUP_CHARS = {
    '0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹',
    '+':'⁺','-':'⁻','=':'⁼','(':'⁽',')':'⁾',
    'a':'ᵃ','b':'ᵇ','c':'ᶜ','d':'ᵈ','e':'ᵉ','f':'ᶠ','g':'ᵍ','h':'ʰ','i':'ⁱ','j':'ʲ',
    'k':'ᵏ','l':'ˡ','m':'ᵐ','n':'ⁿ','o':'ᵒ','p':'ᵖ','r':'ʳ','s':'ˢ','t':'ᵗ','u':'ᵘ',
    'v':'ᵛ','w':'ʷ','x':'ˣ','y':'ʸ','z':'ᶻ',
}


def _tr(s, table):
    return ''.join(table.get(c, c) for c in s)


def _apply_symbols(text):
    text = re.sub(r'\\mathbb\{([A-Z])\}', lambda m: _MATHBB.get(m.group(1), m.group(1)), text)
    text = re.sub(
        r'\\(?:hat|bar|tilde|vec|dot|ddot|overline|underline|widehat|widetilde|overrightarrow)\{([^}]*)\}',
        r'\1', text,
    )
    for cmd in sorted(_SYMBOLS, key=len, reverse=True):
        text = text.replace(cmd, _SYMBOLS[cmd])
    if _HAS_UNICODEIT:
        try:
            text = _unicodeit.replace(text)
        except Exception:
            pass
    return text


def _sub(m):
    content = _apply_symbols(m.group(1).strip('{}'))
    return _tr(content, _SUB_CHARS)


def _sup(m):
    content = _apply_symbols(m.group(1).strip('{}'))
    return _tr(content, _SUP_CHARS)


def _convert(text):
    text = re.sub(r'\\frac\{([^}]*)\}\{([^}]*)\}', r'(\1)/(\2)', text)
    text = re.sub(r'\\sqrt\{([^}]*)\}', r'√\1', text)
    text = re.sub(r'\\text\{([^}]*)\}', r'\1', text)
    text = re.sub(
        r'\\(lim|sin|cos|tan|cot|sec|csc|log|ln|exp|max|min|sup|inf|det|dim|gcd|ker|arg)(?![a-zA-Z])',
        lambda m: m.group(1), text,
    )
    text = re.sub(r'_(\{[^}]*\}|[a-zA-Z0-9])', _sub, text)
    text = re.sub(r'\^(\{[^}]*\}|[a-zA-Z0-9])', _sup, text)
    text = _apply_symbols(text)
    return text


def _process_headers(text):
    def fmt(m):
        level = len(m.group(1))
        content = m.group(2).strip()
        w = min(len(content) + 4, 58)
        if level == 1:
            return f"**{content.upper()}**\n{'═' * w}"
        elif level == 2:
            return f"**{content}**\n{'─' * w}"
        elif level == 3:
            return f"**{content}**"
        else:
            return f"***{content}***"
    return re.sub(r'^(#{1,6})\s+(.+)$', fmt, text, flags=re.MULTILINE)


def _preprocess_math(text):
    parts = re.split(r'(```[\s\S]*?```)', text)
    out = []
    for part in parts:
        if part.startswith('```'):
            raw = part[3:]
            if raw.endswith('```'):
                raw = raw[:-3]
            nl = raw.find('\n')
            if nl >= 0:
                lang = raw[:nl].strip().lower()
                content = raw[nl + 1:]
            else:
                lang = ''
                content = raw
            if lang not in _CODE_LANGS and _MATH_RE.search(content):
                out.append(_convert(content.strip()))
            else:
                out.append(part)
            continue

        part = _process_headers(part)
        part = re.sub(
            r'`([^`\n]+)`',
            lambda m: _convert(m.group(1)) if _MATH_RE.search(m.group(1)) else m.group(0),
            part,
        )
        part = re.sub(r'\$\$([^$]+?)\$\$', lambda m: _convert(m.group(1)), part, flags=re.DOTALL)
        part = re.sub(r'\$([^$\n]+?)\$', lambda m: _convert(m.group(1)), part)
        part = _convert(part)
        out.append(part)
    return ''.join(out)


def glow_print(text: str) -> None:
    processed = _preprocess_math(text)
    if shutil.which("glow"):
        try:
            subprocess.run(["glow", "--style", "light", "-"], input=processed, text=True)
            return
        except Exception:
            pass
    print(format_in_box_markdown(processed))


def format_in_box_markdown(text, width=80, color=Fore.RED):
    paragraphs = text.strip().split("\n")
    formatted_lines = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            formatted_lines.append("")
            continue
        wrapped = wrap(para, width=width-4)
        formatted_lines.extend(wrapped)

    max_len = max(len(line) for line in formatted_lines) if formatted_lines else 0
    top_border = f"{color}╭{'─' * (max_len + 2)}╮{Style.RESET_ALL}"
    bottom_border = f"{color}╰{'─' * (max_len + 2)}╯{Style.RESET_ALL}"
    box_lines = [top_border]
    for line in formatted_lines:
        box_lines.append(f"{color}│{Style.RESET_ALL} {line.ljust(max_len)} {color}│{Style.RESET_ALL}")
    box_lines.append(bottom_border)
    return "\n".join(box_lines)


SORRY_KEYWORDS = [
    "sorry", "apology", "apologies", "unfortunately",
    "i can't", "i cannot", "can't assist",
    "desculpa", "desculpe", "sinto muito", "lamento"
]

def is_apology(text):
    return any(k in text.lower() for k in SORRY_KEYWORDS)

def clean_shell_input(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    text = ansi_escape.sub('', text)
    text = "".join(char for char in text if char.isprintable() or char in "\n\r\t")
    return text.strip()
