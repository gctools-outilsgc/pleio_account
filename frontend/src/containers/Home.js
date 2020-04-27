import React, { Component, Fragment } from 'react';

import { Container, Row } from 'reactstrap';

import { Login } from '../components/home/Login'
export class Home extends Component {
    render() {
        return (
            <Fragment>
                <Container>
                    <Row>
                        <Login />
                    </Row>
                </Container>
            </Fragment>
        )
    }
}

export default Home
