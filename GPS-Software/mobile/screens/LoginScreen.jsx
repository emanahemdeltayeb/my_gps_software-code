import React, { useState } from 'react';
import { View, Text, TextInput, StyleSheet, TouchableOpacity, Dimensions } from 'react-native';
import { CommonActions, useNavigation } from '@react-navigation/native';
import SignUpScreen from './SignUpScreen';
// import { login } from '../utils';

const LoginScreen = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const navigation = useNavigation();

    const handleLogin = async () => {
        // Implement login logic here
        if (!username || !password) { return; }
    
        // try {
        //     const res = await login(username, password); // Wait for login result
    
        //     if (res) {
        //         navigation.dispatch(
        //             CommonActions.reset({
        //                 index: 1, // Focus on the Home screen (2nd screen in the stack)
        //                 routes: [{ name: 'Main' }], // Add Home as the first screen
        //             })
        //         );
        //     }
        // } catch (error) {
        //     console.error("Login failed: ", error);
        // }
    };    

    const navigateSignUp = () => {
        navigation.dispatch(
            CommonActions.reset({
                index: 1, // Focus on the Login screen (2nd screen in the stack)
                routes: [
                    { name: 'Main' }, // Add Home as the first screen
                    { name: 'SignUp' }, // Add Login as the second screen
                ],
            })
        );
    };

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Log In</Text>
            <TextInput
                style={styles.input}
                placeholder="Username"
                value={username}
                onChangeText={setUsername}
                autoCapitalize="none"
            />
            <TextInput
                style={styles.input}
                placeholder="Password"
                value={password}
                onChangeText={setPassword}
                secureTextEntry
            />
            <TouchableOpacity style={styles.button} onPress={handleLogin}>
                <Text style={styles.buttonText}>Log In</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={navigateSignUp}>
                <Text style={styles.linkText}>Don't have an account? Sign Up</Text>
            </TouchableOpacity>
        </View>
    );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    paddingLeft: Dimensions.get('window').width > 768 ? '35%' : '20px',
    paddingRight: Dimensions.get('window').width > 768 ? '35%' : '20px'
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  input: {
    width: '100%',
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    borderRadius: 5,
    marginBottom: 10,
    paddingHorizontal: 10,
  },
  button: {
    backgroundColor: '#4594f1',
    padding: 10,
    borderRadius: 5,
    marginVertical: 10,
    width: '100%',
    alignItems: 'center',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  linkText: {
    color: '#4594f1',
    marginTop: 10,
  },
});

export default LoginScreen;

