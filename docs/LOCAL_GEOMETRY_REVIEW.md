# Lokalna kontrola analitycznej geometrii

Data: 13 listopada 2026. Zakres zaakceptowany przez właściciela: pięć pozostałych
działów, 35 nowych rodzajów zadań i po trzy poziomy. Praca na gałęzi
`codex/analytic-geometry-remaining`, od bazy
`78b8ef0c5650fffab9420d7b2ceec54cf9bfbfde`. Ten raport opisuje weryfikację lokalną
przed publikacją; sam w sobie nie potwierdza push ani wdrożenia.

Dokładny zakres, granice i instrukcja powtarzania kontroli są w
[Analytic geometry practice](architecture/ANALYTIC_GEOMETRY.md). Nie jest to
deklaracja odtworzenia wszystkich podpunktów zbioru 1:1 ani formalnego dowodu
bezbłędności programu.

## Wynik kontroli w trzech rolach

To trzy przejścia kontrolne tego samego wykonawcy, nie niezależne recenzje
profesora, nauczyciela i projektanta. Dodatkowych agentów nie uruchamiano.

| Przejście | Istotne znalezisko | Poprawka i ponowna kontrola |
|---|---|---|
| Matematyczne | Jednostkowe prostopadłe i warunek objętości mają dwa rozwiązania. Kolejność nie powinna mieć znaczenia. | Sprawdzane są oba wektory; brak jednego lub duplikat nie jest pełną odpowiedzią. Ręczne przykłady, dokładny parser i niezależne sprawdzenie długości, iloczynów i objętości. |
| Matematyczne | Płaszczyzna i parametryzacja nie mają jednej poprawnej postaci tekstowej. | Sprawdzanie dokładnej równoważności płaszczyzn i przestrzeni afinicznych. Testy skalowania, przesunięcia parametru, zmiany bazy, utraty rzędu i niedozwolonych dziur w dziedzinie. |
| Matematyczne | Przecięcie, równoległość, pokrywanie i skośność wymagają różnych kryteriów. | Osobne typy klasyfikacji, pełne warunki, zerowe odległości, wszystkie trzy położenia punktów względem płaszczyzny w przygotowanej puli. |
| Matematyczne | Parametry trzech płaszczyzn opisują całe zbiory, a rysunek jeden przypadek. | Kryterium dla wszystkich par parametrów pozostaje jawne. Podpis rysunku podaje konkretne a,b. Sprawdzono równania płaszczyzn i każdą ilustrowaną linię przecięcia przez podstawienie. |
| Dydaktyczne | Dwa początkowe poziomy kollinearności były zbyt podobne. | Poziom 2 odtwarza jeden środek, poziom 3 dwa. Jednostkowe prostopadłe odtwarzają kolejno jeden i oba wektory. Liczby pozostają w tym samym zakresie. |
| Dydaktyczne | Brakowało jawnych przejść w układach, kierunku projekcji i wyborze punktu na płaszczyźnie. | Dodano układy i ich redukcję, definicje symboli, wybór punktu oraz sprawdzenia warunków. Usunięto odwołanie do niepodanych końców odcinka przy odległości prostych. |
| Dydaktyczne | W zadaniu o trzech płaszczyznach A,B oznaczały punkty i szukane stałe. | Końce odcinka oznaczono E,F. Stałe A,B zachowują jedno znaczenie. |
| UI/UX | Długie warunki nie mieściły się w jednej formule. | Zwykły tekst zawija się; dane matematyczne są osobnymi fragmentami. Poprawiono także odstępy TeX przy słowach „and/or”, które powodowały surowy zapis zamiast wzoru. |
| UI/UX | Linki nowych sekcji prowadziły do tego samego widoku. | Osobne adresy i klucze sekcji oraz poprawne zaznaczenie bieżącej pozycji. Wszystkie pięć list ma swoje rodzaje zadań. |
| UI/UX | Stare płaszczyzny pomocnicze i podpisy zasłaniały wynik projekcji. | Późniejsze kadry pomijają wykorzystane konstrukcje; wcześniejsze pozostają w rozwiązaniu. Podpisy 2D nie wychodzą poza kadr i szukają pobliskiego wolnego miejsca. Na sprawdzonym trudnym przykładzie 12 podpisów nie nachodzi na siebie w obu rozmiarach ekranu. |
| Matematyczne / UI | Skończony fragment nieskończonej prostej lub płaszczyzny nie obejmował części leżących na niej punktów i końców wektorów. | Zasięg rysunku uwzględnia widoczne obiekty spełniające równanie prostej lub płaszczyzny. W całej przygotowanej puli liczba takich obciętych kadrów spadła z 33 dla prostych i 334 dla płaszczyzn do zera. Regresje sprawdzają parametry położenia wewnątrz fragmentu, a nie tylko samą współliniowość lub współpłaszczyznowość. |
| UI/UX | Duża ujawniona para wektorów rozszerzała całą stronę telefonu. | Ograniczono szerokość odpowiedzi. Dwa wektory mają dwa zwarte edytory współrzędnych, z informacją o dowolnej kolejności. |
| Integracyjne | Pierwsze otwarcie kodu w podglądzie mogło wysłać kilka żądań konkurujących o jeden worker. | Nowe kody obecne w zweryfikowanej puli są odczytywane z niej bez liczenia i zajmowania workera. Kody spoza puli nadal przechodzą przez proces z limitami. Po poprawce cztery równoczesne odczyty zimnego kodu zwróciły 200. |

## Dlaczego ten wariant odpowiada celowi

Wzory i rysunki korzystają z tych samych dokładnych danych konstrukcji. Nie ma
drugiego generatora po stronie przeglądarki, który mógłby przedstawić inną
geometrię. Zachowano istniejący silnik, kody, sprawdzanie, historię, kartę i
mechanizm ujawniania rozwiązania. Dzięki temu kolejne rodzaje mogą rozszerzać
ten sam mechanizm, zamiast wymagać wymiany całego modułu.

Student wybiera jeden rodzaj i poziom; dostaje jedno zadanie. Rozwiązanie pokazuje
istotne przekształcenia, regułę i odpowiedni etap rysunku. Kolor pomaga połączyć
wzór z konstrukcją, ale znaczenie jest również opisane słowami i oznaczeniami.
Usuwanie niepotrzebnych obiektów z późniejszych kadrów ogranicza przeciążenie
obrazu. Nazwy widoków nie sugerują, że zwykła projekcja 2D zachowuje kąty.

To uzasadniony wybór dla uzgodnionego zakresu i istniejącego projektu, nie
twierdzenie, że jest najlepszy dla każdego kursu lub każdego studenta.

## Dowody lokalne

- 466 testów geometrii, katalogu i sąsiednich istniejących rodzin przeszło;
  23 pominięcia dotyczą linuksowych limitów oraz skryptu wydania dla Linux.
- Osobny aktualny przebieg integracji: 42 testy. Kontrola starych kodów i ich
  publicznej granicy wraz z nową integracją: 3304 testy, 1066 pominięć dotyczących
  linuksowych workerów pozostałych rodzin. Liczniki częściowo się pokrywają.
  Końcowe powtórzenie całego zestawu katalogu wraz z integracją po poprawce
  rysunków: 58 testów przeszło, jeden skrypt wydania dla Linux pominięto na Windows.
- Po ostatniej poprawce zasięgu rysunków: 338 testów odpowiedzi, konstrukcji
  i wizualizacji. W dodatkowym przebiegu 128 testów wizualizacji sprawdza również,
  czy widoczne incydentne punkty i końce wektorów mieszczą się na fragmentach
  prostych i płaszczyzn dla wszystkich 105 kombinacji rodzaju i poziomu.
- Rzeczywisty worker Linux: 105 kombinacji rodzaj/poziom przyjęło dokładną
  odpowiedź i odrzuciło poprawną składniowo błędną odpowiedź. Dodatkowo 105
  kodów spoza puli odtworzyło pełne rozwiązania i poprawny poziom w limitowanym
  procesie. Po zmianie oznaczeń powtórzono dziewięć przypadków trzech płaszczyzn.
- PostgreSQL: 52 testy wybranego przepływu geometrii przeszły na jednorazowej
  bazie. Obejmują zapis, błędną/poprawną odpowiedź, ujawnienie i ponowne otwarcie
  oraz brak prywatnych pól przed ujawnieniem. Migracje i kontrola RLS także przeszły.
  Po ostatniej zmianie zasięgu rysunków powtórzono 105 odtworzeń kodów spoza
  puli i 52 testy bazy na nowej, zweryfikowanej kopii źródeł; oba przebiegi przeszły.
- Frontend: 946 testów w 72 plikach, lint, TypeScript i produkcyjny build.
  Backend: Ruff, format i mypy dla 209 plików. Build zachowuje ostrzeżenie o
  dużych istniejących paczkach, a testy ostrzeżenie Starlette/httpx.
- W próbkach generatora każda z 105 kombinacji ma osiem powtarzalnych seeds,
  ręcznie wyliczone przykłady i wybrane niezależne niezmienniki geometryczne.
  Nie każdy seed jest osobną niezależną recenzją całego rozwiązania.
- Przygotowana pula nowych rodzin: 267 rekordów, 1813 kadrów. Największy kadr
  ma 5706 bajtów wobec limitu 8192; maksimum to 7 punktów, 23 linie i 8 trójkątów.
  Największy zapis zadania ma 57042 bajty. Przy rozbudowie trzeba pilnować
  również limitu 64 KiB całej odpowiedzi workera, nie tylko pojedynczej sceny.
- Jedna próba workera uruchomiona równolegle z innymi ciężkimi testami zakończyła
  się błędem limitowanego procesu. Diagnostyczne odtworzenie tego samego kodu i kolejna seria
  105 przypadków przeszły bez zmiany limitów. Obciążenie jest prawdopodobnym,
  ale nie jednoznacznie udowodnionym wyjaśnieniem. Przeciążenie ma pozostać
  błędem 503 z możliwością ponowienia, nie oceną „Incorrect”.

Sprawdzenie przeglądarkowe korzystało z prawdziwego lokalnego API, bazy i workera,
syntetycznego konta oraz podglądu całego serwisu przez Tailscale. Obejmuje szeroki
ekran i emulację 390×844, oba motywy, wszystkie pięć list, różne rodzaje pól i
przykłady poziomów 1–3. Przejrzano m.in. parametryzację płaszczyzny, parametry
prostopadłości, trzy płaszczyzny, kollinearność, pary wektorów, warunki objętości,
odległości, kąty i rzut całej prostej.

Potwierdzono ruch kamery klawiszami i emulowanym gestem, odtworzenie obrazu po
resetowaniu, usunięcie niewidocznego canvasu i tylko jedną scenę przy przewinięciu
do warunku. Wymuszony brak WebGL uruchomił opisany widok 2D z trzema osiami.
Przeskalowane równanie płaszczyzny zostało zaakceptowane, a rozwiązanie i rysunek
przetrwały ponowne wczytanie karty. Próba pobrania prywatnego pliku katalogu
przez serwer podglądu zwróciła 403.

Po poprawce zasięgu ponownie obejrzano przecięcie prostej z płaszczyzną w 2D
i 3D oraz oba wektory spełniające warunki płaszczyzny i objętości, na wąskim
ekranie i w ciemnym motywie na szerokim. Nie było poziomego przewijania całej
strony ani podpisów poza kadrem. Odświeżony podgląd udostępnia cały serwis:
API zwróciło 50 tematów z algebry, analizy i rachunku prawdopodobieństwa.

### Powtarzalne przykłady

Kody dotyczą tej lokalnej wersji; nie oznaczają publikacji na stronie produkcyjnej.

| Rodzaj / poziom | Kod |
|---|---|
| Równanie płaszczyzny / 3 | `JAE-1-0002000000000000-24` |
| Oba jednostkowe prostopadłe / 2 | `JAC-1-0001000000000000-00` |
| Warunki płaszczyzny i objętości / 3 | `JAD-1-0002000000000000-41` |
| Trzy różne linie przecięcia / 3 | `JAN-1-0002000000000000-01` |
| Kierunkowy rzut prostej / 3 | `JBD-1-0002000000000000-67` |
| Kąt płaszczyzn / 2 | `JAP-1-0001000000000000-39` |
| Przecięcie prostej z płaszczyzną / 1, regresja zasięgu | `JAW-1-0000000000000000-33` |
| Warunki płaszczyzny i objętości / 1, regresja zasięgu | `JAD-1-0000000000000001-48` |

## Granice i osobne problemy

Pełna regresja całego backendu nie jest zielona. Na niezmienionej bazie
`78b8ef0` odtworzono wcześniejsze problemy testów Analysis: fixture zmiennych
pochodnych zakłada inny wylosowany generator, test granicy zakłada błędnie, że
zero zawsze jest niepoprawne, a serializer testowy nie obsługuje zagnieżdżonego
`LimitAnswer` dla całek niewłaściwych. Nie zmieniano ich logiki ani własności
drugiego wykonawcy. Szeroki przebieg przerwany kolejną turą nie jest liczony
jako zaliczona pełna regresja. Przed przyszłym push obowiązuje ponadto
projektowy `scripts/pre-push.py` i osobna zgoda właściciela.

Nie przeprowadzono nowego testu na fizycznym telefonie, kompletnego audytu
czytnikiem ekranu, niezależnej recenzji matematycznej ani badania ze studentami.
W zwykłej projekcji obiekty mogą się nakładać; do rozróżnienia ich położenia
pozostaje obrót 3D. Zakres kątów i parametrów jest świadomie ograniczony, jak
opisano w macierzy pokrycia. Nie dodawano wykresów do eksportu PDF ani zadań
na dowody z punktu 97.

Poza właścicielem i wykonawcą warto zaangażować prowadzącego geometrię do
niezależnej oceny rozwiązań i poziomów, kilku studentów pierwszego semestru do
próby zrozumienia bez podpowiedzi oraz specjalistę od dostępności do kontroli
klawiatury, czytnika ekranu i rzeczywistych urządzeń. Te działania mogą ulepszyć
materiał; nie są przedstawiane jako już wykonane.
