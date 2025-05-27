import React, { useState, useRef } from 'react';
import { View, Text, TextInput, Button, Alert, StyleSheet, TouchableOpacity } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { API_BASE_URL } from './config';

let scanningLock = false; // <-- variable global fuera del componente

export default function ValidarFichoScreen({ token }) {
  const [codigo, setCodigo] = useState('');
  const [permission, requestPermission] = useCameraPermissions();
  const [scanning, setScanning] = useState(false);
  const [facing, setFacing] = useState('back');
  const cameraRef = useRef(null);

  // Solo permite un escaneo por vez
  const handleBarCodeScanned = ({ type, data }) => {
    if (scanningLock) return; // Bloquea si ya está escaneando
    scanningLock = true;
    setScanning(false);

    // Acepta solo números o extrae el último número de un string
    const match = data.match(/(\d+)$/);
    if (match) {
      const fichoId = match[1];
      setCodigo(fichoId);
      validarFicho(fichoId);
    } else {
      Alert.alert('Error', 'El QR no contiene un ID válido');
      scanningLock = false; // Libera si hubo error
    }
  };

  const validarFicho = (codigoValidar = codigo) => {
    fetch(`${API_BASE_URL}/api/validar-ficho/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ codigo: codigoValidar })
    })
      .then(res => res.json())
      .then(data => {
        if (data.valido) {
          if (data.usado) {
            Alert.alert('Atención', 'Este ficho ya fue usado');
          } else {
            Alert.alert('Éxito', 'Ficho validado y marcado como usado');
          }
        } else {
          Alert.alert('Error', data.detail || 'Ficho no válido');
        }
        scanningLock = false; // Libera después de mostrar alerta
      })
      .catch(() => {
        Alert.alert('Error', 'No se pudo validar el ficho');
        scanningLock = false; // Libera en caso de error
      });
  };

  if (!permission) return <View />;
  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text style={{ textAlign: 'center' }}>Necesitamos permiso para acceder a la cámara</Text>
        <Button onPress={requestPermission} title="Conceder permiso" />
      </View>
    );
  }

  if (scanning) {
    return (
      <View style={{ flex: 1 }}>
        <CameraView
          style={{ flex: 1 }}
          facing={facing}
          onBarcodeScanned={handleBarCodeScanned}
          barcodeScannerSettings={{
            barcodeTypes: ['qr'],
          }}
          ref={cameraRef}
        >
          <View style={styles.buttonContainer}>
            <TouchableOpacity style={styles.button} onPress={() => setScanning(false)}>
              <Text style={styles.text}>Cancelar</Text>
            </TouchableOpacity>
          </View>
        </CameraView>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.label}>Código de Ficho:</Text>
      <TextInput
        style={styles.input}
        value={codigo}
        onChangeText={setCodigo}
        placeholder="Ingresa el código"
        keyboardType="numeric"
      />
      <Button title="Validar" onPress={() => validarFicho()} />
      <View style={{ height: 16 }} />
      <Button title="Escanear QR" onPress={() => setScanning(true)} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff'
  },
  label: {
    fontSize: 18,
    marginBottom: 8
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 8,
    width: 220,
    marginBottom: 16
  },
  buttonContainer: {
    flex: 1,
    justifyContent: 'flex-end',
    marginBottom: 30,
    alignItems: 'center',
  },
  button: {
    backgroundColor: '#000',
    padding: 12,
    borderRadius: 8,
  },
  text: {
    color: '#fff',
    fontSize: 18,
  },
});
