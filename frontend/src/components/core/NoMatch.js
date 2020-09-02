import React, { Component } from 'react'
import { Redirect } from "react-router-dom";

export class NoMatch extends Component {
    render() {
        return <Redirect to="/" />;
    }
}

export default NoMatch
