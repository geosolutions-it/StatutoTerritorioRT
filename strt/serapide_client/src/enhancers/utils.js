/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import { withStateHandlers, branch, withState, compose, lifecycle, pure} from 'recompose';
import ReactTooltip from 'react-tooltip'

/**
 * Same as recompose's `withState`, but if the component has already defined a property
 * with the handlerName, it assume the prop is controlled and then
 *
 * @example
 * const CMP = withControllableState('active', 'setActive', false)(({setActive = () => {}, active = false}) => <div><button onClick={e => setActive(!active)} >Activate</button>{active ? <RenderMyComponent /> : <span>activate to see...</span>}</div> )
 * //... far far away in a rendering function the active state is controlled
 * <CMP setActive={callMyAction} active={isMyPanelActive} />
 * // ... far far away in another renering function i don't care if is active or not, let it control by itself
 * <CMP />
 *
 * @param  {string} propName     the name of the property
 * @param  {[type]} handlerName  the name of the handler. If the component already has a property defined with the handler name. withControllableState has no effect (so you can control the component with same properties)
 * @param  {[type]} initialValue [description]
 * @return {[type]}              [description]
 */
export const withControllableState = (propName, handlerName, initialValue) =>
    branch(
        (props = {}) => !props[handlerName] && !props[propName],
        withState(propName, handlerName, initialValue)
    )
export const toggleControllableState = (propName, handlerName, initialValue = false) =>
        branch(
            (props = {}) => !props[handlerName] && !props[propName],
            compose(
                withStateHandlers((props) => ({
                    [propName]: props.initValue || initialValue}), 
                    {[handlerName]: (s) => () => ({[propName]: !s[propName]}) 
                    }
            )
            )
        )

export const rebuildTooltip = ({onUpdate = false, log = false, comp = ""} = {}) => {
    const logger = log ? (fase) => {console.log(comp + " " + fase + " ")} : () => {}
    return compose(pure,
        lifecycle({
            componentDidUpdate() {
                ReactTooltip.rebuild()
                logger("Update")
            },
            componentDidMount() { 
                ReactTooltip.rebuild()
                logger("Mount")
    }}
))}
    
export const stopStartPolling = (pollingInterval) => lifecycle({
    componentDidMount() {
      //console.log("did mount stop", this.props.stopPolling)
      this.props.stopPolling && this.props.stopPolling()
    },
    componentDidUpdate() {
        //console.log("did update stop", this.props.stopPolling)
        this.props.stopPolling && this.props.stopPolling()
    },
    componentWillUnmount() {
        //console.log("will unmount start", this.props.startPolling)
        this.props.startPolling && this.props.startPolling(pollingInterval)
    }})

export default {
        withControllableState,
        toggleControllableState,
        rebuildTooltip,
        stopStartPolling
}

  