from pathlib import Path
import re
import shutil
import zipfile

base = Path('/opt/data/workspace/matematyka/teach-statystyka')
lessons_dir = base / 'lessons'
ref_dir = base / 'reference'
lessons_dir.mkdir(parents=True, exist_ok=True)
ref_dir.mkdir(parents=True, exist_ok=True)

CSS = '''
:root{--bg:#f7f3ea;--paper:#fffaf1;--ink:#1e293b;--muted:#64748b;--line:#e2d6c3;--accent:#7c2d12;--accent2:#1d4ed8;--green:#166534;--yellow:#854d0e;--red:#991b1b;--shadow:0 8px 30px rgba(30,41,59,.08)}
*{box-sizing:border-box}body{margin:0;background:linear-gradient(180deg,#f8f2e6 0,#f7f3ea 38%,#f5efe4 100%);color:var(--ink);font:17px/1.68 ui-serif,Georgia,Cambria,"Times New Roman",serif}main{max-width:980px;margin:0 auto;padding:34px 18px 72px}.shell{background:rgba(255,250,241,.96);border:1px solid var(--line);border-radius:22px;box-shadow:var(--shadow);overflow:hidden}.hero{padding:34px 30px 22px;border-bottom:1px solid var(--line);background:radial-gradient(circle at top right,#fde68a55,transparent 38%),#fffaf1}article{padding:28px 30px 38px}h1,h2,h3{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;line-height:1.16;letter-spacing:-.02em}h1{font-size:clamp(2rem,5vw,3.2rem);margin:.2rem 0 .4rem}h2{font-size:1.45rem;margin:2rem 0 .7rem}h3{font-size:1.08rem;margin:1.35rem 0 .45rem}.eyebrow{display:inline-block;font:700 .78rem/1 ui-sans-serif,system-ui;letter-spacing:.08em;text-transform:uppercase;color:#9a3412;background:#ffedd5;border:1px solid #fed7aa;border-radius:999px;padding:.38rem .65rem}.lead{font-size:1.12rem;color:#475569;max-width:70ch}.muted{color:var(--muted)}a{color:var(--accent2);text-decoration:none}a:hover{text-decoration:underline}.nav{display:flex;flex-wrap:wrap;gap:.55rem;margin-top:1.1rem}.nav a{font-family:ui-sans-serif,system-ui;border:1px solid var(--line);background:#fff;border-radius:999px;padding:.45rem .72rem;color:#334155;text-decoration:none;font-size:.9rem}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:14px}.card,.box,.example,.scheme,.pitfall,.exercise,.source{border:1px solid var(--line);border-radius:16px;background:#fffdf8;padding:16px 18px;margin:14px 0}.card{margin:0}.scheme{border-left:5px solid var(--accent2)}.example{border-left:5px solid var(--green)}.pitfall{border-left:5px solid var(--red);background:#fff7f7}.exercise{border-left:5px solid var(--yellow);background:#fffbeb}.source{background:#f8fafc}.formula{display:block;white-space:pre-wrap;overflow-x:auto;background:#0f172a;color:#f8fafc;border-radius:13px;padding:13px 15px;font:15px/1.55 ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}.small{font-size:.92rem}.tag{display:inline-block;background:#e0f2fe;color:#075985;border-radius:999px;padding:.15rem .5rem;font:700 .78rem/1.4 ui-sans-serif,system-ui;margin-right:.25rem}ul,ol{padding-left:1.35rem}li{margin:.35rem 0}.two{display:grid;grid-template-columns:1fr 1fr;gap:14px}@media(max-width:760px){body{font-size:16px}main{padding:12px 8px 44px}.hero,article{padding:22px 16px}.two{grid-template-columns:1fr}.shell{border-radius:16px}.nav a{font-size:.82rem}}@media print{body{background:#fff}.shell{box-shadow:none;border:none}.nav{display:none}main{max-width:none;padding:0}.hero,article{padding:20px}}
'''

lessons = [
{
'slug':'0001-lista-6-estymacja-parametryczna.html','list':'Lista 6','title':'Estymacja parametryczna: momenty, kwantyle, plug-in, MLE',
'source':'Notatki: Estymacja parametryczna — metoda momentów, metoda kwantyli, plug-in, MLE.',
'goal':'Rozpoznać metodę estymacji i przeprowadzić rachunek bez gubienia sensu.',
'body':'''<h2>Mapa decyzyjna</h2><div class="scheme"><b>Najpierw rozpoznaj typ zadania.</b><ol><li>Masz momenty teoretyczne? Użyj metody momentów.</li><li>Pojawia się mediana, kwartyl albo procent? Użyj metody kwantyli.</li><li>Parametr jest funkcjonałem dystrybuanty, np. E φ(X)? Użyj plug-in.</li><li>Masz gęstość lub pmf i polecenie „wyznacz MLE”? Pisz funkcję wiarygodności.</li></ol></div>
<h2>Metoda momentów</h2><p>Jeżeli parametr θ ma k składowych, bierzesz k momentów teoretycznych i przyrównujesz je do momentów z próby.</p><pre class="formula">m_j(θ) = E_θ X^j
m̂_j = (1/n) Σ X_i^j
Rozwiąż: m_1(θ)=m̂_1, …, m_k(θ)=m̂_k</pre><div class="example"><b>Przykład z notatek: N(μ,σ²).</b><br>m₁=μ, m₂=σ²+μ². Dostajesz μ̂=X̄ oraz σ̂²=(1/n)Σ(Xᵢ−X̄)². To nie jest klasyczne nieobciążone S² z mianownikiem n−1.</div>
<h2>Metoda kwantyli</h2><p>Jeżeli parametr da się zapisać przez kwantyle rozkładu, zamień kwantyl teoretyczny na próbkowy.</p><pre class="formula">x_p = F_θ^{-1}(p)
θ = g(x_{p1},…,x_{ps})
θ̂ = g(x̂_{p1},…,x̂_{ps})</pre><div class="example"><b>Wykładniczy Exp(λ) z notatek.</b><br>Fλ(x)=1−e^{−λx}. Z równania Fλ(xp)=p: λ=−ln(1−p)/xp, więc λ̂=−ln(1−p)/x̂p.</div>
<h2>Plug-in</h2><pre class="formula">θ = T(F)  →  θ̂ = T(F̂_n)
Jeśli θ=∫φ(x)dF(x), to θ̂=(1/n)Σφ(X_i)</pre>
<h2>MLE</h2><div class="scheme"><ol><li>Napisz l(θ)=Π f(xᵢ;θ).</li><li>Przejdź do L(θ)=ln l(θ).</li><li>Rozwiąż L′(θ)=0.</li><li>Sprawdź maksimum i brzegi nośnika.</li></ol></div><div class="example"><b>Poisson(λ) z notatek.</b><pre class="formula">l(λ)=C·λ^{Σx_i}e^{-nλ}
L(λ)=const+(Σx_i)lnλ−nλ
L′(λ)=Σx_i/λ−n=0
λ̂=X̄</pre></div><div class="pitfall"><b>Pułapka:</b> MLE nie zawsze jest jednoznaczny. Dla U(θ−1/2,θ+1/2) z notatek cały przedział może maksymalizować wiarygodność.</div>
<h2>Ćwiczenia do listy 6</h2><div class="exercise"><ol><li>Wyprowadź metodą momentów μ̂ i σ̂² dla normalnego.</li><li>Wyprowadź MLE λ̂=X̄ dla Poissona.</li><li>Spróbuj zbudować estymator z mediany dla dowolnego rozkładu z Fθ.</li></ol></div>'''
},
{
'slug':'0002-lista-7-jakosc-estymatorow.html','list':'Lista 7','title':'Jakość estymatorów: zgodność, obciążenie, ryzyko, Cramer–Rao',
'source':'Notatki: Ocena jakości estymatorów, narzędzia asymptotyczne, nierówność Cramera-Rao, ciągi estymatorów.',
'goal':'Umieć powiedzieć nie tylko „to jest estymator”, ale czy jest dobry i w jakim sensie.',
'body':'''<h2>Trzy pytania o estymator</h2><div class="scheme"><ol><li><b>Czy trafia średnio?</b> Nieobciążoność: EθT=g(θ).</li><li><b>Czy zbiega przy dużej próbie?</b> Zgodność: Tn→g(θ) w prawdopodobieństwie.</li><li><b>Ile kosztuje błąd?</b> Ryzyko: R(T,θ)=EθL(T,θ), zwykle MSE.</li></ol></div>
<h2>Obciążenie i MSE</h2><pre class="formula">b(θ)=Eθ[T]−g(θ)
MSE(T)=Eθ[(T−g(θ))²]=Varθ(T)+b(θ)²</pre><p>Estymator może być obciążony, ale mieć mniejsze MSE, jeśli znacząco zmniejsza wariancję.</p><div class="example"><b>Przykład z notatek: estymacja p w Bin(n,p).</b><br>d₁=X/n ma ryzyko p(1−p)/n. Estymator d₂=(X+½√n)/(n+√n) ma ryzyko 1/[4(√n+1)²]. Nieobciążoność nie oznacza automatycznie najlepszego ryzyka.</div>
<h2>Zgodność i tempo</h2><pre class="formula">T_n zgodny ⇔ dla każdego ε&gt;0:
Pθ(|T_n−θ|≥ε)→0</pre><p>Średnia próbkowa jest mocno zgodna z MPWL. Tempo √n zwykle bierze się z CTG.</p>
<h2>Slutsky i metoda delta</h2><pre class="formula">Jeśli a_n(X_n−c) ⇒ V oraz g′(c)≠0,
to a_n(g(X_n)−g(c)) ⇒ g′(c)V.</pre><p>Używaj, gdy znasz graniczny rozkład Tn, ale zadanie pyta o funkcję g(Tn).</p>
<h2>Cramer–Rao</h2><pre class="formula">Varθ[T(X)] ≥ [g′(θ)]² / I(θ)
I(θ)=Eθ[(∂/∂θ ln f(X;θ))²]
Dla próby iid: I_n(θ)=nI_1(θ)</pre><div class="example"><b>Bernoulli z notatek.</b><br>Dla Xᵢ~B(1,p), X̄ jest efektywnym estymatorem p, bo pochodna log-wiarygodności jest proporcjonalna do X̄−p.</div>
<h2>Ćwiczenia do listy 7</h2><div class="exercise"><ol><li>Dla danego T policz E[T], Var(T), MSE.</li><li>Sprawdź, czy estymator jest asymptotycznie nieobciążony.</li><li>Policz informację Fishera i porównaj z wariancją estymatora.</li></ol><p><b>Typowy błąd:</b> mylenie zgodności z nieobciążonością.</p></div>'''
},
{
'slug':'0003-lista-8-redukcja-umvue.html','list':'Lista 8','title':'Redukcja statystyk: dostateczność, minimalność, zupełność, UMVUE',
'source':'Notatki: Redukcja statystyk, Rao-Blackwell, statystyka swobodna, estymatory UMVUE.',
'goal':'Skompresować próbę do statystyki i użyć tej statystyki do ulepszania estymatorów.',
'body':'''<h2>Intuicja</h2><p>Dostateczność: po poznaniu T(X), reszta próby nie wnosi informacji o parametrze. Minimalność: T jest najprostszą taką kompresją. Zupełność: nie ma niezerowej funkcji g(T) o średniej zero dla wszystkich parametrów.</p>
<h2>Faktoryzacja</h2><div class="scheme"><pre class="formula">f(x;θ)=g_θ(T(x))·h(x)</pre>Jeśli cała zależność od θ przechodzi przez T(x), to T jest dostateczna.</div><div class="example"><b>Bernoulli z notatek.</b><br>Dla X₁,…,Xₙ~B(1,p), prawdopodobieństwo próby zależy od p przez ΣXᵢ, więc T=ΣXᵢ jest dostateczna.</div>
<h2>Minimalność</h2><ol><li>W pełnej rodzinie wykładniczej naturalna statystyka jest minimalnie dostateczna.</li><li>Kryterium ilorazu: jeśli f(x;θ)/f(y;θ) nie zależy od θ, powinno wynikać T(x)=T(y).</li></ol><div class="example">Dla U(0,θ) z notatek dostateczna jest największa obserwacja X(n), bo nośnik wymusza X(n)≤θ.</div>
<h2>Zupełność</h2><pre class="formula">T zupełna ⇔ Eθ[g(T)]=0 dla każdego θ
implikuje Pθ(g(T)=0)=1 dla każdego θ.</pre><p>Dla T=ΣXᵢ~Bin(n,p), warunek Epg(T)=0 daje wielomian równy zero dla wszystkich p, więc współczynniki muszą być zerowe.</p>
<h2>Rao–Blackwell i Lehmann–Scheffé</h2><div class="scheme"><b>Algorytm UMVUE:</b><ol><li>Znajdź T — dostateczną i zupełną.</li><li>Znajdź dowolny nieobciążony estymator W funkcji g(θ).</li><li>Policz φ(T)=E[W|T].</li><li>Z Lehmann–Scheffé: φ(T) jest UMVUE.</li></ol></div><div class="example">Z notatek: dla Poissona i g(λ)=P(X₁=3), weź W=1{X₁=3}, T=ΣXᵢ i policz P(X₁=3|T=t).</div>
<h2>Basu</h2><p>Jeśli T jest dostateczna i zupełna, a V jest statystyką swobodną, to T i V są niezależne.</p>
<h2>Ćwiczenia do listy 8</h2><div class="exercise"><ol><li>Najpierw spróbuj faktoryzacji.</li><li>Potem sprawdź, czy to rodzina wykładnicza pełnego rzędu.</li><li>Jeśli pytają o UMVUE, zacznij od T i W, nie od wariancji.</li></ol></div>'''
},
{
'slug':'0004-lista-9-przedzialy-ufnosci.html','list':'Lista 9','title':'Przedziały ufności: funkcje centralne i odwracanie nierówności',
'source':'Notatki: Estymacja przedziałowa, funkcje centralne, najkrótsze przedziały ufności.',
'goal':'Znaleźć funkcję centralną i zamienić zdarzenie probabilistyczne w przedział dla parametru.',
'body':'''<h2>Znaczenie</h2><p>Parametr θ jest stały. Losowy jest przedział [L(X),U(X)]. Procedura ma pokrycie co najmniej 1−α.</p><pre class="formula">Pθ(θ∈[L(X),U(X)]) ≥ 1−α</pre>
<h2>Funkcja centralna</h2><div class="scheme"><b>Q(X;θ)</b> zależy od próby i parametru, ale jej rozkład nie zależy od θ.</div><pre class="formula">1. Wybierz a,b: P(a≤Q(X;θ)≤b)≥1−α.
2. Rozwiąż a≤Q(X;θ)≤b względem θ.
3. Odczytaj [L(X),U(X)].</pre>
<h2>Normalny: σ znana</h2><div class="example"><pre class="formula">X_i~N(μ,σ²), σ znana
Q=√n(X̄−μ)/σ ~ N(0,1)
μ∈[X̄−σz_{α/2}/√n, X̄+σz_{α/2}/√n]</pre></div>
<h2>Normalny: σ nieznana</h2><div class="example"><pre class="formula">Q=√n(X̄−μ)/S ~ t_{n−1}
μ∈[X̄−S t_{n−1,α/2}/√n,
   X̄+S t_{n−1,α/2}/√n]</pre></div>
<h2>Najkrótsze przedziały</h2><p>Jeśli gęstość funkcji centralnej jest unimodalna, przedział o masie 1−α można dobrać tak, by miał minimalną długość. „Najkrótszy” nie zawsze znaczy symetryczny.</p>
<h2>Ćwiczenia do listy 9</h2><div class="exercise"><ol><li>Podkreśl parametr.</li><li>Wypisz kandydatów na Q: normalny, t, χ², transformacja monotoniczna.</li><li>Po odwróceniu nierówności sprawdź kierunek znaków.</li></ol></div>'''
},
{
'slug':'0005-lista-10-testy-hipotez.html','list':'Lista 10','title':'Testowanie hipotez: Neyman–Pearson, MLR, UMP, LR, p-value',
'source':'Notatki: Testowanie hipotez, MLR/UMP, p-value, hipotezy dwustronne, testy nieobciążone, LR.',
'goal':'Przejść od hipotez do obszaru krytycznego i dobrać próg dający rozmiar α.',
'body':'''<h2>Słownik</h2><ul><li>φ(x) — test; dla niezrandomizowanego φ∈{0,1}.</li><li>Zbiór krytyczny — tam, gdzie φ(x)=1.</li><li>Moc: βφ(θ)=Eθφ(X).</li><li>Rozmiar: sup po θ z H₀ z funkcji mocy.</li></ul>
<h2>Neyman–Pearson</h2><div class="scheme"><b>Dla prostych hipotez H₀:f₀ vs H₁:f₁:</b><pre class="formula">odrzucaj H₀, gdy f₁(x) > c f₀(x)</pre>Stałą c dobierasz tak, żeby E₀φ=α.</div>
<h2>MLR i Karlin–Rubin</h2><pre class="formula">H₀: θ≤θ₀ vs H₁: θ&gt;θ₀
φ*(x)=1 gdy T(x)&gt;c,
φ*(x)=γ gdy T(x)=c,
φ*(x)=0 gdy T(x)&lt;c.
Dobierz c,γ z β(θ₀)=α.</pre><div class="example"><b>Normalny z notatek.</b><br>Dla Xᵢ~N(μ,σ²), σ² znana, H₀:μ≤μ₀ vs H₁:μ&gt;μ₀, odrzucasz dla dużego X̄. Próg: cα=μ₀+zασ/√n.</div><div class="example"><b>Bernoulli z notatek.</b><br>Dla H₀:p≤p₀ vs H₁:p&gt;p₀ odrzucasz dla dużej sumy T=ΣXᵢ. W dyskretnym przypadku może pojawić się randomizacja γ.</div>
<h2>p-value</h2><pre class="formula">p-value = inf { α : x∈B_α }
Dla B_α={T(x)&gt;c_α}:
p-value = sup_{θ∈H₀} Pθ(T(X)≥T(x_obs))</pre>
<h2>Dwustronność i UMPU</h2><p>Dla H₀:θ=θ₀ vs θ≠θ₀ test UMP zwykle nie istnieje. W jednoparametrowych rodzinach wykładniczych szuka się wtedy UMPU, czyli najlepszego testu wśród nieobciążonych.</p>
<h2>Test LR</h2><div class="scheme"><pre class="formula">λ(x)= sup_{θ∈Θ₀} l(θ) / sup_{θ∈Θ} l(θ)
Odrzucaj H₀, gdy λ(x)&lt;c.</pre>Małe λ oznacza: najlepsze dopasowanie pod H₀ jest dużo gorsze od najlepszego dopasowania ogólnie.</div><div class="example"><b>Normalny z notatek.</b><br>Dla Xᵢ~N(θ,1), H₀:θ=θ₀ vs H₁:θ≠θ₀, λ(x)=exp[−n(X̄−θ₀)²/2], więc odrzucasz dla dużego |X̄−θ₀|.</div>
<h2>Ćwiczenia do listy 10</h2><div class="exercise"><ol><li>Zapisz H₀ i H₁. Czy są proste, jednostronne, dwustronne?</li><li>Sprawdź MLR względem T.</li><li>Ustal kierunek ogona.</li><li>Dobierz próg z warunku rozmiaru α.</li><li>Policz moc albo p-value, jeśli proszą.</li></ol></div>'''
}
]

def nav(idx=None):
    items = ['<a href="../index.html">Start</a>' if idx is not None else '<a href="index.html">Start</a>', '<a href="../kurs-statystyka-full.html">Jedna strona</a>' if idx is not None else '<a href="kurs-statystyka-full.html">Jedna strona</a>', '<a href="../reference/statystyka-listy-6-10.html">Ściąga</a>' if idx is not None else '<a href="reference/statystyka-listy-6-10.html">Ściąga</a>']
    if idx is not None and idx > 0: items.append(f'<a href="{lessons[idx-1]["slug"]}">← Poprzednia</a>')
    if idx is not None and idx < len(lessons)-1: items.append(f'<a href="{lessons[idx+1]["slug"]}">Następna →</a>')
    return '<nav class="nav">' + ''.join(items) + '</nav>'

def lesson_article(l, i):
    return f'''<section id="l{i+1}"><p class="eyebrow">{l['list']}</p><h1>{l['title']}</h1><p class="lead">{l['goal']}</p><div class="source"><b>Źródło główne:</b> {l['source']}<br><span class="muted">Uwaga: katalog psets istnieje obok repo, ale w kontenerze nie mam uprawnień do czytania go. Dlatego odwołania do list są tematyczne, nie do numerów konkretnych zadań.</span></div>{l['body']}<div class="box small"><b>Jak się uczyć:</b> zasłoń schemat, odtwórz go z pamięci, potem zrób jedno zadanie z listy w tym wzorcu. Jeśli utkniesz, zapytaj mnie o dokładnie ten krok.</div></section>'''

for i,l in enumerate(lessons):
    html = f'''<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{l['title']}</title><style>{CSS}</style></head><body><main><div class="shell"><div class="hero">{nav(i)}</div><article>{lesson_article(l,i)}</article></div></main></body></html>'''
    (lessons_dir/l['slug']).write_text(html, encoding='utf-8')

aliases = {'0001-estymacja.html':0,'0002-redukcja-statystyk.html':2,'0003-rao-blackwell-umvue.html':2,'0004-przedzialy-ufnosci.html':3,'0005-testy-hipotez.html':4}
for name, idx in aliases.items():
    (lessons_dir/name).write_text((lessons_dir/lessons[idx]['slug']).read_text(encoding='utf-8'), encoding='utf-8')

cards = ''.join(f'<div class="card"><span class="tag">{l["list"]}</span><h2><a href="lessons/{l["slug"]}">{l["title"]}</a></h2><p>{l["goal"]}</p></div>' for l in lessons)
index = f'''<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Kurs statystyki — listy 6–10</title><style>{CSS}</style></head><body><main><div class="shell"><div class="hero"><p class="eyebrow">Kurs statystyki</p><h1>Listy 6–10: schematy rozwiązywania zadań</h1><p class="lead">Przepisana wersja: mniej ogólników, więcej schematów, przykładów i odwołań do zakresu z notatek.</p>{nav(None)}</div><article><div class="grid">{cards}</div><div class="pitfall"><b>Na Androidzie:</b> jeśli otwierasz plik z Discorda i widzisz adres content://, użyj wersji jednoplikowej. Linki między osobnymi plikami mogą się wtedy psuć.</div></article></div></main></body></html>'''
(base/'index.html').write_text(index, encoding='utf-8')

full_nav = '<nav class="nav">' + ''.join(f'<a href="#l{i+1}">{l["list"]}</a>' for i,l in enumerate(lessons)) + '<a href="#sciaga">Ściąga</a></nav>'
full_body = ''.join(lesson_article(l,i) for i,l in enumerate(lessons))
cheat_grid = ''.join([ '<div class="card"><h2>Lista 6</h2><p>Momenty, kwantyle, plug-in, MLE.</p></div>', '<div class="card"><h2>Lista 7</h2><p>Obciążenie, MSE, zgodność, Cramer–Rao.</p></div>', '<div class="card"><h2>Lista 8</h2><p>Faktoryzacja, minimalność, zupełność, UMVUE.</p></div>', '<div class="card"><h2>Lista 9</h2><p>Funkcja centralna i odwracanie nierówności.</p></div>', '<div class="card"><h2>Lista 10</h2><p>NP, MLR, UMP, p-value, LR.</p></div>' ])
full = f'''<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Kurs statystyki — jedna strona</title><style>{CSS}</style></head><body><main><div class="shell"><div class="hero"><p class="eyebrow">Wersja jednoplikowa</p><h1>Statystyka matematyczna — listy 6–10</h1><p class="lead">Najlepsza wersja na telefon: wszystko jest w jednym HTML-u, więc Androidowe content:// nie psuje linków.</p>{full_nav}</div><article>{full_body}<section id="sciaga"><h1>Ściąga końcowa</h1><div class="grid">{cheat_grid}</div></section></article></div></main></body></html>'''
(base/'kurs-statystyka-full.html').write_text(full, encoding='utf-8')

cheat = f'''<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Ściąga — statystyka listy 6–10</title><style>{CSS}</style></head><body><main><div class="shell"><div class="hero"><p class="eyebrow">Ściąga</p><h1>Statystyka — listy 6–10</h1>{nav(None)}</div><article><div class="grid"><div class="card"><h2>Estymacja</h2><pre class="formula">Momenty: EX^j=(1/n)ΣX_i^j
MLE: argmax l(θ)</pre></div><div class="card"><h2>Ryzyko</h2><pre class="formula">MSE = Var + bias²
R(T,θ)=E L(T,θ)</pre></div><div class="card"><h2>Dostateczność</h2><pre class="formula">f(x;θ)=g_θ(T(x))h(x)</pre></div><div class="card"><h2>UMVUE</h2><pre class="formula">T dostateczna + zupełna
W nieobciążony
E[W|T]</pre></div><div class="card"><h2>Przedziały</h2><pre class="formula">a ≤ Q(X;θ) ≤ b
→ odwróć względem θ</pre></div><div class="card"><h2>Testy</h2><pre class="formula">NP: f1/f0 &gt; c
MLR: ogon T
LR: sup_H0 l / sup_Θ l</pre></div></div></article></div></main></body></html>'''
(ref_dir/'statystyka-listy-6-10.html').write_text(cheat, encoding='utf-8')

(base/'RESOURCES.md').write_text('''# Resources

## Primary source
- `/opt/data/workspace/matematyka/statystyka/main.typ` — główne źródło treści. Lekcje oparto przede wszystkim na sekcjach: estymacja parametryczna, ocena jakości estymatorów, redukcja statystyk, Rao–Blackwell/UMVUE, estymacja przedziałowa, testowanie hipotez, MLR/UMP, p-value, testy LR.

## Problem lists
- `/opt/data/workspace/psets` — katalog z listami zadań istnieje obok repo, ale w kontenerze ma uprawnienia `770 root:9997`, więc nie był czytelny z tej sesji. Dlatego lekcje odwołują się do „list 6–10” przez zakres tematyczny i typy zadań, nie przez numery konkretnych zadań.

## Best file for phone
- `kurs-statystyka-full.html` — jednoplikowa wersja kursu, odporna na problem Androidowego `content://`.
''', encoding='utf-8')
(base/'NOTES.md').write_text('''# Notes

- Użytkownik chce kurs po polsku, dydaktyczny, oparty głównie na lokalnych notatkach.
- Preferowane są proste schematy rozwiązywania zadań, dużo przykładów i jasne powiązanie z listami 6–10.
- Dla telefonu najlepiej wysyłać `kurs-statystyka-full.html` albo ZIP z tym plikiem na wierzchu, bo linki między plikami HTML potrafią się psuć przy Androidowym `content://`.
''', encoding='utf-8')

out = Path('/opt/data/workspace/matematyka/teach-statystyka-v2.zip')
if out.exists(): out.unlink()
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write(base/'kurs-statystyka-full.html', 'kurs-statystyka-full.html')
    for p in sorted(base.rglob('*')):
        if p.name == 'generate_course.py':
            continue
        zf.write(p, p.relative_to(base.parent))
print(out)
print('html files', len(list(base.rglob('*.html'))))
