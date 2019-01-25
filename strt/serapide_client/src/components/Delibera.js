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


class Delibera extends React.PureComponent {
    static propTypes = {
           delibera: PropTypes.object,
           codice: PropTypes.string
    } 
    onFilesChange = (files = []) => {
        if (files[0]) {
            this.setState(() => ({file: files[0]}))
        }else {
            this.setState(() => ({file: undefined}))
        }
    }
    updateCache = (cache, { data: {upload : {success, risorse}}  = {}} = {}) => {
        const {codice} = this.props
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
        const {codice, delibera} = this.props
        if (success) {
            let { piani ={}} = cache.readQuery({ query: GET_PIANI, variables: {codice}}) || {}
            const edges = piani.edges[0].node.risorse.edges.filter(({node: {uuid}}) => uuid !== delibera.uuid)
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
        const {delibera, codice} = this.props
        return  delibera ? (<Resource update={this.updateResource}mutation={DELETE_RISORSA} refetchQueries={this.refetchQueries} resource={delibera}/>) : (
            <div style={{minHeight: "3.813rem"}}className="d-flex justify-content-between border-top border-bottom align-items-center">
                <FileLoader
                    mutation={FILE_UPLOAD}
                    file={file}
                    placeholder="Delibera Comunale (obbligatoria)"
                    variables={{codice, tipo: "delibera" }}
                    update={this.updateCache}
                />
                <FileChooser 
                    disableBtn={!!file}
                    multiple={false}
                    fileType="application/pdf"
                    onFilesChange={this.onFilesChange}
                    modal
                    showBtn
                    sz="lg"/>
            </div>
            )
    }
    componentWillUnmount() {
        this.setState({file: undefined})
    }
}

export default Delibera
