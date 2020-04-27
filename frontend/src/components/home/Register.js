import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import { connect } from 'react-redux';
import PropTypes from 'prop-types'
import { register } from '../../actions/auth';
import { createMessage } from '../../actions/messages'

import {
    Card, CardText, CardBody,
    CardTitle, CardSubtitle, Button,
    Form, FormGroup, Label, Input,
    FormText
} from 'reactstrap';

export class Register extends Component {
    state = {
        name: '',
        email: '',
        password: '',
        password2: '',
    }

    static propTypes = {
        register: PropTypes.func.isRequired,
        isAuthenticated: PropTypes.bool
    }


    onSubmit = e => {
        e.preventDefault();
        const { name, email, password, password2 } = this.state;
        if (password !== password2) {
            this.props.createMessage({
                passwordNotMatch:
                    'passwords do not match'
            });
        } else {
            const newUser = {
                name,
                email,
                password
            }
            this.props.register(newUser);
        }
    }

    onChange = e => this.setState({ [e.target.name]: e.target.value });

    render() {
        if (this.props.isAuthenticated) {
            return <Redirect to="/" />;
        }

        const { name, email, password, password2 } = this.state;

        return (
            <div>
                <Card className="col-md-6 m-auto">
                    <CardBody>
                        <h1>
                            <CardTitle>Register</CardTitle>
                            <CardSubtitle>with your account</CardSubtitle>
                        </h1>

                        <Form onSubmit={this.onSubmit}>
                            <FormGroup>
                                <Label for="name">First and last name</Label>
                                <Input
                                    type="text"
                                    name="name"
                                    id="name"
                                    onChange={this.onChange}
                                    value={name}
                                />
                            </FormGroup>
                            <FormGroup>
                                <Label for="username">Email</Label>
                                <Input
                                    type="email"
                                    name="email"
                                    id="email"
                                    onChange={this.onChange}
                                    value={email}
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
                            <FormGroup>
                                <Label for="password2">Confirm password</Label>
                                <Input
                                    type="password"
                                    name="password2"
                                    id="password2"
                                    onChange={this.onChange}
                                    value={password2}
                                />
                            </FormGroup>
                            <Button color="primary" block>Register</Button>
                        </Form>
                        <Link to="/login">Return to sign in</Link>
                    </CardBody>
                </Card>
            </div >
        )
    }
}

const mapStateToProps = state => ({
    isAuthenticated: state.auth.isAuthenticated,
});

export default connect(mapStateToProps, { register, createMessage })(Register);
