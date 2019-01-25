/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import PropTypes from 'prop-types'
import {Button} from 'reactstrap'


const getFileSize = (file) => file.size ? `${Math.round(file.size/100000)/10} MB` : null
const UI = ({placeholder, isLoading, progress, icon = "picture_as_pdf", onCancel, file = {}, error = false, onRetry}) => (
        <div className="file-loader d-flex justify-content-between align-items-center" >
            <div className="d-flex">
                {file.name && (<i className="material-icons text-warning">{icon}</i>)}
            <div className="pl-1 d-flex flex-column justify-content-between">
                <span>{file.name || placeholder}</span>
                <span style={{fontSize: "0.8rem"}}>{getFileSize(file)}</span>
            </div>
        </div>
            {isLoading && (
                            <div className="d-flex justify-content-center align-items-center">
                                <div className="prog text-dark">{Math.round(progress)}%</div> 
                                <div className="spinner-grow text-warning"role="status">
                                        <span className="sr-only">Loading...</span>                
                                </div>       
                                <i className="material-icons text-danger" onClick={onCancel}style={{cursor: 'pointer'}}>cancel</i>
                                </div>)
                }
                {error && file.name && !isLoading && (<Button color="danger" onClick={onRetry}>Riprova</Button>)}
            </div>

)

class FileLoader extends React.Component {
    static propTypes = {
        file: PropTypes.object,
        variables: PropTypes.object,
        placeholder: PropTypes.string,
        isLoading: PropTypes.bool,
        upload: PropTypes.func,
        error: PropTypes.bool,
        onAbort: PropTypes.func
    }
    static defaultProps = {
        placeholder: "",
        isLoading: false,
        variables: {},
        upload: () => (console.warn("mutation function required")),
        onAbort: () => {}
    }
    constructor(props) {
        super(props)
        this.state = {}
    }
    componentDidMount() {
        this.hasMounted = true
        this.uploadProgress = (data, abort) => {
            if(data && this.hasMounted) {
                this.setState(() => ({...data, abort}))
            }
        }
        const {file, variables} = this.props
        if(file) {
            this.props.upload({ variables: { file, ...variables } , context: {uploadProgress: this.uploadProgress }})
        }
    }
    componentDidUpdate(prevProps) {
        const {file, variables, error} = this.props
        if((!prevProps.file && this.props.file) || (error && prevProps.file !== this.props.file)) {
            this.props.upload({ variables: { file, ...variables } , context: {uploadProgress: this.uploadProgress }})
        }
    }
    retry = () => {
        const {file, variables} = this.props
        if(file) {
            this.props.upload({ variables: { file, ...variables } , context: {uploadProgress: this.uploadProgress }})
        }
    }
    abort = () => {
        if ( this.state.abort ) {
            this.state.abort()
            this.props.onAbort(this.props.file.name)
        }
    }
    render() {
        const {loaded = 0, total = 1} = this.state
        return  (
            <UI onRetry={this.retry} onCancel={this.abort} progress={loaded/total * 100} {...this.props}/>)
    }
    componentWillUnmount() {
        this.uploadProgress = null
        this.hasMounted = false
    }
}

export default FileLoader