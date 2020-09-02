import React, { Component } from 'react';
import { Redirect } from "react-router-dom";
import { Link } from 'react-router-dom';
import { connect } from 'react-redux';
import PropTypes from 'prop-types'
import { register, registerConfirm } from '../../actions/auth';
import { createMessage } from '../../actions/messages'

import {
  Card, CardBody,
  CardTitle, CardText, CardSubtitle, Button,
  Form, FormGroup, Label, Input,
} from 'reactstrap';

export class Register extends Component {
  state = {
    name: '',
    email: '',
    password: '',
    password2: '',
    accepted_terms: false,
  }

  static propTypes = {
    register: PropTypes.func.isRequired,
    registerConfirm: PropTypes.func.isRequired,
    isAuthenticated: PropTypes.bool,
    user: PropTypes.object,
  }

  onSubmit = e => {
    e.preventDefault();
    const { name, email, password, password2, accepted_terms } = this.state;
    if (password !== password2) {
      this.props.createMessage({
        passwordNotMatch:
          'passwords do not match'
      });
    } else {
      const newUser = {
        name,
        email,
        password,
        accepted_terms
      }
      this.props.register(newUser);
    }
  }

  onChange = e => this.setState({ [e.target.name]: e.target.value });
  onCheckChange = e => this.setState({
    accepted_terms: !this.state.accepted_terms
  });

  componentWillUnmount() {
    if (this.props.user) {
      this.props.registerConfirm();
    }
  }

  render() {
    const { name, email, password, password2, accepted_terms } = this.state;

    if (this.props.isAuthenticated) {
      return <Redirect to="/" />;
    }

    if (this.props.user) {
      return (
        <Card className="col-md-6 m-auto">
          <CardBody>
            <h1>
              <CardTitle>Registration Success</CardTitle>
            </h1>
            <CardText>
              A confirmation email has been sent to <strong>{email}</strong>.
            </CardText>
            <Link to="/login">Return to sign in</Link>
          </CardBody>
        </Card>
      );
    }

    return (
      <div>
        <Card className="col-md-6 m-auto">
          <CardBody>
            <h1>
              <CardTitle>Register</CardTitle>
              <CardSubtitle>your GCaccount</CardSubtitle>
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
                  required
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
                  required
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
                  required
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
                  required
                />
              </FormGroup>
              <FormGroup check>
                <Label check>
                  <Input
                    id="accepted_terms"
                    type="checkbox"
                    checked={accepted_terms}
                    onChange={e => this.setState({ accepted_terms: e.target.checked })}
                    required
                  />
                  {' '} I agree with the terms and conditions
                </Label>
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
  user: state.auth.user,
});

export default connect(mapStateToProps, { register, registerConfirm, createMessage })(Register);
