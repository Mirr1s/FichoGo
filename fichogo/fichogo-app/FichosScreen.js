import React, { useEffect, useState } from 'react';
import { View, Text, Button, ActivityIndicator, StyleSheet, Alert, Modal, TouchableOpacity, Image } from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';
import { API_BASE_URL } from './config';

export default function FichosScreen({ token, username, navigation }) {
  const [usuario, setUsuario] = useState(null);
  const [fichos, setFichos] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [servicios, setServicios] = useState([]);
  const [cupoId, setCupoId] = useState(null);
  const [hora, setHora] = useState(new Date());
  const [showPicker, setShowPicker] = useState(false);
  const [loading, setLoading] = useState(false);

  // Obtener info de usuario (incluye is_admin)
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/usuario/`, {
      headers: { 'Authorization': `Token ${token}` }
    })
      .then(res => res.json())
      .then(data => setUsuario(data))
      .catch(() => setUsuario(null));
  }, [token]);

  useEffect(() => {
    fetchFichos();
    // eslint-disable-next-line
  }, []);

  // 1. Obtener fichos activos
  const fetchFichos = () => {
    fetch(`${API_BASE_URL}/api/fichos/`, {
      headers: {
        'Authorization': `Token ${token}`
      }
    })
      .then(res => res.json())
      .then(data => {
        const activo = data.find(f => f.estado === 'activo');
        setFichos(activo ? [activo] : []);
      })
      .catch(() => {
        Alert.alert('Error', 'No se pudo cargar la información de fichos');
      });
  };

  // 2. Obtener servicios/cupos
  const fetchServicios = () => {
    setServicios([]);
    fetch(`${API_BASE_URL}/api/cupos/`, {
      headers: {
        'Authorization': `Token ${token}`
      }
    })
      .then(res => res.json())
      .then(data => setServicios(data));
  };

  // 3. Solicitar ficho
  const solicitarFicho = () => {
    if (!cupoId || !hora) {
      Alert.alert('Completa todos los campos');
      return;
    }
    setLoading(true);
    // Formatea la hora como "HH:MM"
    const horaStr = hora.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
    console.log('Enviando:', { cupo: cupoId, hora: horaStr }); // <-- Agrega esto
    fetch(`${API_BASE_URL}/api/fichos/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token}`
      },
      body: JSON.stringify({
        cupo: cupoId,
        hora: horaStr
      }),
    })
      .then(async res => {
        setLoading(false);
        let data;
        try {
          data = await res.json();
        } catch {
          data = {};
        }
        if (res.ok) {
          setModalVisible(false);
          setCupoId(null);
          setHora(new Date());
          Alert.alert('Ficho solicitado', 'Tu ficho ha sido generado.');
          fetchFichos();
        } else {
          console.log('Error al solicitar ficho:', data);
          Alert.alert('Error', data.detail || JSON.stringify(data) || 'No se pudo solicitar el ficho.');
        }
      })
      .catch(() => {
        setLoading(false);
        Alert.alert('Error', 'No se pudo conectar con el servidor.');
      });
  };

  // 4. Cancelar ficho
  const cancelarFicho = (fichoId) => {
    Alert.alert(
      "Cancelar ficho",
      "¿Estás seguro de cancelar tu ficho?",
      [
        { text: "No", style: "cancel" },
        {
          text: "Sí",
          style: "destructive",
          onPress: () => {
            fetch(`${API_BASE_URL}/api/fichos/${fichoId}/cancelar/`, {
              method: 'POST',
              headers: {
                'Authorization': `Token ${token}`
              }
            })
              .then(res => {
                if (res.ok) {
                  Alert.alert("Ficho cancelado");
                  fetchFichos();
                } else {
                  Alert.alert("No se pudo cancelar el ficho");
                }
              })
              .catch(() => Alert.alert("Error de red"));
          }
        }
      ]
    );
  };

  const renderFicho = ({ item }) => (
    <View style={styles.card}>
      <Text style={styles.bienvenida}>¡Hola, {username || 'Usuario'}!</Text>
      <Text style={styles.titulo}>Este es tu ficho</Text>
      <Text style={styles.estado}>
        Estado: <Text style={{fontWeight: 'bold'}}>{item.estado}</Text>
      </Text>
      <Text style={styles.info}>Fecha de solicitud: {item.fecha_solicitud?.slice(0, 10)}</Text>
      <Text style={styles.info}>Hora: {item.hora}</Text>
      <Text style={styles.info}>Servicio: {item.cupo_nombre_servicio || item.cupo?.nombre_servicio}</Text>
      {item.codigo_qr ? (
        <Image
          source={{ uri: item.codigo_qr.startsWith('http') ? item.codigo_qr : `${API_BASE_URL}/media/${item.codigo_qr}` }}
          style={styles.qr}
          resizeMode="contain"
        />
      ) : (
        <Text style={styles.noqr}>QR no disponible</Text>
      )}
      <Text style={styles.mensajeQR}>Muestra este código QR para validar tu ingreso</Text>
    </View>
  );

  // Renderizado principal
  if (!usuario) {
    return (
      <View style={styles.container}>
        <ActivityIndicator color="#2ed8b6" style={{ marginTop: 32 }} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.header}>FichoGo</Text>
      {fichos.length === 0 ? (
        <View style={styles.card}>
          <Text style={styles.noqr}>No tienes ficho activo hoy.</Text>
          <Button
            title={usuario.is_admin ? "Validar Ficho" : "Solicitar nuevo ficho"}
            color="#2ed8b6"
            onPress={() => {
              if (usuario.is_admin) {
                navigation.navigate('Validar');
              } else {
                fetchServicios();
                setModalVisible(true);
              }
            }}
          />
        </View>
      ) : (
        <View style={styles.card}>
          {renderFicho({ item: fichos[0] })}
          <Button
            title="Cancelar ficho"
            color="#e74c3c"
            onPress={() => cancelarFicho(fichos[0].id)}
          />
        </View>
      )}

      {/* Modal para seleccionar servicio y hora */}
      <Modal
        visible={modalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Solicitar Ficho</Text>
            <Text style={styles.modalLabel}>Servicio:</Text>
            {servicios.length === 0 ? (
              <ActivityIndicator color="#2ed8b6" />
            ) : (
              servicios.map(servicio => (
                <TouchableOpacity
                  key={servicio.id}
                  style={[
                    styles.servicioBtn,
                    cupoId === servicio.id && styles.servicioBtnSelected
                  ]}
                  onPress={() => setCupoId(servicio.id)}
                >
                  <Text style={{ color: cupoId === servicio.id ? '#fff' : '#2ed8b6' }}>
                    {servicio.nombre_servicio} ({servicio.cantidad_disponible} disponibles)
                  </Text>
                </TouchableOpacity>
              ))
            )}
            <Text style={styles.modalLabel}>Hora:</Text>
            <TouchableOpacity
              style={styles.input}
              onPress={() => setShowPicker(true)}
            >
              <Text>
                {hora
                  ? hora.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                  : 'Selecciona la hora'}
              </Text>
            </TouchableOpacity>
            {showPicker && (
              <DateTimePicker
                value={hora}
                mode="time"
                is24Hour={true}
                display="default"
                onChange={(event, selectedDate) => {
                  setShowPicker(false);
                  if (selectedDate) setHora(selectedDate);
                }}
              />
            )}
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 16 }}>
              <Button title="Cancelar" color="#888" onPress={() => setModalVisible(false)} />
              <Button title={loading ? "Solicitando..." : "Solicitar"} color="#2ed8b6" onPress={solicitarFicho} disabled={loading} />
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8f8f8',
    padding: 16,
  },
  header: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#2ed8b6',
    marginBottom: 24,
    marginTop: 16,
    letterSpacing: 1,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 24,
    marginBottom: 24,
    width: 340,
    alignItems: 'center',
    elevation: 4,
    shadowColor: '#000',
    shadowOpacity: 0.08,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 4 }
  },
  bienvenida: {
    fontSize: 18,
    color: '#2ed8b6',
    fontWeight: 'bold',
    marginBottom: 8,
  },
  titulo: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 12,
    color: '#222',
  },
  estado: {
    fontSize: 16,
    marginBottom: 6,
    color: '#2ed8b6',
  },
  info: {
    fontSize: 15,
    marginBottom: 2,
    color: '#444',
  },
  qr: {
    width: 180,
    height: 180,
    marginVertical: 18,
    borderWidth: 2,
    borderColor: '#2ed8b6',
    borderRadius: 12,
    backgroundColor: '#f8f8f8'
  },
  mensajeQR: {
    fontSize: 14,
    color: '#888',
    marginTop: 8,
    textAlign: 'center'
  },
  noqr: {
    color: '#888',
    textAlign: 'center',
    marginVertical: 16,
    fontSize: 16
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.3)',
    justifyContent: 'center',
    alignItems: 'center'
  },
  modalContent: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 24,
    width: 320,
    elevation: 8
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2ed8b6',
    marginBottom: 12,
    textAlign: 'center'
  },
  modalLabel: {
    fontSize: 15,
    color: '#2ed8b6',
    marginTop: 10,
    marginBottom: 4
  },
  servicioBtn: {
    borderWidth: 1,
    borderColor: '#2ed8b6',
    borderRadius: 8,
    padding: 10,
    marginVertical: 4,
    alignItems: 'center'
  },
  servicioBtnSelected: {
    backgroundColor: '#2ed8b6',
    borderColor: '#2ed8b6'
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 10,
    marginBottom: 8
  }
});