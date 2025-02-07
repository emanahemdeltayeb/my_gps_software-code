import axios from 'axios';
import * as SecureStore from 'expo-secure-store';
import { URI } from './constants'

export async function login(username, password) {
    console.log("Attempting to login with: " + username + " " + password)
    try {
        const response = await axios.post(`${API}/api/auth/login`, {
            username,
            password,
        }, {
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.data.token) {
            await SecureStore.setItemAsync('token', response.data.token);
            axios.defaults.headers.common['Authorization'] = `JWT ${response.data.token}`
            return true
        }
    } catch (error) {
        console.error("Failed to login: " + error);
        return false
    }
}

export async function logout() {
    try {
        const response = await axios.post(`${API}/api/auth/logout/`)
        if (response.status) { 
            await SecureStore.deleteItemAsync('token');
            delete axios.defaults.headers.common['Authorization'];
            return true
        }
    } catch (error) {
        console.error('Error logging out of account: ', error);
        return false
    }
}

export async function signup(first_name, last_name, email, password) {
    console.log("Attempting to login with: " + username + " " + password)
    try {
        const response = await axios.post(`${API}/api/auth/register`, {
            first_name,
            last_name,
            email,
            password,
        }, {
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.data.token) {
            await SecureStore.setItemAsync('token', response.data.token);
            axios.defaults.headers.common['Authorization'] = `JWT ${response.data.token}`
            return true
        }
    } catch (error) {
        console.error("Failed to login: " + error);
        return false
    }
}