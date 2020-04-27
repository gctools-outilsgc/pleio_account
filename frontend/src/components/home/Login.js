import React, { Component } from 'react';
import { Link, Redirect } from 'react-router-dom';
import { connect } from 'react-redux';
import PropTypes from 'prop-types'
import { login } from '../../actions/auth';

import {
    Card, CardText, CardBody,
    CardTitle, CardSubtitle, Button,
    Form, FormGroup, Label, Input,
    FormText
} from 'reactstrap';

export class Login extends Component {
    state = {
        username: '',
        password: '',
    }

    static propTypes = {
        login: PropTypes.func.isRequired,
        isAuthenticated: PropTypes.bool
    }

    onSubmit = (e) => {
        e.preventDefault();
        this.props.login(this.state.username, this.state.password);
    }

    onChange = (e) => this.setState({ [e.target.name]: e.target.value });

    render() {
        if (this.props.isAuthenticated) {
            return <Redirect to="/" />;
        }
        const { username, password } = this.state;
        return (
            <div>
                <Card className="col-md-6 m-auto">
                    <CardBody>
                        <h1>
                            <CardTitle>Sign in</CardTitle>
                            <CardSubtitle>with your account</CardSubtitle>
                        </h1>

                        <Form onSubmit={this.onSubmit}>
                            <FormGroup>
                                <Label for="username">Email</Label>
                                <Input
                                    type="email"
                                    name="username"
                                    id="username"
                                    onChange={this.onChange}
                                    value={username}
                                />
                            </FormGroup>
                            <FormGroup>
                                <Label for="password">Password</Label>
                                <Input
                                    type="password"
                                    name="password"
                                    id="password"
                                    onChange={this.onChange}
                                    value={password}
                                />
                            </FormGroup>
                            <Button color="primary" block>Login</Button>
                            <p>Don't have an account?<Link to='/register'>Register</Link></p>
                        </Form>
                    </CardBody>
                </Card>
            </div>
        )
    }
}

const MapStateToProps = state => ({
    isAuthenticated: state.auth.isAuthenticated,
});

export default connect(MapStateToProps, { login })(Login)

