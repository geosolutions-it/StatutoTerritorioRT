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
import {FILE_UPLOAD, GET_PIANI} from "../queries"
import Resource from './EnhancedResource'

class UploadFiles extends React.PureComponent {
    static propTypes = {
        placeholder: PropTypes.string,
        variables: PropTypes.object,
        fileType: PropTypes.string,
        risorse: PropTypes.array
    }
    static defaultProps = {
        placeholder: "",
        variables: {},
        fileType: "application/pdf",
        risorse: []
    }
    onFilesChange = (files = []) => {
        console.log("files_changed")
        if (files.length > 0) {
            this.setState(() => ({files}))
        }else {
            this.setState(() => ({files: undefined}))
        }
    }
    getRisorse = () => (
        this.props.risorse.map((res) => (
            <Resource refetchQueries={this.refetchQueries} key={res.uuid} resource={res}/>))
            )
    removeFile = ({upload: {success, risorse}}) => {
        if(success) {
            const {nome} = risorse[0] || {}
            const files = this.state.files.filter(file => file.name !== nome);
            this.setState(() => ({files}))
        }        
    }
    getLoader = () => {
        const {files = []} = this.state || {}
        const {variables, placeholder} = this.props
        return files.map((file) => (
            <FileLoader
                key={file.name}
                onCompleted={this.removeFile}
                refetchQueries={this.refetchQueries}
                mutation={FILE_UPLOAD}
                file={file}
                placeholder={placeholder}
                variables={variables}
            />))
    } 
    refetchQueries = () => {
        const {variables} = this.props
        return [{query: GET_PIANI, variables}]
    }
    render() {
        return  (
            <React.Fragment>
               <div className="multiple-upload mt-3 pb-2 d-flex flex-column justify-content-between"> 
               {this.getRisorse()}
               {this.getLoader()}
               </div>
               <div className="align-self-start"> 
                <FileChooser 
                    fileType={this.props.fileType}
                    multiple={true}
                    onFilesChange={this.onFilesChange}
                    sz="sm"/>
                </div>
            </React.Fragment>
            )
    }
}

export default UploadFiles
