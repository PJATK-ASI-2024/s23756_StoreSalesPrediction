import pandas as pd
from sklearn.model_selection import train_test_split

# Wczytaj plik
file_path = '/mnt/data/train.csv'
data = pd.read_csv(file_path)

# Podziel dane na 70% (trening) i 30% (doszkalanie)
train_data, retrain_data = train_test_split(data, test_size=0.3, random_state=42)

# Zapisz wyniki do plików
train_data.to_csv('/mnt/data/train_data.csv', index=False)
retrain_data.to_csv('/mnt/data/retrain_data.csv', index=False)

print("Podział danych zakończony. Pliki zapisane jako 'train_data.csv' i 'retrain_data.csv'.")