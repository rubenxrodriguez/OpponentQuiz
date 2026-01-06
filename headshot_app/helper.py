import re
import unicodedata
from difflib import SequenceMatcher

# -----------------------------
# Text normalization
# -----------------------------
def norm_text(s: str) -> str:
    if s is None:
        return ""
    s = str(s).strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-z0-9\s]", " ", s)   # keep letters/numbers/spaces
    s = re.sub(r"\s+", " ", s).strip()
    return s

def token_sort(s: str) -> str:
    toks = norm_text(s).split()
    toks.sort()
    return " ".join(toks)

def fuzzy_ratio(a: str, b: str) -> float:
    a2, b2 = token_sort(a), token_sort(b)
    if not a2 or not b2:
        return 0.0
    return SequenceMatcher(None, a2, b2).ratio()

def close_enough(a: str, b: str, threshold: float = 0.86) -> bool:
    # 0.86 is a good “strict but forgiving” default for names
    return fuzzy_ratio(a, b) >= threshold


# -----------------------------
# YEAR normalization
# -----------------------------
YEAR_MAP = {
    "fr": "fr", "freshman": "fr",
    "so": "so", "sophomore": "so",
    "jr": "jr", "junior": "jr",
    "sr": "sr", "senior": "sr",
    "gr": "gr", "grad": "gr", "graduate": "gr",
}
def norm_year(s: str) -> str:
    """
    Keeps redshirt tag if present: r-fr, r-so, r-jr, r-sr
    Converts common text variants.
    """
    t = norm_text(s)
    t = t.replace("redshirt", "r").replace("rs", "r").replace("r s", "r")
    t = t.replace(" ", "")
    # examples: "rfr" -> "r-fr", "r-fr" stays, "fr." -> "fr"
    t = t.replace(".", "")
    if t.startswith("r") and len(t) >= 3:
        base = t[1:]
        base = YEAR_MAP.get(base, base)
        return f"r-{base}"
    return YEAR_MAP.get(t, t)

def year_match(user: str, truth: str) -> bool:
    return norm_year(user) == norm_year(truth)


# -----------------------------
# Hometown / location logic
# -----------------------------
US_STATE_CODES = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
    "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
    "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
    "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC"
}

# add common aliases seen in rosters
STATE_ALIASES = {
    "wash": "WA", "washington": "WA", "wash.": "WA",
    "mont": "MT", "montana": "MT", "mont.": "MT",
    "calif": "CA", "california": "CA", "calif.": "CA",
    "nev": "NV", "nevada": "NV",
    "ore": "OR", "oregon": "OR", "ore.": "OR",
    "idaho": "ID",
    "utah": "UT",
    "ariz": "AZ", "arizona": "AZ",
    "texas": "TX",
    "ill": "IL", "illinois": "IL",
    # add more as you run into them
}

STATE_CODE_TO_NAME = {
    "AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California","CO":"Colorado",
    "CT":"Connecticut","DE":"Delaware","FL":"Florida","GA":"Georgia","HI":"Hawaii","ID":"Idaho",
    "IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana",
    "ME":"Maine","MD":"Maryland","MA":"Massachusetts","MI":"Michigan","MN":"Minnesota",
    "MS":"Mississippi","MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada","NH":"New Hampshire",
    "NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina","ND":"North Dakota",
    "OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island","SC":"South Carolina",
    "SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia",
    "WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming","DC":"District of Columbia"
}

def extract_state_code(hometown: str) -> str:
    """
    For US hometowns that look like:
      "Seattle, WA" or "Seattle, Wash." or "Seattle, Washington"
    returns the 2-letter code if recognized, else "".
    """
    if not hometown:
        return ""
    s = str(hometown).strip()
    parts = [p.strip() for p in s.split(",") if p.strip()]
    if len(parts) < 2:
        return ""
    last = parts[-1]
    last_norm = norm_text(last).replace(" ", "")
    last_up = last.strip().upper().replace(".", "")
    if last_up in US_STATE_CODES:
        return last_up
    # alias mapping (wash -> WA)
    last_norm_spaced = norm_text(last)  # keep words
    if last_norm_spaced in STATE_ALIASES:
        return STATE_ALIASES[last_norm_spaced]
    return ""

def extract_country(hometown: str) -> str:
    """
    For international hometowns often like:
      "Madrid, Spain" or "Stockholm, Sweden"
    returns last comma chunk as 'country' (normalized).
    """
    if not hometown:
        return ""
    s = str(hometown).strip()
    parts = [p.strip() for p in s.split(",") if p.strip()]
    if len(parts) >= 2:
        return norm_text(parts[-1])
    # if no comma, treat whole thing as "country-ish"
    return norm_text(s)

def classify_national_or_intl(hometown: str) -> str:
    """
    Return: 'national', 'international', 'unknown'
    National = US state code/alias recognized in last token.
    """
    if hometown is None:
        return "unknown"
    s = str(hometown).strip()
    if not s:
        return "unknown"
    return "national" if extract_state_code(s) else "international"
def hometown_match(user_answer: str, truth_hometown: str) -> bool:
    ua = norm_text(user_answer)
    ua_clean = ua.replace(" ", "").upper()   # ✅ DEFINE ONCE

    th = str(truth_hometown or "").strip()
    if not th:
        return ua in {"", "unknown", "na", "n a"}

    cls = classify_national_or_intl(th)

    # Always allow fuzzy full-string match
    if close_enough(user_answer, th, threshold=0.80):
        return True

    if cls == "national":
        true_state = extract_state_code(th)
        if not true_state:
            return False

        full_state = STATE_CODE_TO_NAME.get(true_state, "").upper()

        # exact state code: CO
        if ua_clean == true_state:
            return True

        # full state name: Colorado
        if ua_clean == full_state.replace(" ", ""):
            return True

        # appears anywhere: "Aurora CO", "Colorado Springs"
        if true_state in ua_clean or full_state in ua_clean:
            return True

        return False

    if cls == "international":
        true_country = extract_country(th)
        if not true_country:
            return False

        true_country = true_country.replace(" ", "")

        # accept country-only answers
        if ua_clean == true_country.upper():
            return True

        if true_country.upper() in ua_clean:
            return True

        return False

    return False


# -----------------------------
# Previous school matching
# -----------------------------
def prev_school_match(user_answer: str, truth_prev: str) -> bool:
    ua = norm_text(user_answer)
    tp = norm_text(truth_prev)

    if not tp:
        return ua in {"", "none", "na", "n a", "n/a", "no", "nil"}
    # allow “close enough” because of abbreviations (CC, Univ, State, etc.)
    return close_enough(user_answer, truth_prev, threshold=0.80)
