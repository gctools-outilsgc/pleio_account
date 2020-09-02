import axios from 'axios';
import { returnErrors, createMessage } from './messages';

import {
    USER_LOADED,
    USER_LOADING,
    AUTH_ERROR,
    LOGIN_SUCCESS,
    LOGIN_FAIL,
    LOGOUT_SUCCESS,
    REGISTER_SUCCESS,
    REGISTER_CONFIRM,
    REGISTER_FAIL,
    ACTIVATE_USER,
    ACTIVATE_FAIL
} from './types';

// Check token & load user
export const loadUser = () => (dispatch, getState) => {

    axios.get('/api/auth/user', tokenConfig(getState))
        .then(res => {
            dispatch({
                type: USER_LOADED,
                payload: res.data
            });
        }).catch(err => {
            dispatch(returnErrors(err.response.data, err.response.status));
            dispatch({
                type: AUTH_ERROR
            });
        })
}

// LOGIN USER
export const login = (username, password) => dispatch => {
    // Headers
    const config = {
        headers: {
            'Content-Type': 'application/json'
        },
    };

    // REQUEST body

    const body = JSON.stringify({ username, password });

    axios.post('/auth/login', body, config)
        .then(res => {
            dispatch({
                type: LOGIN_SUCCESS,
                payload: res.data
            });
        }).catch(err => {
            dispatch(returnErrors(err.response.data, err.response.status));
            dispatch({
                type: LOGIN_FAIL
            });
        })
}

// REGISTER
export const register = ({ name, email, password }) => dispatch => {
    // Headers
    const config = {
        headers: {
            'Content-Type': 'application/json'
        },
    };

    // REQUEST body

    const body = JSON.stringify({ name, email, password });

    axios.post('/api/auth/register', body, config)
        .then(res => {
            // dispatch(createMessage(err.response.data, err.response.status));
            dispatch({
                type: REGISTER_SUCCESS,
                payload: res.data
            });
        }).catch(err => {
            dispatch(returnErrors(err.response.data, err.response.status));
            dispatch({
                type: REGISTER_FAIL
            });
        })
}

// REGISTER CONFIRM
export const registerConfirm = () => (dispatch) => {
    dispatch({
        type: REGISTER_CONFIRM,
        payload: null
    });
}

// ACTIVATE_USER
export const activateUser = ({ activation_token }) => dispatch => {
    // Headers
    const config = {
        headers: {
            'Content-Type': 'application/json'
        },
    };

    // REQUEST body

    const body = JSON.stringify({ activation_token });

    axios.post('/api/auth/activate', body, config)
        .then(res => {
            dispatch(createMessage({ accountActivated: "Account activated" }));
            dispatch({
                type: ACTIVATE_USER,
                payload: res.data
            });
        }).catch(err => {
            dispatch(returnErrors(err.response.data, err.response.status));
            dispatch({
                type: ACTIVATE_FAIL
            });
        })
}

// LOG OUT user
export const logout = () => (dispatch, getState) => {

    axios.post('/api/auth/logout', null, tokenConfig(getState))
        .then(res => {
            dispatch({
                type: LOGOUT_SUCCESS
            });
        }).catch(err => {
            dispatch(returnErrors(err.response.data, err.response.status));
        })
}

// Setup config token - helper function
export const tokenConfig = getState => {
    // Get token from cookie
    const csrftoken = getCookie('csrftoken');

    // Headers
    const config = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
    };

    return config;
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}