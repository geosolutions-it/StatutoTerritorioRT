/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import PropTypes from 'prop-types'
import FileChooser from "./FileChooser"
import FileLoader from "./EnhancedFileLoader"
import {FILE_UPLOAD, GET_PIANI, DELETE_RISORSA} from "../queries"
import Resource from './EnhancedResource'


class SingleFile extends React.PureComponent {
    static propTypes = {
        risorsa: PropTypes.object,
        placeholder: PropTypes.string,
        variables: PropTypes.object,
        fileType: PropTypes.string,
        isLocked: PropTypes.bool,
        disabled: PropTypes.bool
    }
    static defaultProps = {
        placeholder: "",
        variables: {},
        fileType: "application/pdf",
        isLocked: true,
        disabled: false
    } 
    onFilesChange = (files = []) => {
        if (files[0]) {
            this.setState(() => ({file: files[0]}))
        }else {
            this.setState(() => ({file: undefined}))
        }
    }
    updateCache = (cache, { data: {upload : {success, risorse}}  = {}} = {}) => {
        const {codice} = this.props.variables
        if (success) {
            const __typename = "RisorsaNodeEdge" 
            let { piani ={}} = cache.readQuery({ query: GET_PIANI, variables: {codice}}) || {}
            const edges = piani.edges[0].node.risorse.edges.concat(risorse.map(node => ({__typename, node})))
            piani.edges[0].node.risorse.edges = edges
            cache.writeQuery({
                            query: GET_PIANI,
                            data: { piani},
                            variables: {codice}
                        })
            this.removeFile()
        }
    }
    updateResource = (cache, { data: {deleteRisorsa : {success}}  = {}} = {}) => {
        const {variables: {codice} = {}, risorsa} = this.props
        if (success) {
            let { piani ={}} = cache.readQuery({ query: GET_PIANI, variables: {codice}}) || {}
            const edges = piani.edges[0].node.risorse.edges.filter(({node: {uuid}}) => uuid !== risorsa.uuid)
            piani.edges[0].node.risorse.edges = edges
            cache.writeQuery({
                            query: GET_PIANI,
                            data: { piani},
                            variables: {codice}
                        })
        }
    }
    removeFile = () => {
        if(this.state && this.state.file) {
            this.setState(()=> ({file: undefined}))
        }
    }
    render() {
        const {file} = this.state || {}
        const {risorsa, variables, placeholder, isLocked, disabled} = this.props
        return  risorsa ? (<Resource update={this.updateResource} mutation={DELETE_RISORSA} resource={risorsa} isLocked={isLocked}/>) : (
            <div style={{minHeight: "3.813rem"}} className="d-flex justify-content-between border-top border-bottom align-items-center">
                <FileLoader
                    mutation={FILE_UPLOAD}
                    file={file}
                    placeholder={placeholder}
                    variables={variables}
                    update={this.updateCache}
                    onAbort={this.removeFile}
                    renderChooser={(loading) => (
                        <FileChooser 
                            disableBtn={    disabled || !!loading}
                            multiple={false}
                            fileType="application/pdf"
                            onFilesChange={this.onFilesChange}
                            modal
                            showBtn
                            sz="lg"/>)}
                />
                
            </div>
            )
    }
    componentWillUnmount() {
        this.setState({file: undefined})
    }
}

export default SingleFile
