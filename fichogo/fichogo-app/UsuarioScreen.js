import React, { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator, Alert } from 'react-native';
import { API_BASE_URL } from './config';
import { API_BASE_URL } from './config';

export default function UsuarioScreen({ token }) {
  const [usuario, setUsuario] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/usuario/`, {
      headers: { 'Authorization': `Token ${token}` }
    })
      .then(res => {
        if (!res.ok) throw new Error('Error al obtener usuario');
        return res.json();
      })
      .then(data => {
        setUsuario(data);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
        Alert.alert('Error', 'No se pudo cargar la información del usuario');
      });
  }, []);

  if (loading) return <ActivityIndicator color="#2ed8b6" style={{ marginTop: 32 }} />;
  if (!usuario) return <Text>No se encontró información del usuario.</Text>;

  return (
    <View style={{ padding: 24 }}>
      <Text style={{ fontSize: 20, fontWeight: 'bold' }}>Usuario: {usuario.username}</Text>
      <Text>Email: {usuario.email}</Text>
    </View>
  );
}