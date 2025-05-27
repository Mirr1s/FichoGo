import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet, Image, ActivityIndicator } from 'react-native';
import { API_BASE_URL } from './config';

export default function HistorialScreen({ token }) {
  const [fichos, setFichos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/historial-hoy/`, {
      headers: { 'Authorization': `Token ${token}` }
    })
      .then(res => res.json())
      .then(data => {
        setFichos(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const renderFicho = ({ item }) => (
    <View style={styles.card}>
      <Text style={styles.estado}>Estado: {item.estado}</Text>
      <Text style={styles.info}>Fecha: {item.fecha_solicitud?.slice(0, 10)}</Text>
      <Text style={styles.info}>Hora: {item.hora}</Text>
      <Text style={styles.info}>Servicio: {item.cupo_nombre_servicio}</Text>
      {item.codigo_qr ? (
        <Image
          source={{ uri: item.codigo_qr }}
          style={styles.qr}
          resizeMode="contain"
        />
      ) : (
        <Text style={styles.noqr}>QR no disponible</Text>
      )}
    </View>
  );

  if (loading) return <ActivityIndicator color="#2ed8b6" style={{ marginTop: 32 }} />;

  return (
    <FlatList
      data={fichos}
      keyExtractor={item => item.id.toString()}
      renderItem={renderFicho}
      contentContainerStyle={{ alignItems: 'center', paddingBottom: 32 }}
      ListEmptyComponent={<Text style={styles.noqr}>No tienes fichos en tu historial.</Text>}
    />
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    marginVertical: 10,
    alignItems: 'center',
    width: 320,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 4,
  },
  estado: {
    fontWeight: 'bold',
    color: '#2ed8b6',
    marginBottom: 4,
    fontSize: 16,
  },
  info: {
    fontSize: 15,
    color: '#444',
    marginBottom: 2,
  },
  qr: {
    width: 120,
    height: 120,
    marginTop: 12,
    marginBottom: 8,
  },
  noqr: {
    color: '#aaa',
    fontStyle: 'italic',
    marginTop: 12,
  },
});