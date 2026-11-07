# Wytyczne strony i rozwiązań — algebra

Status: robocze; decyzje potwierdzone w rozmowie oraz punkty do ustalenia oznaczono niżej. Niniejszy dokument opisuje lokalny podgląd w checkoutcie `practiceloop-algebra-redesign`; nie oznacza wdrożenia. Zachowaj istniejące, niezacommitowane zmiany. Przed pracą przeczytaj również `AGENTS.md` oraz `docs/intent/CONTENT_STYLE.md`.

## Uzgodniony sposób pracy

- Pracuj lokalnie. Nie wykonuj push ani wdrożenia bez nowego polecenia użytkownika. Projekt graficzny może jeszcze ulec zmianie.
- Używaj generatorów zadań. Ustawienia są wybierane przed pierwszym kliknięciem **Generate problem**; następnie dostępne są **Check answer**, **Show answer**, **Show solution** i **Generate next problem**.
- Wybór tematu odbywa się przez drzewo. Na telefonie drzewo ma być zwijanym panelem otwieranym przyciskiem. Przy niezgodnych wymiarach operacji macierzowych pokaż wyjaśnienie i nie generuj błędnego zadania. Same macierze prostokątne są poprawne, gdy wymiary działania są zgodne.
- Zwróć uwagę na testowalność: zapisuj parametry lub kod umożliwiający odtworzenie przykładu. Nie ujawniaj poprawnej odpowiedzi ani rozwiązania przed odpowiednim żądaniem.

## Język i układ

- Tekst produktu i wyjaśnień pozostaje po angielsku. Pisz krótko, precyzyjnie, w stylu podręcznika, bezosobowo; inspiruj się zasadami prostego języka STE, bez deklarowania zgodności z ASD-STE100. Styl wypowiedzi użytkownika ma pierwszeństwo przed starszą propozycją zwracania się do czytelnika „you”.
- Zachowaj istniejące logo, ciemną estetykę i komponenty projektu. Treść polecenia umieść poza polem przykładu; w samym polu pokaż wyłącznie niepokolorowane wyrażenie matematyczne.
- Korzystaj z KaTeX i istniejącego pola odpowiedzi z klawiaturą PracticeLoop. Opis, pole odpowiedzi i przyciski pozostają widoczne i czytelne na telefonie.
- Długie wzory, macierze i kroki muszą mieć lokalne przewijanie poziome, bez ucinania treści i bez poziomego przewijania całej strony. Zachowaj dostępność klawiatury i czytelne oznaczenia niezależne od koloru.

## Rozwiązania

- Pokaż pełne rozwiązanie dopiero po kliknięciu **Show solution**. Zacznij od przepisania zadania; kolejne numerowane kroki podawaj w rzeczywistej kolejności działań. Każdy istotny krok ma krótki opis matematyczny.
- Pokaż podstawienia, warunki stosowalności, istotne przekształcenia i wynik. Nie pomijaj dziedzin, krotności, zerowych części liczby zespolonej ani przypadków szczególnych, gdy są istotne dla zadania.
- Kolory są dopuszczalne w rozwiązaniu, jeśli wyjaśniają powiązania matematyczne. Koloruj nawias razem z jego zawartością, jeżeli cały nawias oznacza daną grupę. Nie polegaj wyłącznie na kolorze. To potwierdzone przez użytkownika odstępstwo od starszych reguł systemu wzorniczego.
- Przy istotnym dla studiów twierdzeniu lub wzorze umożliwiaj kliknięcie odpowiedniego kroku i rozwinięcie ogólnego wzoru wraz z objaśnieniem. Nie dodawaj podpowiedzi dla elementarnych reguł maturalnych, np. podstawowego mnożenia nawiasów.
- Wizualizacje mają przedstawiać faktyczne dane zadania i być zrozumiałe bez nich; pokazuj je po ujawnieniu rozwiązania. Dla liczb zespolonych wykorzystuj płaszczyznę zespoloną i istniejące interakcje, jeśli pasują do zadania.

## Zasady specyficzne dla macierzy

- Dopuszczalne wymiary działań: do 5×5. Dla iloczynu wiersz A i odpowiadająca mu kolumna B muszą pokazywać zgodne pary elementów; wizualizacja wyjaśnia powstawanie wybranego elementu wyniku.
- Dzielenie zapisuj w zadaniu jako `A : B`, a w rozwiązaniu interpretuj jako `A B⁻¹`; sprawdź zgodność wymiarów i odwracalność B.
- Odwracanie i eliminacja: pokazuj operacje wierszowe krok po kroku i wyróżniaj wiersze uczestniczące w operacji, nie kolorując pojedynczych elementów bez potrzeby.
- Wyznaczniki: 2×2 i 3×3 pokazuj wizualnie; dla większych stopni pokazuj rozwinięcie do minorów 3×3. Pokaż znaki dopełnień, a kliknięcie minora powinno wskazać właściwe elementy macierzy rodzicielskiej.

## Zasady specyficzne dla modułu

- Lokalny podtemat obejmuje moduł wyrażenia po działaniach, zastosowanie własności modułu i równania okręgu interpretowane jako odległość. W zadaniach geometrycznych odpowiedź to współrzędne środka i dodatni promień.
- Wyjaśniaj zastosowane własności iloczynu, ilorazu i potęgi oraz warunek niezerowego mianownika. Wizualizacja okręgu pokazuje jego środek i promień w tej samej skali osi.
- W lokalnym menu nie oferuj samodzielnie prostych działań na wielomianach, liczenia pierwiastków z samego stopnia, dodawania i odejmowania liczb zespolonych ani bezpośrednich przejść między postacią trygonometryczną i wykładniczą.

## Uzgodniony zakres pierwszego etapu

- Audyt obejmuje macierze, liczby zespolone i wielomiany oraz poprawę znalezionych błędów; nie oznacza automatycznej realizacji wszystkich potencjalnych typów zadań.
- Lokalny tryb losowania ma wybierać wyłącznie spośród gotowych lokalnych podtematów. Dla każdego wybranego podtematu z poziomami użytkownik wybiera osobny poziom trudności. W działaniach na macierzach wybiera również operację i wymiary; do losowania dopuszczalne są tylko zgodne ustawienia.
- W podtemacie „Polar form, powers and roots” użytkownik zaznacza rodzaje zadań osobno; argument, potęga i pierwiastek nie są poziomami trudności. W pozostałych podtematach z rodzajami zadań użytkownik również może zaznaczyć dopuszczone rodzaje osobno.
- Braki rodzajów zadań wykryte w audycie zapisz w raporcie; dalsze rozszerzenia materiału uzgadnia się osobno.
- Mobilne drzewo ma być panelem otwieranym przyciskiem; po wybraniu podtematu panel zamyka się i pokazuje ustawienia tego podtematu.
- W lokalnych zadaniach z trzema poziomami karta pokazuje trzy kropki, zgodne z wybranym poziomem.

## Znane ograniczenia i kwestie do potwierdzenia

- Test studenta znalazł odrzucanie równoważnego `1/(-1)` oraz niespójność wyboru **Advanced** z oznaczeniem `3/5`; lokalny checker i skala zostały poprawione. Lokalne losowanie korzysta z gotowych generatorów, a pozostałe tematy są oznaczone jako niedostępne w podglądzie.
- Zbiór pierwiastków wielomianów w obecnym generatorze ogranicza się do rzeczywistych całkowitych; układy liniowe mają jedno rozwiązanie. Generator twierdzenia algebry pyta głównie o liczbę pierwiastków z krotnościami. To zakres obecnej implementacji, nie zatwierdzony docelowy program.
- W losowaniu każdy wybrany podtemat ma jednakową szansę; dopiero po jego wyborze losowany jest jeden z dopuszczonych rodzajów. **Generate next problem** losuje z tego samego zapisanego wyboru. Nie przedstawiaj tych propozycji jako decyzji użytkownika.

## Przekazanie i weryfikacja

- Dla każdej zmiany sprawdź generowanie, poprawną i błędną odpowiedź, ujawnienie odpowiedzi i rozwiązania oraz kolejne zadanie. Testuj przypadki brzegowe i równoważne zapisy; weryfikuj obliczenia niezależnie od generatora.
- Przeprowadź przegląd mobilny i komputerowy w rzeczywistej przeglądarce; odróżnij emulację od testu na fizycznym urządzeniu. Sprawdź również obsługę klawiatury i dostępność.
- W raporcie podaj zakres rzeczywiście przetestowany, wyniki, ograniczenia i lokalizację istotnych usterek. Przy przeglądzie matematycznym nie sugeruj, że automatyczny test zastępuje niezależnego eksperta.
