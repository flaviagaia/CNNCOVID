# -*- coding: utf-8 -*-
"""CNN_COVID_NOTEBOOK_hiper.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IdmxiKdYkjC7fB60AGM795YMAWPsttxI

# CNN

Este código é uma implementação completa de uma Rede Neural Convolucional (CNN) para classificar imagens em duas categorias: "Normal" e "Covid". Ele foi projetado para ser executado no ambiente do Google Colab e utiliza diversas bibliotecas Python, como TensorFlow, NumPy e Matplotlib.
"""

# Bibliotecas:
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from sklearn.metrics import roc_auc_score, confusion_matrix, roc_curve, classification_report
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.preprocessing import image
from tensorflow.keras.callbacks import TensorBoard
import datetime

# Montar Google Drive:
from google.colab import drive
drive.mount('/content/drive')

# Definindo os caminhos:
train_dir = '/content/drive/MyDrive/CNN_COVID/Data/train'
test_dir = '/content/drive/MyDrive/CNN_COVID/Data/test'

# Tensorboard:
log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
tensorboard_callback = TensorBoard(log_dir=log_dir, histogram_freq=1)

# Verificar a existência dos diretórios de dados:

if not os.path.exists(train_dir):
    raise FileNotFoundError(f"O diretório de treinamento não foi encontrado: {train_dir}")
if not os.path.exists(test_dir):
    raise FileNotFoundError(f"O diretório de teste não foi encontrado: {test_dir}")

# Se os diretórios existirem, o código prossegue normalmente.

# Inicialização da CNN:
classifier = tf.keras.Sequential([ #criando o modelo sequencial
    tf.keras.layers.Conv2D(32, 3, padding="same", input_shape=(64, 64, 3), activation='relu'), #primeira camada convolucional
    tf.keras.layers.MaxPooling2D(), #primeira camada de pooling
    tf.keras.layers.Conv2D(64, 3, padding="same", activation="relu"), #camada convolucionalcom 64 filtros
    tf.keras.layers.MaxPooling2D(),  #camada de pooling com um tamanho de janela 2x2
    tf.keras.layers.Flatten(), #camada de achatamento
    tf.keras.layers.Dense(128, activation='relu'), #camada densa com 128 neurônios
    tf.keras.layers.Dense(1, activation='sigmoid') #camada de saída
])
# Compilando o modelo:
classifier.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
classifier.summary()

# Fitting da CNN às imagens:
train_datagen = ImageDataGenerator(
    rescale=1./255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
)

test_datagen = ImageDataGenerator(rescale=1./255)

training_set = train_datagen.flow_from_directory(
    train_dir,
    target_size=(64, 64),
    batch_size=32,
    class_mode='binary'
)

test_set = test_datagen.flow_from_directory(
    test_dir,
    target_size=(64, 64),
    batch_size=32,
    class_mode='binary'
)

# Treinamento:
history = classifier.fit(
    training_set,
    steps_per_epoch=4,
    epochs=10,
    validation_data=test_set,
    validation_steps=4,
    callbacks=[tensorboard_callback]
)

# Salvando o modelo:
classifier.save('/content/drive/MyDrive/CNN_COVID/meu_modelo.h5')

# Avaliação do modelo carregado:
loaded_model = tf.keras.models.load_model('/content/drive/MyDrive/CNN_COVID/meu_modelo.h5')
loaded_model.evaluate(test_set)

# Predições:
y_pred = []
y_test = []
import os

for i in os.listdir("/content/drive/MyDrive/CNN_COVID/Data/test/Normal"):
    img = image.load_img("/content/drive/MyDrive/CNN_COVID/Data/test/Normal/" + i, target_size=(64, 64))
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    p = classifier.predict(img)
    y_test.append(p[0, 0])
    y_pred.append(1)

for i in os.listdir("/content/drive/MyDrive/CNN_COVID/Data/test/Covid"):
    img = image.load_img("/content/drive/MyDrive/CNN_COVID/Data/test/Covid/" + i, target_size=(64, 64))
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    p = classifier.predict(img)
    y_test.append(p[0, 0])
    y_pred.append(0)

y_pred = np.array(y_pred)
y_test = np.array(y_test)

# Calculando a matriz de confusão:
cm = confusion_matrix(y_test.round(), y_pred)

# Calculando sensibilidade e especificidade:
true_positive = cm[0][0]
false_positive = cm[0][1]
true_negative = cm[1][1]
false_negative = cm[1][0]

sensitivity = true_positive / (true_positive + false_negative)
specificity = true_negative / (true_negative + false_positive)

print(f'Sensibilidade (Recall): {sensitivity}')
print(f'Especificidade: {specificity}')

plt.figure(figsize=(5,5))
sns.heatmap(cm, annot=True, fmt=".0f", linewidths=.5, square=True, cmap='Blues')
plt.ylabel('Label Verdadeiro')
plt.xlabel('Label Previsto')
plt.title('Matriz de Confusão', size=15)

# Grafico de acurácia:
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Acurácia do Modelo')
plt.ylabel('Acurácia')
plt.xlabel('Época')
plt.legend(['Treino', 'Teste'], loc='upper left')
plt.show()

# Gráfico de perda:
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Perda do Modelo')
plt.ylabel('Perda')
plt.xlabel('Época')
plt.legend(['Treino', 'Teste'], loc='upper left')
plt.show()

# Calcular a AUC-ROC
auc_roc = roc_auc_score(y_test.round(), y_pred)
print(f'AUC-ROC: {auc_roc}')

# Calcular a curva ROC
fpr, tpr, _ = roc_curve(y_test.round(), y_pred)

# Plotar a curva ROC
plt.figure()
plt.plot(fpr, tpr, label='ROC curve (area = %0.2f)' % auc_roc)
plt.plot([0, 1], [0, 1], 'k--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('Taxa de Falsos Positivos')
plt.ylabel('Taxa de Verdadeiros Positivos')
plt.title('Curva ROC')
plt.legend(loc="lower right")
plt.show()

# Cálculo da sensibilidade e especificidade com base na matriz de confusão
true_positive = cm[0][0]
false_positive = cm[0][1]
true_negative = cm[1][1]
false_negative = cm[1][0]

sensitivity = true_positive / (true_positive + false_negative)
specificity = true_negative / (true_negative + false_positive)

print(f'Sensibilidade (Recall): {sensitivity}')
print(f'Especificidade: {specificity}')

# Histograma das previsões pode mostrar se o modelo está incerto sobre certas classificações
plt.figure(figsize=(10, 5))
plt.hist(y_pred, bins=30, label='Previsões do Modelo', color='blue')
plt.xlabel('Probabilidade Prevista de Ser Classe Positiva')
plt.ylabel('Frequência')
plt.title('Distribuição das Previsões do Modelo')
plt.legend()
plt.show()

# Gráfico de Métricas por Época
plt.plot(history.history['accuracy'], label='Acurácia no Treino')
plt.plot(history.history['val_accuracy'], label='Acurácia na Validação')
plt.xlabel('Época')
plt.ylabel('Acurácia')
plt.title('Acurácia por Época')
plt.legend()
plt.show()

# Impressão do relatório de classificação:
print(classification_report(y_pred, y_test.round()))

# Commented out IPython magic to ensure Python compatibility.
# Tensorboard:
# %load_ext tensorboard
# %tensorboard --logdir logs/fit