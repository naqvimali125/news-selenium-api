import re
from collections import Counter

STOP = set("""a an the and or but if while of at by for with about against between into through during before after
above below to from up down in out on off over under again further then once here there when where why how all any
both each few more most other some such no nor not only own same so than too very can will just don should now is
are was were be been being have has had do does did this that these those it its he she they them his her their we
you your i me my our as also said says say would could may might one two""".split())


def summarize(text, title="", max_sentences=3, max_chars=700):
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 40]
    if not sentences:
        return (title or "No article text found")[:max_chars]
    words = re.findall(r"[a-zA-Z']+", text.lower())
    freq = Counter(w for w in words if w not in STOP and len(w) > 2)
    if not freq:
        return " ".join(sentences[:max_sentences])[:max_chars]
    top = max(freq.values())
    scores = []
    for i, s in enumerate(sentences):
        toks = [w for w in re.findall(r"[a-zA-Z']+", s.lower()) if w in freq]
        score = sum(freq[w] / top for w in toks) / (len(toks) + 5)
        if i < 3:
            score *= 1.3
        scores.append((score, i))
    best = sorted(sorted(scores, reverse=True)[:max_sentences], key=lambda x: x[1])
    summary = " ".join(sentences[i] for _, i in best)
    return summary[:max_chars]
