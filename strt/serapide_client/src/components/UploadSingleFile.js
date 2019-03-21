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
import {FILE_UPLOAD, DELETE_RISORSA} from "../queries"
import Resource from './EnhancedResource'


class SingleFile extends React.PureComponent {
    static propTypes = {
        risorsa: PropTypes.object,
        placeholder: PropTypes.string,
        variables: PropTypes.object,
        fileType: PropTypes.string,
        isLocked: PropTypes.bool,
        disabled: PropTypes.bool,
        mutation: PropTypes.object,
        resourceMutation: PropTypes.object,
        modal: PropTypes.bool,
        showBtn: PropTypes.bool,
        getSuccess: PropTypes.func,
        sz: PropTypes.oneOf(["sm","lg"]) 
    }
    static defaultProps = {
        placeholder: "",
        variables: {},
        fileType: "application/pdf",
        isLocked: true,
        disabled: false,
        mutation: FILE_UPLOAD,
        resourceMutation: DELETE_RISORSA,
        modal: true,
        showBtn: true,
        getSuccess: ({upload: {success}}) => success,
        sz: "lg"
        
    } 
    onFilesChange = (files = []) => {
        if (files[0]) {
            this.setState(() => ({file: files[0]}))
        }else {
            this.setState(() => ({file: undefined}))
        }
    }
    updateCache = (cache, { data} = {}) => {
        if (this.props.getSuccess(data)) {
            this.removeFile()
        }
    }
    removeFile = () => {
        if(this.state && this.state.file) {
            this.setState(()=> ({file: undefined}))
        }
    }
    render() {
        
        const {file} = this.state || {}
        const {risorsa, variables, placeholder, isLocked, disabled, mutation, resourceMutation, modal, showBtn, sz, className = ""} = this.props
        return  risorsa ? (<Resource className={className} codice={variables.codice} mutation={resourceMutation} resource={risorsa} isLocked={isLocked}/>) : (
            <div style={{minHeight: "3.813rem"}} className={`${className} file-loader d-flex justify-content-between border-top border-bottom align-items-center`}>
                <FileLoader
                    mutation={mutation}
                    file={file}
                    placeholder={placeholder}
                    variables={variables}
                    update={this.updateCache}
                    onAbort={this.removeFile}
                    renderChooser={(loading) => (
                        <FileChooser 
                            isLocked={disabled || !!loading || isLocked}
                            multiple={false}
                            fileType="application/pdf"
                            onFilesChange={this.onFilesChange}
                            modal={modal}
                            showBtn={showBtn}
                            sz={sz}/>)}
                />
                
            </div>
            )
    }
    componentWillUnmount() {
        this.setState({file: undefined})
    }
}

export default SingleFile
