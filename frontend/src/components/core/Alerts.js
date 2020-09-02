import React, { Component, Fragment } from 'react'
import { withAlert } from 'react-alert';
import { connect } from 'react-redux';
import PropTypes from 'prop-types'


export class Alerts extends Component {
    static propTypes = {
        error: PropTypes.object.isRequired,
        message: PropTypes.object.isRequired
    }

    componentDidUpdate(prevProps) {
        const { error, alert, message } = this.props;
        if (error !== prevProps.error) {
            if (error.msg.non_field_errors) {
                alert.error(error.msg.non_field_errors.join());
            }
            if (error.msg.email) alert.error(error.msg.email);
        }

        if (message !== prevProps.message) {
            // if (message.userDeleted) alert.success(message.userDeleted)     <- uses key created in reducer
            // if (message.userAdded) alert.success(message.userAdded)     <- uses key created in reducer
            if (message.passwordNotMatch) alert.error(message.passwordNotMatch);
            if (message.accountActivated) alert.error(message.accountActivated);
        }
    }

    render() {
        return <Fragment />;
    }
}

const MapStateToProps = state => ({
    error: state.errors,
    message: state.messages
});

export default connect(MapStateToProps)(withAlert()(Alerts))