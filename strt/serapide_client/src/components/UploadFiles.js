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

class UploadFiles extends React.PureComponent {
    static propTypes = {
        placeholder: PropTypes.string,
        variables: PropTypes.object,
        fileType: PropTypes.string,
        risorse: PropTypes.array,
        isLocked: PropTypes.bool,
        disabled: PropTypes.bool,
        mutation: PropTypes.object,
        resourceMutation: PropTypes.object,
        getSuccess: PropTypes.func,
        multiple: PropTypes.bool
    }
    static defaultProps = {
        placeholder: "",
        variables: {},
        fileType: "application/pdf",
        risorse: [],
        isLocked: true,
        disabled: false,
        multiple: true,
        mutation: FILE_UPLOAD,
        resourceMutation: DELETE_RISORSA,
        getSuccess: ({upload: {success}}) => success
    }
    onFilesChange = (files = []) => {
        if (files.length > 0) {
            this.setState(() => ({files}))
        }else {
            this.setState(() => ({files: undefined}))
        }
    }
    updateCache = (cache, { data} = {}) => {
        if (this.props.getSuccess(data)) {
            const {upload: {fileName} } = data
            this.removeFile(fileName)
        }
    }
    renderRisorse = () => {
        const {variables, resourceMutation, isLocked} = this.props
        return (this.props.risorse.map((res) => (
            <Resource codice={variables.codice} mutation={resourceMutation} key={res.uuid} resource={res} isLocked={isLocked}/>))
            )
        }
    removeFile = (nome= "") => {
        const files = this.state.files.filter(file => file.name !== nome);
        this.setState(() => ({files}))
    }
    renderLoader = () => {
        const {files = []} = this.state || {}
        const {variables, placeholder} = this.props
        return files.map((file) => (
            <FileLoader
                key={file.name}
                update={this.updateCache}
                mutation={FILE_UPLOAD}
                file={file}
                placeholder={placeholder}
                variables={variables}
                onAbort={this.removeFile}
            />))
    }
    render() {
        return  (
            <React.Fragment>
               <div className="multiple-upload mt-3 pb-2 d-flex flex-column justify-content-between"> 
               {this.renderRisorse()}
               {this.renderLoader()}
               </div>
               <div className="align-self-start"> 
               {!this.props.isLocked && <FileChooser
                    isLocked={this.props.isLocked}
                    disabled={this.props.isLocked} 
                    fileType={this.props.fileType}
                    multiple={this.props.multiple }
                    onFilesChange={this.onFilesChange}
                    sz="sm"/>}
                </div>
            </React.Fragment>
            )
    }
}

export default UploadFiles
