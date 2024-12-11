# Projekt: Konteneryzacja i Wdrożenie Modelu

## Wprowadzenie
Projekt przedstawia proces konteneryzacji i wdrożenia modelu ML jako serwisu REST API. Serwis ładuje wytrenowany model, przyjmuje dane wejściowe w formacie JSON i zwraca przewidywania.
airflow (na porcie 8080),
rest_api (na porcie 5000).

## Struktura projektu
```
projekt-6-Konteneryzacja-i-Wdrozenie-Modelu/
|├── Dockerfile
|├── docker-compose.yml
|├── requirements.txt
|├── app/
|   |├── main.py
|   |└── model.pkl
|├── dags/
|   |└── example_dag.py
|└── test_data.json
|└── screenshots
|└── scripts
|   |└── train_model.py (opcjonalnie do stworzenia model.pkl)
```

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
```

