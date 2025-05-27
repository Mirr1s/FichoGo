import * as React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import FichosScreen from './FichosScreen';
import HistorialScreen from './HistorialScreen';
import PerfilScreen from './PerfilScreen';
import LoginScreen from './LoginScreen';
import RegistroScreen from './RegistroScreen';
import ValidarFichoScreen from './ValidarFichoScreen';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE_URL } from './config';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

function MainTabs({ token, username, setToken }) {
  const [usuario, setUsuario] = React.useState(null);

  React.useEffect(() => {
    fetch(`${API_BASE_URL}/api/usuario/`, {
      headers: { 'Authorization': `Token ${token}` }
    })
      .then(res => res.json())
      .then(data => setUsuario(data))
      .catch(() => setUsuario(null));
  }, [token]);

  if (!usuario) {
    return <></>;
  }

  return (
    <Tab.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: '#2ed8b6' },
        headerTintColor: '#fff',
        tabBarActiveTintColor: '#2ed8b6'
      }}
    >
      {usuario.is_admin ? (
        <>
          <Tab.Screen
            name="Validar"
            options={{
              title: 'Validar Fichos',
              tabBarIcon: ({ color, size }) => (
                <Icon name="qrcode-scan" color={color} size={size} />
              ),
            }}
          >
            {props => <ValidarFichoScreen {...props} token={token} />}
          </Tab.Screen>
          <Tab.Screen
            name="Perfil"
            options={{
              tabBarIcon: ({ color, size }) => (
                <Icon name="account-circle" color={color} size={size} />
              ),
            }}
          >
            {props => <PerfilScreen {...props} token={token} username={username} setToken={setToken} />}
          </Tab.Screen>
        </>
      ) : (
        <>
          <Tab.Screen
            name="Inicio"
            options={{
              tabBarIcon: ({ color, size }) => (
                <Icon name="chevron-left" color={color} size={size} />
              ),
            }}
          >
            {props => <FichosScreen {...props} token={token} username={username} />}
          </Tab.Screen>
          <Tab.Screen
            name="Historial"
            options={{
              tabBarIcon: ({ color, size }) => (
                <Icon name="chevron-right" color={color} size={size} />
              ),
            }}
          >
            {props => <HistorialScreen {...props} token={token} username={username} />}
          </Tab.Screen>
          <Tab.Screen
            name="Perfil"
            options={{
              tabBarIcon: ({ color, size }) => (
                <Icon name="account-circle" color={color} size={size} />
              ),
            }}
          >
            {props => <PerfilScreen {...props} token={token} username={username} setToken={setToken} />}
          </Tab.Screen>
        </>
      )}
    </Tab.Navigator>
  );
}

export default function App() {
  const [token, setToken] = React.useState(null);
  const [username, setUsername] = React.useState('');
  const [showRegister, setShowRegister] = React.useState(false);

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {!token && !showRegister ? (
          <Stack.Screen name="Login">
            {props => (
              <LoginScreen
                {...props}
                onLogin={(tk, user) => { setToken(tk); setUsername(user); }}
                onShowRegister={() => setShowRegister(true)}
              />
            )}
          </Stack.Screen>
        ) : !token && showRegister ? (
          <Stack.Screen name="Registro">
            {props => (
              <RegistroScreen
                {...props}
                onRegister={() => setShowRegister(false)}
              />
            )}
          </Stack.Screen>
        ) : (
          <Stack.Screen name="Main">
            {props => <MainTabs {...props} token={token} username={username} setToken={setToken} />}
          </Stack.Screen>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
