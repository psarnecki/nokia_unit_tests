# Naprawione błędy

## 2026-05-27

### 1) Transfer DL generowal nieprawidlowy ruch UL
- **Problem:** Podczas symulacji ruchu w kierunku Downlink system zwiększał też licznik ruchu uplink, co było niezgodne z założeniami.
- **Przyczyna:** W `epc/traffic.py` pętla symulacji inkrementowała jednocześnie `bytes_tx` i `bytes_rx`.
- **Naprawa:** Pozostawiono inkrementację tylko dla licznika DL (`bytes_rx`), usunięto zwiększanie licznika UL.
- **Efekt:** W trybie DL-only licznik UL pozostaje rowny `0`.

### 2) Akceptowanie ujemnej przepustowosci w starcie transferu
- **Problem:** Zadanie typu `{"protocol":"tcp","Mbps":-40}` było akceptowane, mimo że ujemna przepustowość jest niemożliwa.
- **Przyczyna:** Brak walidacji zakresu dla pól `Mbps`, `kbps` i `bps`.
- **Naprawa:** Dodano walidację `>= 0` dla pól `Mbps`, `kbps` i `bps` w `epc/models.py` oraz poprawiono warunek startu ruchu w `epc/traffic.py`, aby `0` było traktowane jako poprawna wartość.
- **Efekt:** Wartości ujemne są odrzucane kodem `422`, a wartość `0` jest poprawnie akceptowana.

### 3) Brak ograniczenia maksymalnej przepustowosci DL (100 Mbps)
- **Problem:** Zadanie uruchomienia transferu z prędkością `180 Mbps` było akceptowane kodem `200`, mimo limitu z dokumentacji.
- **Przyczyna:** Brak walidacji górnego limitu przepustowości w `StartTrafficRequest`.
- **Naprawa:** Dodano walidację maksymalnej wartości `100 Mbps` (tj. `100_000_000 bps`) po przeliczeniu jednostek w `epc/models.py`.
- **Efekt:** Zadania powyżej `100 Mbps` są odrzucane kodem `422`.

### 4) Odczyt statystyk dla bearera nienależącego do UE zwracał zera zamiast błędu
- **Problem:** Zapytanie o statystyki dla bearera, który nie należał do wskazanego UE, zwracało odpowiedź `200` z zerowymi statystykami.
- **Przyczyna:** Endpoint `GET /ues/{ue_id}/bearers/{bearer_id}/traffic` sprawdzał tylko istnienie wpisu w `stats`, bez weryfikacji, czy bearer istnieje w `state.bearers`.
- **Naprawa:** Dodano jawną walidację przynależności bearera do UE i zwracanie błędu `400` (`"Bearer not found"`), gdy bearer nie istnieje.
- **Efekt:** Odczyt statystyk dla obcego/nieistniejącego bearera jest poprawnie odrzucany błędem.

### 5) Brak endpointu zatrzymującego ruch globalnie (`DELETE /ues/traffic`)
- **Problem:** Wywołanie `DELETE /ues/traffic` nie zatrzymywało ruchu na wszystkich UE (w praktyce route trafiał w `/ues/{ue_id}` i kończył się `422`, albo brakowało realnego zatrzymania tasków).
- **Przyczyna:** Brak dedykowanego endpointu `DELETE /ues/traffic` (oraz konieczność zadeklarowania go przed `/ues/{ue_id}`, żeby nie był interpretowany jako parametr ścieżki).
- **Naprawa:** Dodano `DELETE /ues/traffic`, który wywołuje `tm.stop_all()` oraz ustawia `active=False` na wszystkich bearerach we wszystkich UE; route umieszczono przed `/ues/{ue_id}`.
- **Efekt:** Ruch jest zatrzymywany globalnie, a stan bearerów w bazie jest spójny.

### 6) Brak obsługi `DELETE /ues/{ue_id}/traffic` bez parametru `bearer_id`
- **Problem:** Zapytanie `DELETE /ues/{id}/traffic` bez podania `bearer_id` zwracało `404`, bo endpoint nie istniał.
- **Przyczyna:** W implementacji API był tylko stop dla konkretnego bearera (`DELETE /ues/{ue_id}/bearers/{bearer_id}/traffic`) oraz stop globalny (`DELETE /ues/traffic`).
- **Naprawa:** Dodano endpoint `DELETE /ues/{ue_id}/traffic`, który (gdy `bearer_id` nie jest podany) zatrzymuje ruch dla wszystkich bearerów w danym UE (wywołuje `tm.stop_ue(ue_id)` oraz ustawia `active=False` dla wszystkich bearerów w UE).

### 7) Brak obsługi `GET /ues/{ue_id}/traffic` (statystyki sumaryczne UE) bez opcjonalnych parametrów
- **Problem:** Zapytanie `GET /ues/{id}/traffic` bez parametrów `bearer_id` i `unit` zwracało `404`.
- **Przyczyna:** Brak endpointu zwracającego sumaryczne statystyki dla UE; istniał tylko odczyt per bearer (`GET /ues/{ue_id}/bearers/{bearer_id}/traffic`) oraz agregacja globalna (`GET /ues/stats`).
- **Naprawa:** Dodano `GET /ues/{ue_id}/traffic`, który zwraca sumaryczne statystyki dla UE (domyślnie w `kbps`) oraz opcjonalnie obsługuje query parametry `bearer_id` i `unit`.

### 8) Zawyżone statystyki w pierwszych sekundach ruchu (tzw. „Traffic Burst”)
- **Problem:** Trzy scenariusze (jednostki jednolite, jednostki mieszane i protokoły mieszane TCP/UDP) raportowały zawyżony ruch po ~2 sekundach od startu transferu.
- **Przyczyna:** W `epc/traffic.py` pierwszy przyrost bajtów był zapisywany natychmiast po uruchomieniu taska, jeszcze przed pierwszym interwałem, co zawyżało wynik `*_bps` przy krótkim czasie obserwacji.
- **Naprawa:** Zmieniono algorytm generatora ruchu: najpierw `sleep(interval)`, a następnie dopisywanie bajtów proporcjonalnie do rzeczywistego czasu (`dt`) między kolejnymi aktualizacjami.
- **Efekt:** Znika początkowy pik; agregacja ruchu dla krótkich okien czasowych jest zgodna z zadanym limitem i poprawna niezależnie od protokołu (`tcp`/`udp`) oraz jednostki (`Mbps`/`kbps`/`bps`).
