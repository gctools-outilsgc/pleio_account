import React, { Component, Fragment } from 'react';
import ReactDOM from 'react-dom';
import { HashRouter as Router, Route, Switch, Redirect, Link } from 'react-router-dom';

import Users from './Users';
import Alerts from './core/Alerts';
import PrivateRoute from './core/PrivateRoute';
import Header from './core/Header';
import NoMatch from './core/NoMatch';
import Login from './home/Login';
import Register from './home/Register';
import Activate from './home/Activate';

import LoggedIN from './settings/LoggedIN';
import OtherPath from './settings/OtherPath';

import { Provider as AlertProvider } from 'react-alert';
import AlertTemplate from 'react-alert-template-basic';

import { Provider } from 'react-redux';
import store from '../store';
import { loadUser } from '../actions/auth';

// Alert options
const alertOptions = {
    timeout: 3000,
    position: 'top center'
}

class App extends Component {
    componentDidMount() {
        store.dispatch(loadUser());
    }

    render() {
        return (
            <Provider store={store}>
                <AlertProvider template={AlertTemplate} {...alertOptions}>
                    <Router>
                        <Fragment>
                            <Header />
                            <Alerts />
                            <Switch>
                                <PrivateRoute exact path="/" component={Users} />
                                <PrivateRoute exact path="/loggedin" component={LoggedIN} />
                                <PrivateRoute exact path="/otherpath" component={OtherPath} />
                                <Route exact path="/register/activate/:activation_token" component={Activate} />
                                <Route path="/register" component={Register} />
                                <Route path="/login" component={Login} />
                                <Route component={NoMatch} />
                            </Switch>
                        </Fragment>
                    </Router>
                </AlertProvider>
            </Provider>
        )
    }
}

ReactDOM.render(<App />, document.getElementById('app'));