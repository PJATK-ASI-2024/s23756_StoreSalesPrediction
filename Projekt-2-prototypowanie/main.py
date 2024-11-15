# Importowanie bibliotek
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_absolute_error, classification_report
from sklearn.ensemble import ExtraTreesClassifier
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

# Generowanie raportu EDA za pomocą Pandas Profiling
print("\nGenerowanie raportu EDA...")
profile = ProfileReport(data, title="Raport Profilowania Danych", explorative=True)
profile.to_file("raport_eda.html")

# Wizualizacje rozkładów zmiennych numerycznych
print("\nTworzenie histogramów dla zmiennych numerycznych...")
data.hist(bins=20, figsize=(14, 8))
plt.suptitle("Histogramy zmiennych numerycznych")
plt.show()

# Macierz korelacji
print("\nTworzenie macierzy korelacji...")
numeric_data = data.select_dtypes(include=['float64', 'int64'])
plt.figure(figsize=(12, 9))
sns.heatmap(numeric_data.corr(), annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title("Macierz korelacji zmiennych numerycznych")
plt.show()

# Przetwarzanie danych
print("\nPrzetwarzanie danych...")
# Usuwanie kolumn z nadmierną ilością brakujących danych
threshold_missing = 0.5 * len(data)
columns_to_remove = missing_values[missing_values > threshold_missing].index.tolist()
cleaned_data = data.drop(columns=columns_to_remove)

# Uzupełnianie brakujących wartości za pomocą mediany
numerical_columns = cleaned_data.select_dtypes(include=['float64', 'int64']).columns
cleaned_data[numerical_columns] = cleaned_data[numerical_columns].fillna(cleaned_data[numerical_columns].median())

# Kodowanie zmiennych kategorycznych
categorical_columns = cleaned_data.select_dtypes(include=['object']).columns
encoded_data = pd.get_dummies(cleaned_data, columns=categorical_columns, drop_first=True)

# Podział na dane treningowe i testowe
print("\nDostępne kolumny po kodowaniu zmiennych:")
print(encoded_data.columns.tolist())
target = 'target_column'

X = encoded_data.drop(target, axis=1)
y = encoded_data[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

# Modelowanie za pomocą TPOT
print("\nAutomatyczne modelowanie za pomocą TPOT...")
tpot = TPOTClassifier(generations=10, population_size=50, verbosity=2, random_state=42, n_jobs=-1)
tpot.fit(X_train, y_train)

print("\nNajlepszy model znaleziony przez TPOT:")
print(tpot.fitted_pipeline_)
tpot.export("tpot_best_model.py")

# Ewaluacja najlepszego modelu TPOT
y_pred = tpot.predict(X_test)
print("\nDokładność modelu TPOT:", accuracy_score(y_test, y_pred))
print("\nRaport klasyfikacji TPOT:\n", classification_report(y_test, y_pred))

# Ręczne modelowanie z ExtraTreesClassifier
print("\nTrenowanie modelu ExtraTreesClassifier...")
extratrees = ExtraTreesClassifier(
    criterion='gini',
    max_features=0.5,
    min_samples_leaf=5,
    min_samples_split=5,
    n_estimators=200,
    random_state=42
)
extratrees.fit(X_train, y_train)

# Ewaluacja modelu ExtraTreesClassifier
y_pred_extratrees = extratrees.predict(X_test)
print("\nDokładność modelu ExtraTreesClassifier:", accuracy_score(y_test, y_pred_extratrees))
print("\nRaport klasyfikacji ExtraTreesClassifier:\n", classification_report(y_test, y_pred_extratrees))

# Zapis wyników do pliku
with open("results.txt", "w") as file:
    file.write(f"Dokładność TPOT: {accuracy_score(y_test, y_pred)}\n")
    file.write(f"Dokładność ExtraTreesClassifier: {accuracy_score(y_test, y_pred_extratrees)}\n")
    file.write(f"Raport klasyfikacji TPOT:\n{classification_report(y_test, y_pred)}\n")
    file.write(f"Raport klasyfikacji ExtraTreesClassifier:\n{classification_report(y_test, y_pred_extratrees)}\n")
