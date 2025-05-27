import React, { useState } from 'react';
import { View, Text, TextInput, Button, Alert, StyleSheet } from 'react-native';

export default function RegistroScreen({ onRegister }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const register = () => {
    fetch('http://192.168.1.10:8000/api/registro/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    })
      .then(res => res.json())
      .then(data => {
        if (data.token) {
          Alert.alert('Registro exitoso', '¡Ya puedes iniciar sesión!');
          onRegister();
        } else {
          Alert.alert('Error', data.error || 'No se pudo registrar');
        }
      })
      .catch(() => Alert.alert('Error', 'No se pudo conectar con el servidor.'));
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Registro</Text>
      <TextInput style={styles.input} placeholder="Usuario" value={username} onChangeText={setUsername} />
      <TextInput style={styles.input} placeholder="Contraseña" value={password} onChangeText={setPassword} secureTextEntry />
      <Button title="Registrarse" color="#2ed8b6" onPress={register} />
      <Button title="Volver" color="#888" onPress={onRegister} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 24, backgroundColor: '#fff' },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 24, color: '#2ed8b6', textAlign: 'center' },
  input: { borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 12, marginBottom: 16 }
});