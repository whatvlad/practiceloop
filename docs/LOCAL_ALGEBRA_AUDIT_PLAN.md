# Plan audytu i poprawek lokalnej algebry

Status: **zatwierdzony przez użytkownika; realizacja lokalna rozpoczęta**. Baza lokalnego checkoutu w chwili opracowania: `464dc77`; przed pracą ponownie sprawdź aktualny stan. Zachowaj wszystkie istniejące zmiany użytkownika. Obowiązują także `AGENTS.md` i `docs/ALGEBRA_SOLUTION_GUIDELINES.md`.

## Cel i zakres

Audyt oraz poprawa błędów w trzech lokalnych działach: macierze, liczby zespolone i wielomiany. Działaj w lokalnym checkoutcie `practiceloop-algebra-redesign`; bez pushowania, scalania i wdrażania. Luki w zakresie materiału zapisuj w raporcie, a nowe rodzaje zadań uzgadniaj osobno. Użytkownik chce zachować obecny przepływ i możliwość dalszych zmian wyglądu.

## Potwierdzone decyzje

1. Lokalne losowanie obejmuje tylko gotowe lokalne podtematy. Użytkownik wybiera każdy podtemat i, tam gdzie poziomy faktycznie istnieją, osobny poziom trudności.
2. Użytkownik może osobno zaznaczać dopuszczone rodzaje zadań w podtematach, które je oferują. Dla działań na macierzach ustawia operację i wymiary; niezgodnych wymiarów nie wolno generować.
3. Argument, potęga i pierwiastek w `Polar form, powers and roots` są rodzajami zadania, a nie poziomami trudności; można je zaznaczyć osobno.
4. Losowanie ma dwa etapy: każdy wybrany, poprawnie skonfigurowany podtemat ma równą szansę; następnie wybierany jest jeden z jego dopuszczonych rodzajów. Liczba zaznaczonych rodzajów nie zwiększa szansy podtematu.
5. **Generate next problem** losuje z tego samego zapisanego wyboru i ustawień. Brak konfiguracji lub niepoprawna konfiguracja ma czytelny komunikat; nie wolno losowo podstawiać innych ustawień.
6. Na telefonie drzewo tematów jest zwijanym panelem otwieranym przyciskiem. Po wybraniu podtematu panel zamyka się i pokazuje jego ustawienia; nie zasłania zadania ani klawiatury.
7. Zadania mające trzy rzeczywiste poziomy pokazują trzy kropki, zgodne z ustawieniem. Nie nazywaj rodzajów zadań poziomami; skalę produkcyjną innych zadań zachowaj, o ile audyt nie wykaże osobnego problemu.

## Etapy

### 1. Inwentaryzacja i kryteria

- Sporządź tabelę 14 lokalnych podtematów: dostępne rodzaje, poziomy, ustawienia, domena odpowiedzi, ważne przypadki brzegowe i znane braki. Sprawdź stan implementacji przed założeniem, że wszystkie opcje działają.
- Zachowaj dowody z poprzedniej próby: 150 zestawów API, 40 dodatkowych losowań 5×5 i 14 podstawowych przepływów w emulowanej przeglądarce. Te próby nie stanowią niezależnego dowodu matematyki ani testu prawdziwego telefonu.
- Oznacz błędy według skutku: błędna matematyka / odrzucenie poprawnej odpowiedzi; blokada korzystania; czytelność / niespójność; brak zakresu materiału.

### 2. Sprawdzanie odpowiedzi i matematyka

- Odtwórz błąd, w którym `-1` jest poprawne, a `1/(-1)` lub `1/(0-1)` jest odrzucane. Ustal, które równoważne wyrażenia mają być akceptowane, zachowując ograniczenia złożoności i odrzucając dzielenie przez zero.
- Zweryfikuj zadania, odpowiedzi i kroki dla przypadków brzegowych: zgodne i niezgodne wymiary, 1×1 i 5×5, macierze osobliwe, zerowe i powtarzające się pierwiastki, dziedzina ułamków, znaki i argumenty liczb zespolonych.
- Użyj niezależnych obliczeń symbolicznych oraz przykładów liczonych ręcznie. Test oparty na oczekiwaniu pobranym z tego samego generatora sprawdza integrację, ale nie dowodzi poprawności matematyki.

### 3. Lokalny tryb losowania

- Opracuj jedną spójną konfigurację wybranych podtematów, ich poziomów i dozwolonych rodzajów oraz ustawień macierzy. Trzymaj dane lokalnie, bez potrzeby logowania; nie mieszaj ich z zapisami produkcyjnymi bez uzasadnienia.
- Wybieraj podtemat równomiernie, następnie rodzaj. Przekaż poprawne ustawienia do odpowiedniego istniejącego generatora; nie zakładaj, że wszystkie generatory mają identyczne opcje.
- Zachowaj konfigurację dla kolejnego zadania, również po zmianie widoku lub odświeżeniu podglądu. Poinformuj o pustym wyborze i błędnych wymiarach; brak gotowych rodzajów nie może prowadzić do cichej zmiany wyboru.
- Pokryj testami wybór, filtrowanie, ustawienia, losowanie o różnej liczbie rodzajów, przejście do kolejnego zadania, odtworzenie wyboru oraz obsługę błędów.

### 4. Mobilna nawigacja i spójność

- Wprowadź panel otwierany przyciskiem w widoku mobilnym, z obsługą klawiatury, widocznym fokusem i poprawnym stanem otwarcia. Wybór podtematu zamyka panel i prowadzi do ustawień zadania.
- Ustal zachowanie trybu losowania w panelu tak, by konfiguracja wielu opcji była możliwa bez utraty wyboru; sprawdź zarówno dotyk, jak i klawiaturę.
- Dopasuj kropki do trzech faktycznych poziomów lokalnych i usuń mylące przedstawianie rodzajów zadań jako poziomów. Nie zmieniaj istniejącego zachowania innych obszarów bez potrzeby.

### 5. Przegląd rozwiązań i wyglądu

- Dla każdego rodzaju zadania sprawdź instrukcję, niepokolorowaną treść, pierwsze przepisanie zadania, kolejność operacji, klikalne istotne wzory oraz angielskie, bezosobowe opisy.
- Sprawdź przewijanie szerokich wzorów i macierzy, działanie klawiatury, przycisków, wizualizacji oraz dostępność informacji niezależnie od koloru. Porównaj wygląd na małym i dużym ekranie.
- Test przeglądarkowy emulujący telefon oznacz jako emulację; prawdziwy iPhone lub Android sprawdź osobno z udziałem użytkownika, jeżeli urządzenie jest dostępne.

### 6. Regresja i raport

- Wykonaj odpowiednie testy backendu, frontendu, lint i build; podaj rzeczywiste wyniki. Dodaj testy obejmujące nowe zachowania, w tym losowanie i poprawne odpowiedzi w równoważnych postaciach.
- Sporządź raport: problem, przykład odtwarzalny, waga, wprowadzone rozwiązanie, dowód ponownego sprawdzenia oraz pozostałe braki. Oddziel automatyczne testy, przegląd agenta, emulację i faktyczną ocenę użytkownika lub matematyka.

## Kryteria odbioru

- Nie pozostają znane błędy, które zmieniają wynik matematyczny lub blokują poprawną odpowiedź w uzgodnionym zakresie; przypadki niejednoznaczne są udokumentowane.
- Losowanie działa zgodnie z siedmioma decyzjami powyżej, bez wymagania konta w lokalnym podglądzie, i kontynuuje zapisany wybór.
- Trzy kropki oznaczają trzy poziomy, a na telefonie panel otwiera się i zamyka zgodnie z decyzją użytkownika.
- Żadne ważne obliczenie nie jest ucięte bez dostępnego przewijania; można korzystać z klawiatury i nie trzeba rozróżniać informacji wyłącznie po kolorze.
- Raport wskazuje zakres testów i wszystkie znane luki. Nie deklaruj certyfikacji dostępności ani niezależnej recenzji matematyka bez faktycznego wykonania.
