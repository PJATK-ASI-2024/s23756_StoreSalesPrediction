import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_absolute_error
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from tpot import TPOTClassifier
from ydata_profiling import ProfileReport

# Wczytanie danych
data_path = 'C://Users//Michal//Desktop//train.csv'
data = pd.read_csv(data_path)

# Podstawowa analiza danych
print("Informacje o danych:")
print(data.info())
print("\nStatystyki opisowe danych:")
print(data.describe())

# Sprawdzanie brakujących danych
missing_values = data.isnull().sum()
print("\nBrakujące dane w poszczególnych kolumnach:\n", missing_values)

# Zamiana wartości tekstowych na NaN w kolumnach numerycznych
for column in data.select_dtypes(include=['float64', 'int64']).columns:
    data[column] = pd.to_numeric(data[column], errors='coerce')

# Wizualizacja rozkładów zmiennych numerycznych
print("\nTworzenie histogramów dla zmiennych numerycznych...")
data.hist(bins=20, figsize=(14, 8))
plt.suptitle("Histogramy zmiennych numerycznych")
plt.show()

# Wykresy pudełkowe dla zmiennych numerycznych
print("\nWykresy pudełkowe dla zmiennych numerycznych...")
for column in data.select_dtypes(include=['float64', 'int64']).columns:
    plt.figure(figsize=(8, 6))
    sns.boxplot(data[column])
    plt.title(f"Wykres pudełkowy dla {column}")
    plt.show()

# Macierz korelacji
print("\nTworzenie macierzy korelacji...")
numeric_data = data.select_dtypes(include=['float64', 'int64'])
plt.figure(figsize=(12, 9))
sns.heatmap(numeric_data.corr(), annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title("Macierz korelacji zmiennych numerycznych")
plt.show()

# Generowanie raportu EDA
print("\nGenerowanie raportu EDA...")
profile_report = ProfileReport(data, title="Raport Profilowania Danych", explorative=True)
profile_report.to_file("raport_eda.html")

# Usuwanie kolumn z nadmierną ilością brakujących danych
threshold_missing = 0.5 * len(data)
columns_to_remove = missing_values[missing_values > threshold_missing].index.tolist()
columns_to_remove.append('Name')  # Dodatkowe usunięcie kolumny 'Name'
cleaned_data = data.drop(columns=columns_to_remove)

# Uzupełnianie brakujących wartości za pomocą mediany
numerical_columns = cleaned_data.select_dtypes(include=['float64', 'int64']).columns
cleaned_data[numerical_columns] = cleaned_data[numerical_columns].fillna(cleaned_data[numerical_columns].median())

# Usunięcie kolumn związanych z imionami
name_related_columns = [col for col in cleaned_data.columns if 'Name_' in col]
cleaned_data = cleaned_data.drop(columns=name_related_columns)

# Kodowanie zmiennych kategorycznych
categorical_columns = cleaned_data.select_dtypes(include=['object']).columns
encoded_data = pd.get_dummies(cleaned_data, columns=categorical_columns, drop_first=True)

# Podział na dane treningowe i testowe
print("Dostępne kolumny po kodowaniu zmiennych:")
print(encoded_data.columns.tolist())

# Wybór zmiennej docelowej
target = 'Have you ever had suicidal thoughts ?_Yes'

X = encoded_data.drop(target, axis=1)  # Zmienne wejściowe
y = encoded_data[target]  # Zmienna docelowa

# Podział na zbiór treningowy i testowy
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

# Automatyczne modelowanie za pomocą TPOT
print("\nUruchomienie automatycznego modelowania z TPOT...")
tpot_classifier = TPOTClassifier(generations=20, population_size=100, verbosity=3, random_state=42, n_jobs=-1)
tpot_classifier.fit(X_train, y_train)

print("Najlepsza struktura pipeline znalezionego przez TPOT: ", tpot_classifier.fitted_pipeline_)
tpot_classifier.export("tpot_best_model.py")

# Trenowanie modelu ExtraTreesClassifier
print("\nTrenowanie modelu ExtraTreesClassifier...")
extratrees_model = ExtraTreesClassifier(
    criterion='gini',
    max_features=0.5,
    min_samples_leaf=5,
    min_samples_split=5,
    n_estimators=200,
    random_state=42
)
extratrees_model.fit(X_train, y_train)

# Ocena modelu
print("\nOcena modelu...")
y_pred = extratrees_model.predict(X_test)

# Przekształcenie wartości logicznych na liczby całkowite
if y_test.dtype == 'bool':
    y_test = y_test.astype(int)
if y_pred.dtype == 'bool':
    y_pred = y_pred.astype(int)

# Obliczenie dokładności i średniego błędu bezwzględnego
accuracy = accuracy_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)

print(f"Dokładność modelu: {accuracy}")
print(f"Średni błąd bezwzględny: {mae}")

# Zapisanie wyników do pliku
with open("model_results.txt", "w") as result_file:
    result_file.write(f"Dokładność: {accuracy}\n")
    result_file.write(f"Średni błąd bezwzględny: {mae}\n")
