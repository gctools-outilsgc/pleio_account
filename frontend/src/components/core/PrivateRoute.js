import React, { useEffect } from "react";
import { Route, Redirect } from "react-router-dom";
import { connect } from "react-redux";
import PropTypes from 'prop-types'

const PrivateRoute = ({ component: Component, auth, ...rest }) => (
    <Route
        {...rest}
        render={props => {
            if (auth.isLoading) {
                return <h2>Loading...</h2>;
            } else if (!auth.isAuthenticated) {
                return <Redirect to={{
                    pathname: "/login",
                    state: {
                        next: props.location.pathname,
                        querystring: props.location.search
                    }
                }} />;
            } else {
                return <Component {...props} />;
            }
        }}
    />
)

const MapStateToProps = state => ({
    auth: state.auth
});

export default connect(MapStateToProps)(PrivateRoute);