import React, { useState } from 'react';
import { View, Text, TextInput, Button, Alert, StyleSheet } from 'react-native';
import { API_BASE_URL } from './config';

export default function LoginScreen({ onLogin, onShowRegister }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const login = () => {
    fetch(`${API_BASE_URL}/api/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    })
      .then(res => res.json())
      .then(data => {
        if (data.token) {
          onLogin(data.token, username); // Pasa el token y el usuario al App.js
        } else {
          Alert.alert('Error', data.non_field_errors ? data.non_field_errors[0] : 'Credenciales incorrectas');
        }
      })
      .catch(() => Alert.alert('Error', 'No se pudo conectar con el servidor.'));
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Iniciar Sesión</Text>
      <TextInput style={styles.input} placeholder="Usuario" value={username} onChangeText={setUsername} />
      <TextInput style={styles.input} placeholder="Contraseña" value={password} onChangeText={setPassword} secureTextEntry />
      <Button title="Ingresar" color="#2ed8b6" onPress={login} />
      <Button title="Registrarse" color="#888" onPress={onShowRegister} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 24, backgroundColor: '#fff' },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 24, color: '#2ed8b6', textAlign: 'center' },
  input: { borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 12, marginBottom: 16 }
});