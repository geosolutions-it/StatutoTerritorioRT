/* All rights reserved.
*
* This source code is licensed under the BSD-style license found in the
* LICENSE file in the root directory of this source tree.
*/
import React from 'react'

import {Input} from 'reactstrap'
import {Mutation, Query} from  "react-apollo"
import classNames from "classnames"
import {GET_ENTI, CREATE_CONTATTO, GET_CONTATTI, GET_TIPO_CONTATTO} from '../graphql'

import EnteSelector from "./EnteSelector"
import { withStateHandlers, compose} from 'recompose';
import { withControllableState} from '../enhancers/utils';
import {isEmail} from "validator"
import SelectTipo from './SelectTipo';
import {showError} from '../utils'

const enhancer = compose(withStateHandlers({email: "", nome: ""}, 
    {
        nameChange: () => (e) => ({nome: e.target.value || ""}),
        emailChange: () => (e) => ({email: e.target.value || ""}),
        enteChange: () => (e) => ({ente: e}),
        reset: () => () => ({nome: "", email: "",ente: undefined})
    }), withControllableState("tipologia", "onTypeChange", "generico"))

const isValid = ({email, ente, nome = ""}) => isEmail(email) && nome && ente

const getVariables = ({nome, email, ente: {node: {code} = {}}}, tipologia) => ({
    input: {
      contatto: {
        nome,
        email,
        tipologia,
        ente: {code}
      }
    }
  })
const onUpdate = (tipo) => (cache, { data: {createContatto: {nuovoContatto: node} ={}} }) => {
    if(node) {
        const {contatti} = cache.readQuery({ query: GET_CONTATTI, variables: tipo ? {tipo} : {} })
        const nCont = {...contatti, edges: contatti.edges.concat({node, __typename: "ContattoNodeEdge"})} 
        cache.writeQuery({
          query: GET_CONTATTI,
          variables: tipo ? {tipo} : {},
          data: { contatti: nCont},
        });
    }
}
const AddContact = ({onTypeChange, tipologia, ...p}) => (
    <Mutation mutation={CREATE_CONTATTO} update={onUpdate(!!onTypeChange ? undefined : tipologia)} onCompleted={p.reset} onError={showError}>
        {(onChange, {loading}) => {
            const t = tipologia.value ? tipologia.value : tipologia
            const createContact = () => {
                onChange({variables: getVariables(p,t)})
            }
            const isF = !!onTypeChange
            return (
                <div style={{marginLeft: 0, marginRight: 0}}className={classNames("add-contact row d-flex align-items-center mb-3", p.className)}>
                    <div className={`my-1 col col-sm-12 col-md-${isF ? 6 : 4}  col-lg-${isF ? 3 : 4} `}><Input  name="name" placeholder="Nominativo" value={p.nome} onChange={p.nameChange}/></div>
                    <div className={`my-1 col col-sm-12 col-md-${isF ? 6 : 3}  col-lg-3`}>
                        <Query query={GET_ENTI} onError={showError}>
                            {({loading: isLoading, data: {enti: {edges = []} = {}} = {}}) => {
                        return (
                            <EnteSelector showSelected={false}  enti={edges} onChange={p.enteChange} isLoading={isLoading} value={p.ente}></EnteSelector>
                            )
                        }}
                        </Query>
                    </div>
                    <div className={`my-1 col col-sm-12 col-md-${isF ? 6 : 4}  col-lg-${isF ? 3 : 4}`}>
                        <Input type="email" placeholder="Indirizzo PEC" value={p.email} onChange={p.emailChange}/>
                    </div>
                    {onTypeChange && (<div className={`my-1 col col-sm-11 col-md-5 col-lg-2`}>
                        <Query query={GET_TIPO_CONTATTO} onError={showError}>
                            {({loading: isLoading, data: {tipologiaContatto: tipi =[]}}) => {
                            return (
                                <SelectTipo placeholder="Selezionare tipo..." tipiPiano={tipi} onChange={(a,b) => {onTypeChange(a)}} isLoading={isLoading} value={tipologia}/>
                            )
                        }}
                        </Query>
                    </div>)}
                    <div className="my-1 col col-1 d-flex justify-content-center">
                        {loading ? (<div className="spinner-border spinner-border-sm ml-2" role="status">
                                <span className="sr-only">Loading...</span>
                        </div>): (<i className={classNames("material-icons icon-34", {disabled: !isValid(p)})} onClick={createContact  }>perm_contact_calendar</i>)}
                    </div>
                </div>
            )}}
    </Mutation>
    )


export default enhancer(AddContact)
