import React, { Component } from 'react'
import { Link } from 'react-router-dom';
import { Nav, NavItem, Button } from 'reactstrap';
import { connect } from "react-redux";
import PropTypes from 'prop-types'

import { logout } from '../../actions/auth';

export class Header extends Component {
    static propTypes = {
        auth: PropTypes.object.isRequired,
        logout: PropTypes.func.isRequired
    }
    render() {
        const { isAuthenticated, user } = this.props.auth;

        const authLinks = (
            <Nav className="ml-auto">
                <NavItem className="mr-3">
                    {user ? `Welcome ${user.name}` : ""}
                </NavItem>
                <NavItem>
                    <Button onClick={this.props.logout} size="sm">logout</Button>
                </NavItem>
            </Nav>
        );

        const guestLinks = (
            <Nav>
                <NavItem>
                    <Link to="/register">Register</Link>
                </NavItem>
                <NavItem>
                    <Link to="/login">Login</Link>
                </NavItem>
            </Nav>
        );

        return (
            <div>
                {isAuthenticated ? authLinks : guestLinks}
            </div>
        )
    }
}

const mapStateToProps = state => ({
    auth: state.auth,
})

export default connect(mapStateToProps, { logout })(Header);
