# Audyt lokalnych działów algebry

Zakres: lokalny podgląd `practiceloop-algebra-redesign`, nie wdrożenie produkcyjne. Weryfikacja dotyczy gotowych generatorów; brakujące rodzaje są propozycjami dalszych prac, nie deklaracją pełnego pokrycia materiału.

## Inwentarz podtematów

| Podtemat | Dostępne rodzaje i ustawienia | Granice obecnego zakresu |
|---|---|---|
| Matrix operations | cztery działania, poziom 1–3, niezależne wymiary 1–5 | dzielenie wymaga kwadratowej i odwracalnej B oraz zgodnych wymiarów |
| Determinants | poziom 1–3, rozmiar 2–5 | zakres generatora nie obejmuje 1×1 |
| Inverse matrices | poziom 1–3, rozmiar 2–5 | generowane są macierze odwracalne |
| Matrix rank | poziom 1–3, wiersze i kolumny 2–5 | przypadki prostokątne, zerowe i zależne wymagają dalszej próbki niezależnej |
| Systems of linear equations | poziom 1–3, 2–5 niewiadomych | tylko układy kwadratowe z jednym rozwiązaniem |
| Complex arithmetic | mnożenie i dzielenie, poziom 1–3 | odpowiedź w postaci algebraicznej |
| Modulus | moduł wyrażenia, własności modułu, okrąg jako zbiór punktów; poziom 1–3 | odpowiedź dokładna; dla okręgu środek i promień |
| Converting complex forms | cztery kierunki między postacią algebraiczną a trygonometryczną lub wykładniczą, poziom 1–3 | wymaga argumentu głównego |
| Polar form, powers and roots | argument, potęga, wybrany pierwiastek | rodzaje nie są poziomami; pierwiastki: jeden wskazany, nie pełny zbiór |
| Division, remainders and divisibility | iloraz i reszta, twierdzenie o reszcie, podzielność; poziom 1–3 | zakres dzielników zależy od generatora |
| Roots and factors | różne pierwiastki rzeczywiste, poziom 1–3 | generowane pierwiastki rzeczywiste są całkowite |
| Partial fractions | różne liniowe, powtórzony liniowy, nierozkładalny kwadratowy | nie obejmuje wszystkich możliwych rozkładów |

## Znaleziska i decyzje

1. **Odrzucanie równoważnych odpowiedzi — poprawione w lokalnym checkerze.** Rozpoznawane są małe wymierne mianowniki, takie jak `1/(-1)` i `1/(0-1)`, a dzielenie przez zero pozostaje niedozwolone. Dopuszczone są też ograniczone wyrażenia z pierwiastkami w mianowniku, np. `2/sqrt(2)` i `(1+sqrt(2))/(1+sqrt(2))`. Checker ma nadal ograniczoną gramatykę i nie gwarantuje akceptacji wszystkich matematycznie równoważnych wyrażeń.
2. **Lokalne losowanie — zaimplementowane.** Użytkownik wskazuje gotowe podtematy, poziomy i rodzaje; dla działań macierzowych również wymiary. Wybór podtematu jest równomierny, a następnie wybierany jest rodzaj w obrębie tego podtematu. Konfiguracja jest przechowywana na urządzeniu i używana dla kolejnych zadań.
Po wygenerowaniu zadania ustawienia losowania zwijają się, ale można je ponownie otworzyć. Podtematy bez lokalnych generatorów są oznaczone jako niedostępne lokalnie.
3. **Skala — poprawiona lokalnie.** Rzeczywiste trzy poziomy mają trzy kropki; rodzaje zadań postaci trygonometrycznej nie są przedstawiane jako poziomy. Produkcyjna skala pozostaje oddzielna.
4. **Drzewo na telefonie — zmienione lokalnie.** Panel otwierany jest przyciskiem, a wybór podtematu zamyka go. Należy jeszcze wykonać kontrolę dotyku na prawdziwym telefonie.
5. **Pokrycie materiału — otwarte.** Brak typów wymienionych w tabeli należy przedyskutować oddzielnie; nie zostały dodane automatycznie w trakcie audytu.
6. **Uproszczone rodzaje — wycofane z lokalnego menu i losowania.** Po decyzji użytkownika usunięto działania na wielomianach, liczenie pierwiastków według stopnia, dodawanie i odejmowanie liczb zespolonych oraz bezpośrednie przejścia między postacią trygonometryczną i wykładniczą. Dotychczasowe generatory pozostawiono dla zgodności istniejących kodów; produkcja nie została zmieniona.
7. **Moduł — przebudowany lokalnie.** Dodano wyrażenia z działaniami, wykorzystanie własności modułu oraz równania okręgu z wizualizacją i osobnymi polami środka i promienia. Każdy rodzaj ma trzy poziomy; rozwiązania i opisy pozostają po angielsku.

## Dowody i ograniczenia

- Wcześniejsza próba studenta: 150 zestawów API, 40 dodatkowych macierzy 5×5 i 14 podstawowych przepływów w emulacji 390 px. Odpowiedzi w części testów odtwarzano z tego samego generatora.
- Dla nowego losowania dodano test wyboru podtematu przed rodzajem, test wymiarów macierzy, test argumentu/potęgi/pierwiastka bez sztucznego poziomu oraz test zapisu i kolejnego zadania.
- W przeglądarce Edge, w emulacji 390 px, sprawdzono otwarcie i zamknięcie panelu, losowanie modułu, generowanie następnego zadania oraz brak poziomego przewijania całej strony. Osobno sprawdzono mnożenie 2×3 przez 3×4 i odtworzenie konfiguracji po odświeżeniu.
- Końcowa regresja: 824 testy frontendu, lint i build przeszły; 34 testy lokalnych generatorów i checkerów oraz kontrola Ruff przeszły. Build zgłasza ostrzeżenie o rozmiarze paczek, a testy backendu ostrzeżenie o przestarzałej integracji Starlette/httpx.
- Po ponownym uruchomieniu lokalnego API sprawdzono w emulacji także potęgowanie liczby zespolonej: wybrany rodzaj trafia do generatora, rozwiązanie ma kolejne kroki i wizualizację, a kropki poziomu nie są pokazywane.
- Nie przeprowadzono niezależnej recenzji matematyka, testu na rzeczywistym telefonie ani kompletnej weryfikacji każdej kombinacji ustawień. Te ograniczenia nie pozwalają uznać audytu za pełne potwierdzenie poprawności matematycznej.
