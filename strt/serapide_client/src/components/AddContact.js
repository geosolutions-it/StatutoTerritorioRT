/* All rights reserved.
*
* This source code is licensed under the BSD-style license found in the
* LICENSE file in the root directory of this source tree.
*/
import React from 'react'

import {Input} from 'reactstrap'
import {Mutation, Query} from  "react-apollo"
import classNames from "classnames"
import {GET_ENTI, CREATE_CONTATTO, GET_CONTATTI} from '../queries'
import { toast } from 'react-toastify'
import EnteSelector from "./EnteSelector"
import { withStateHandlers} from 'recompose';
import {isEmail} from "validator"
const enhancer = withStateHandlers({email: "", nome: ""}, 
    {
        nameChange: () => (e) => ({nome: e.target.value || ""}),
        emailChange: () => (e) => ({email: e.target.value || ""}),
        enteChange: () => (e) => ({ente: e}),
        reset: () => () => ({nome: "", email: "",ente: undefined})
    })

const isValid = ({email, ente, nome = ""}) => isEmail(email) && nome.length > 0 && ente
const showError = (error) => {
    toast.error(error.message,  {autoClose: true})
}
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
        const {contatti} = cache.readQuery({ query: GET_CONTATTI, variables: {tipo} })
        const nCont = {...contatti, edges: contatti.edges.concat({node, __typename: "ContattoNodeEdge"})} 
        cache.writeQuery({
          query: GET_CONTATTI,
          variables: {tipo},
          data: { contatti: nCont},
        });
    }
}
const AddContact = ({tipologia = "generico", ...p}) => (
    <Mutation mutation={CREATE_CONTATTO} update={onUpdate(tipologia)} onCompleted={p.reset} onError={showError}>
    {(onChange, {loading}) => {
        const createContact = () => {
            onChange({variables: getVariables(p,tipologia)})
        }
        return (<div className={classNames("add-contact d-flex justify-content-between align-items-center mb-3", p.className)}>
            <Input  name="name" placeholder="Nome" value={p.nome} onChange={p.nameChange}/>
            <Query query={GET_ENTI}>
                {({loading: isLoading, data: {enti: {edges = []} = {}} = {}, error}) => {
                    if (error) {
                    toast.error(error,  {autoClose: true})
                }
            return (
                <EnteSelector showSelected={false} className="ente-sel pl-2 pr-2" enti={edges} onChange={p.enteChange} isLoading={isLoading} value={p.ente}></EnteSelector>
                )
            }}
        </Query>
        <Input type="email" placeholder="Indirizzo PEC" value={p.email} onChange={p.emailChange}/>
        {loading ? (<div className="spinner-border spinner-border-sm ml-2" role="status">
                <span className="sr-only">Loading...</span>
            </div>): (
        <i className={classNames("material-icons icon-34", {disabled: !isValid(p)})} onClick={createContact  }>perm_contact_calendar</i>)}
    </div>)}}
    </Mutation>
    )


export default enhancer(AddContact)
