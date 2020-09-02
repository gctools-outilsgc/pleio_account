import React, { Component } from 'react'
import { Redirect } from "react-router-dom";
import PropTypes from 'prop-types'
import { connect } from 'react-redux';
import { Container, Row, CardBody, Card, CardText, CardTitle } from 'reactstrap';

import { activateUser } from '../../actions/auth';
import { createMessage } from '../../actions/messages'

export class Activate extends Component {

  static propTypes = {
    activateUser: PropTypes.func.isRequired,
  }

  componentDidMount() {
    if (this.props.match.params.activation_token) {
      const activation_token = {
        activation_token: this.props.match.params.activation_token
      }
      this.props.activateUser(activation_token);
    } else {
      return <Redirect to="/" />;
    }
  }
  render() {
    if (this.props.isAuthenticated) {
      return <Redirect to="/" />;
    }

    let errorSection = this.props.error ? "Invalid or expired token. Please try again." : "Loading"
    return (
      <Container>
        <Row>
          <Card className="col-md-6 m-auto">
            <CardBody>
              <h1>
                <CardTitle>Activating account</CardTitle>
              </h1>
              <div aria-live="assertive">
                <CardText >
                  {errorSection}
                </CardText>
              </div>
            </CardBody>
          </Card>
        </Row>
      </Container>
    )
  }
}

const mapStateToProps = state => ({
  isAuthenticated: state.auth.isAuthenticated,
  user: state.auth.user,
  error: state.errors,
});

export default connect(mapStateToProps, { activateUser, createMessage })(Activate);
