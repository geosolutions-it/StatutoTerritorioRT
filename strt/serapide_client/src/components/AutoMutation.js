/* All rights reserved.
*
* This source code is licensed under the BSD-style license found in the
* LICENSE file in the root directory of this source tree.
*/
import React from 'react'
import {isFunction} from 'lodash'
import {Mutation} from "react-apollo"


/**
 * Auto trigger mutation onMount or Update
 */
class AutoMutate extends React.PureComponent {

    componentDidMount() {
        if(!this.props.called && !this.props.loading) {
            this.props.triggerMutation()
        }

    }
    componentDidUpdate() {
        if(!this.props.called && !this.props.loading) {
            this.props.triggerMutation()
        }
    }

    render() {
        return null
    }
}

export default (props = {}) => (
    <Mutation {...props}>
        {(triggerMutation, {loading, called, ...rest}) => (
            <React.Fragment>
                <AutoMutate loading={loading} called={called} triggerMutation={triggerMutation}></AutoMutate>
                {isFunction(props.children) && props.children(triggerMutation, {loading, called, ...rest})}
            </React.Fragment>
        )}
    </Mutation>

)