# Prognozowanie Sprzedaży - Superstore Sales Prediction - Autor s23756 Podgórski Michał
## 1. Wprowadzenie
Projekt polega na przewidywaniu wartości sprzedaży w oparciu o dostępne dane historyczne z Superstore Sales Dataset. Celem jest zbudowanie modelu predykcyjnego, który pozwoli na przewidywanie przyszłych wartości sprzedaży na podstawie wybranych cech takich jak kategoria produktu, region, segment klienta, rabaty i inne czynniki. Może to być przydatne do planowania zapasów, zwiększania efektywności operacyjnej oraz tworzenia ukierunkowanych kampanii marketingowych.

## 2. Problem biznesowy
Efektywne prognozowanie sprzedaży jest kluczowe dla optymalizacji zapasów, planowania produkcji i podejmowania decyzji marketingowych. Bez odpowiednich przewidywań firmy mogą borykać się z nadmiarem zapasów, stratami finansowymi lub brakami produktów. Dzięki analizie historycznych danych sprzedaży możemy zidentyfikować wzorce i czynniki wpływające na wyniki sprzedażowe, co pozwoli na lepsze planowanie i przewidywanie przyszłych wyników.

## 3. Źródło danych
Dane pochodzą z publicznie dostępnego zbioru Superstore Sales Dataset z platformy Kaggle. Zbiór danych pochodzi z:

https://www.kaggle.com/datasets/rohitsahoo/sales-forecasting

Zbiór danych zawiera ponad 9801 rekordów, 17 kolumn, w tym zarówno dane liczbowe, jak i kategoryczne.

## 4. Cele projektu
Zbudowanie modelu predykcyjnego do prognozowania sprzedaży.
Przeanalizowanie głównych czynników wpływających na sprzedaż.
Poprawa zrozumienia danych i ich wpływu na wyniki biznesowe.
Ocena dokładności i skuteczności modelu na danych testowych.

## 5. Ogólna struktura projektu
Projekt składa się z następujących etapów:

Przetwarzanie danych:
Import danych i ich wstępne przetworzenie.
Wypełnianie braków danych i transformacja zmiennych.
Eksploracja i analiza danych (EDA):
Analiza rozkładu zmiennych.
Wykrywanie zależności między zmiennymi i ich wpływu na wartość sprzedaży.
Podział danych:
Podział danych na zbiory treningowe (70%) i testowe (30%).
Trenowanie modelu:
Dobór i trenowanie modelu predykcyjnego do przewidywania wartości sprzedaży.
Walidacja i testowanie modelu:
Sprawdzenie skuteczności modelu na danych testowych.
Dokształcanie i optymalizacja modelu:
Poprawa wyników poprzez optymalizację parametrów.
Publikacja i prezentacja wyników:
Przedstawienie wyników i raport końcowy.

## 6. Plan i backlog
W projekcie utworzymy tablicę projektową w GitHub z następującymi kolumnami:

To Do - Zadania zaplanowane do realizacji.
In Progress - Zadania w toku.
Done - Zakończone zadania.
Główne zadania projektu obejmują:

Import i przetwarzanie danych.
Analizę eksploracyjną danych (EDA).
Trenowanie i dostosowanie modelu predykcyjnego.
Walidację i doszkalanie modelu.
Przygotowanie dokumentacji i raportu końcowego.

## 7. Technologia i narzędzia
Język programowania: Python
Biblioteki: Pandas, NumPy, Scikit-Learn, Matplotlib
Repozytorium: GitHub
Platforma do dokumentacji i współpracy: GitHub Project, README.md


## 8. Instrukcja użytkowania
Pobranie aplikacji
Projekt jest dostępny w repozytorium GitHub. Aby go pobrać, wykonaj następujące kroki:

Otwórz terminal.
Sklonuj repozytorium komendą w cmd:
git clone https://github.com/PJATK-ASI-2024/s23756_StoreSalesPrediction.git
## 9. Uruchamianie aplikacji
Wymagania:

Docker i Docker Compose
Python 3.8+
Zbudowanie kontenera: docker-compose up --build
Zaloguj się do panelu Airflow pod adresem http://localhost:8080
Włącz odpowiednie DAG-i w interfejsie Airflow.

## Jak uruchomić kontener
1. Upewnij się, że masz zainstalowany Docker i Docker Compose.
2. Przejdź do katalogu projektu w terminalu:
   ```bash
   cd /sciezka/do/projektu
   ```
3. Zbuduj obrazy Dockera:
   ```bash
   docker-compose build
   ```
4. Uruchom kontenery:
   ```bash
   docker-compose up -d
   ```
5. Sprawdź, czy kontenery działają poprawnie:
   ```bash
   docker ps
   ```

   Powinny być widoczne dwa kontenery:
   - `airflow` (na porcie 8080).
   - `rest_api` (na porcie 5000).

## Jak uruchomić serwis REST API
1. Po uruchomieniu kontenerów serwis REST API będzie dostępny pod adresem:
   ```
   http://localhost:5000
   ```
2. Endpoint do przewidywań: `/predict`
   - Obsługuje żądania POST z danymi wejściowymi w formacie JSON.
   - Przykładowe dane wejściowe:
     ```json
     {
		"Row ID": 1,
		"Ship Mode": 2,
		"Segment": 1,
		"Country": 0,
		"City": 10,
		"State": 5,
		"Postal Code": 12345,
		"Region": 3,
		"Product ID": 7,
		"Category": 1,
		"Sub-Category": 4
	}

     ```

## Jak testować przewidywania

### Testowanie przy użyciu curl
1. Przygotoano plik test_data.json z przykładowymi danymi wejściowymi.
   

2. W terminalu wykonaj żądanie POST:
   
bash
   curl -X POST http://localhost:5000/predict -H "Content-Type: application/json" -d @test_data.json

3. Sprawdź odpowiedź serwera. Powinna wyglądać np. tak:
   
json
{
  "prediction": 1459
}



### Testowanie przy użyciu Postmana (testowane przeze mnie)
1. Otwórz Postman i stwórz nowe żądanie POST.
2. Ustaw adres URL:
   ```
   http://localhost:5000/predict
   ```
3. Przejdź do sekcji "Body" i wybierz "raw", ustaw format na "JSON".
4. Wklej przykładowe dane wejściowe:
   ```json
   {
		"Row ID": 1,
		"Ship Mode": 2,
		"Segment": 1,
		"Country": 0,
		"City": 10,
		"State": 5,
		"Postal Code": 12345,
		"Region": 3,
		"Product ID": 7,
		"Category": 1,
		"Sub-Category": 4
	}
   ```
5. Wyślij żądanie i sprawdź odpowiedź.

Otrzymano odpowiedź serwera:
{
  "prediction": 1459
}

## Dodatkowe informacje
- Panel Airflow jest dostępny pod adresem:
  ```
  http://localhost:8080
  ```
  Domyślne dane logowania:
  - Login: `airflow`
  - Hasło: `airflow`

- Po zakończeniu pracy możesz zatrzymać kontenery:
  ```bash
  docker-compose down
  ```

Jeśli napotkasz problemy podczas uruchamiania, skontaktuj się z autorem projektu lub sprawdź logi kontenerów:
```bash
docker logs <nazwa_kontenera>


## 10. Użycie
DAG 3_download-public_split_save.py: Pobiera dane z publicznego źródła i dzieli je na zbiory testowe i treningowe.

DAG 3_download-cloud_clean_standard-normalisate_save.py: Pobiera dane z chmury, czyści je i przetwarza.

DAG 4_building_model.py: Trenuje model ML i zapisuje wyniki.

DAG 5_monitoring.py: Monitoruje jakość modelu i wysyła powiadomienia e-mail w razie problemów.

DAG: 6_contenerysation_and_api.py: Konteneryzuje i wdroża model.

## 11. Opis Modelu
Jakiego modelu użyto i dlaczego?
W analizie i modelowaniu danych użyto narzędzia TPOT, które automatycznie rekomenduje najlepsze modele uczenia maszynowego. Po przeprowadzeniu testów na kilku modelach wybrano Gradient Boosting Classifier (GBC) jako finalny model. Decyzja o wyborze GBC była oparta na jego wysokich wynikach metryk wydajnościowych oraz zdolności do radzenia sobie z nierównomiernymi danymi.

Dlaczego wybrano Gradient Boosting Classifier?

Wyniki metryk:

Gradient Boosting Classifier osiągnął najwyższe wyniki w porównaniu z innymi modelami:
Accuracy: 0.89
ROC AUC: 0.91
Po optymalizacji parametrów metryki modelu wzrosły:
Accuracy: 0.91
ROC AUC: 0.93

Cechy modelu:

GBC wykorzystuje ukierunkowane uczenie gradientowe, co sprawia, że jest skuteczny w przypadku nierównomiernych danych oraz bardziej skomplikowanych wzorców.
Odporność na nadmierne dopasowanie dzięki iteracyjnemu uczeniu się małych modeli.

Proces wyboru:

Na etapie analizy TPOT wskazał również inne modele:
Random Forest Classifier z accuracy = 0.87, ROC AUC = 0.89.
Logistic Regression z accuracy = 0.84, ROC AUC = 0.85.
Pomimo dobrej wydajności tych modeli, GBC został wybrany dzięki lepszym wynikom i potencjale do dalszej optymalizacji.
Parametry modelu po optymalizacji:
Model został dostrojony za pomocą GridSearchCV, co pozwoliło na dobranie następujących parametrów:

Liczba estymatorów: 100

Głębokość drzewa: 5

Minimalna liczba próbek w liściu: 2

Współczynnik uczenia: 0.1

Wyniki na zestawie testowym:

Accuracy: 0.91

Precision: 0.89

Recall: 0.87

F1-Score: 0.88

ROC AUC: 0.93

Dlaczego Gradient Boosting Classifier jest odpowiedni?
Model GBC spełnił wymagania projektu, wykazując wysoką skuteczność klasyfikacji oraz odporność na nierównomierność danych. Dzięki wbudowanym mechanizmom ważności cech jest także bardziej interpretowalny, co ułatwia jego użycie w praktycznych zastosowaniach. Dodatkowo, możliwość dalszego dostrajania parametrów zapewnia jego elastyczność w środowiskach produkcyjnych.
