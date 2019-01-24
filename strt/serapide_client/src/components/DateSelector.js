/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import Button from '../components/IconButton'
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css"

class CustomInput extends React.PureComponent {
    render () {
        const {onClick, value} = this.props 
            return (
                <Button 
                    style={{minWidth: 170}}
                    label={value || "Seleziona Data"}
                    color="warning"
                    icon="date_range"
                    onClick={onClick}>          
                </Button>
            )
    }
  }

export default (props) => (<DatePicker customInput={<CustomInput />} {...props}/>)