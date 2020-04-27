import axios from 'axios';
import { createMessage, returnErrors } from './messages';
import { tokenConfig } from './auth';

import { GET_USERS } from './types';

//GET USERS
export const getUsers = () => (dispatch, getState) => {
    axios.get('/api/users/all', tokenConfig(getState))
        .then(res => {
            dispatch({
                type: GET_USERS,
                payload: res.data
            });
        }).catch(err => dispatch(returnErrors(
            err.response.data, err.response.status))
        );
};

//Delete user example
/*
export const deleteUsers = (id) => (dispatch, getState) => {
    axios.delete(`/api/users/all/${id}/`, tokenConfig(getState))
        .then(res => {
            dispatch(createMessage({ userDeleted: 'user deleted'}))
            dispatch({
                type: DELETE_USERS, // LOADED from TYPES
                payload: id
            });
        }).catch(err => dispatch(returnsErrors(
            err.response.data, err.response.status))
        );
};*/

//add user example
/*
export const addUser = (user) => (dispatch, getState) => {
    axios.post('/api/users/all', user, tokenConfig(getState))
        .then(res => {
            dispatch(createMessage({ userAdded: 'user added'})
            dispatch({
                type: ADD_USER,
                payload: res.data
            });
        }).catch(err => dispatch(returnsErrors(
            err.response.data, err.response.status))
        );
};*/