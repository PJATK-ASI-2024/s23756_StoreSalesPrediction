import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error
import pickle

# Wczytaj dane
data = pd.read_csv('data.csv')

# Usuwanie zbędnych kolumn
columns_to_drop = ['Order ID', 'Customer Name', 'Product Name', 'Customer ID', 'Order Date', 'Ship Date']
data.drop(columns=columns_to_drop, inplace=True)

# Wypełnianie braków danych w 'Postal Code'
data['Postal Code'].fillna(data['Postal Code'].mode()[0], inplace=True)

# Zakodowanie zmiennych kategorycznych
label_encoders = {}
for column in data.select_dtypes(include=['object']).columns:
    le = LabelEncoder()
    data[column] = le.fit_transform(data[column])
    label_encoders[column] = le

# Przygotowanie cech (X) i celu (y)
X = data.drop(columns=['Sales'])
y = data['Sales']

# Podział na dane treningowe i testowe
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Trening modelu
model = RandomForestRegressor(random_state=42, n_estimators=100)
model.fit(X_train, y_train)

# Predykcja i ocena modelu
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f"Średni błąd absolutny (MAE): {mae:.2f}")

# Zapis modelu do pliku
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)
print("Model zapisano jako model.pkl")
