import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, Alert, Image, Button, TouchableOpacity } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE_URL } from './config';

export default function PerfilScreen({ token, navigation, setToken }) {
  const [usuario, setUsuario] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/usuario/`, {
      headers: { 'Authorization': `Token ${token}` }
    })
      .then(res => res.json())
      .then(data => {
        setUsuario(data);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
        Alert.alert('Error', 'No se pudo cargar el perfil');
      });
  }, []);

  const handleLogout = async () => {
    await AsyncStorage.removeItem('token');
    setToken(null);
    navigation.navigate('Login');
  };

  if (loading) return <ActivityIndicator color="#2ed8b6" style={{ marginTop: 32 }} />;
  if (!usuario) return <Text>No se encontró información del usuario.</Text>;

  return (
    <View style={styles.container}>
      <Image source={require('./assets/profile.png')} style={styles.avatar} />
      <Text style={styles.nombre}>{usuario.username}</Text>
      {usuario.is_admin && (
        <TouchableOpacity
          style={styles.adminBtn}
          onPress={() => navigation.navigate('ValidarFicho')}
        >
          <Text style={styles.adminBtnText}>Validar Fichos (Admin)</Text>
        </TouchableOpacity>
      )}
      <Button title="Cerrar sesión" color="#e74c3c" onPress={handleLogout} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: '#fff' },
  avatar: { width: 100, height: 100, borderRadius: 50, marginBottom: 20 },
  nombre: { fontSize: 22, fontWeight: 'bold', marginBottom: 32, color: '#2ed8b6' },
  adminBtn: { backgroundColor: '#2ed8b6', padding: 12, borderRadius: 8, marginBottom: 24 },
  adminBtnText: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
});