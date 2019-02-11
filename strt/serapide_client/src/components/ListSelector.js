/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Modal, ModalBody, ModalHeader, ListGroup, ListGroupItem} from 'reactstrap'
import {toggleControllableState} from '../enhancers/utils'
import {Query} from 'react-apollo'
import {toast} from 'react-toastify'
import classNames from 'classnames'


const enhancer = toggleControllableState("isOpen", "toggleOpen", false)

const ListItem = ({option: {value, label} = {}, selected = false, onClick}) => (
    <ListGroupItem  onClick={() => onClick(value)}>
        <span className="d-flex justify-content-start">
            <i className={classNames('material-icons',{"text-warning": selected})}>{selected ?  'radio_button_checked' : 'radio_button_unchecked'}</i>
            <span className="pl-2">{label}</span>
        </span>
    </ListGroupItem>)

const ListSelector = enhancer(({size, children, label, selected = [], isOpen, toggleOpen, onChange = () => {}, btn, items = [], getOption = ({value, label}) => ({value, label})}) => {
    return (
    <React.Fragment>
           {btn && btn(toggleOpen)}
            <Modal size={size} isOpen={isOpen} toggle={toggleOpen} wrapClassName="serapide" autoFocus={true}>
                <ModalHeader>{label}</ModalHeader>
                <ModalBody> 
                    <ListGroup>
                        {items.map((n) => {
                            const opt = getOption(n) || {}
                            return <ListItem key={opt.value} option={opt} onClick={onChange} selected={selected.indexOf(opt.value) !== -1} ></ListItem>
                        })}
                    </ListGroup>
                    {children}
                </ModalBody>
            
                
            </Modal>
    </React.Fragment>
    )}
)
export default ListSelector

const _getList = (data) => {
    return[]
}

export const EnhancedListSelector = ({query, variables, getList = _getList , ...props}) => (
    <Query query={query} variables={variables}>
        {({loading, data, error}) => {
                if (error) {
                    toast.error(error.message,  {autoClose: true})
                }
                return (
                    <ListSelector isLoading={loading} items={getList(data)} {...props}></ListSelector>
                    )
        }}
    </Query>
)