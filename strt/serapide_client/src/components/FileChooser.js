/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import Dropzone from 'react-dropzone'
import {Button, Modal, ModalBody} from 'reactstrap'

class FileChooser extends React.Component {
    static propTypes = {
      width: PropTypes.string,
      sz: PropTypes.oneOf(["sm","lg"]),
      modal: PropTypes.bool,
      isOpen: PropTypes.bool,
      toggleOpen: PropTypes.func,
      onFilesChange: PropTypes.func,
      fileType: PropTypes.string,
      multiple: PropTypes.bool,
      showBtn: PropTypes.bool,
      isLocked: PropTypes.bool,
      fontSize: PropTypes.string
    }
    static defaultProps = {
      sz: "sm",
      modal: false,
      isOpen: false,
      multiple: true,
      showBtn: false,
      onFilesChange: (files) => {console.log(files)}
    }
    constructor(props) {
      super(props)
      this.state = !props.toggleOpen ? {isOpen: props.isOpen} : {}
    }
    onDrop = (acceptedFiles = [], rejectedFiles = []) => {
      if(acceptedFiles.length > 0) {
        this.toggleOpen()
        this.props.onFilesChange(acceptedFiles)
      }
    }
    toggleOpen = () => {
      if (this.props.toggleOpen) {
        this.props.toggleOpen()
      }else {
        this.setState(() => ({isOpen: !this.state.isOpen}))
      }
    }
    getTitle = () => this.props.multiple ? "Trascina i Files qui" : "Trascina il File qui"
    getLabel = () => this.props.multiple ? "Seleziona i Files" : "Seleziona il File"
    renderChooser = () => (

      <Dropzone disabled={this.props.isLocked} onDrop={this.onDrop} accept={this.props.fileType} multiple={this.props.multiple}>
        {({getRootProps, getInputProps, isDragActive, isDragAccept, isDragReject,rejectedFiles = [],acceptedFiles =[]}) => {
          return (
            <div
              {...getRootProps()}
              style={{width: this.props.width || "auto"}}
              className={classNames('d-flex','align-items-center', 'justify-content-around', 'dropzone', `${this.props.sz}`,
                {'isRejected': isDragActive ? isDragReject : rejectedFiles.length > 0 ,
                'isAccept':isDragActive ? isDragAccept : acceptedFiles.length > 0 },
                `${this.props.fontSize}`)}
            >
              <input {...getInputProps()} />
              <i className="material-icons text-serapide">cloud_upload</i>
              <span className="title">{this.getTitle()}</span>
              <span className="sub-title">oppure</span>
              <Button className={this.props.fontSize} color="serapide" size={this.props.sz}>{this.getLabel()}</Button>
            </div>
          )
        }}
      </Dropzone>
    )
    render() {
      const {modal, sz, isOpen, toggleOpen, showBtn, isLocked, fontSize} = this.props
      const open = toggleOpen ? isOpen : this.state.isOpen
      if(modal && !open && showBtn) {
        return (<Button className={fontSize} disabled={isLocked} color="serapide" onClick={this.toggleOpen}>Upload</Button>)
      }
      const comp = this.renderChooser()
     return modal ? (
      <Modal toggle={this.toggleOpen} isOpen={open} centered size={`${sz === 'lg' ? 'md' : 'sm'}`} wrapClassName="serapide" autoFocus={true}>
        <ModalBody className="d-flex justify-content-center">{comp}</ModalBody>
      </Modal>) : comp

   }
 }

 export default FileChooser
