import { format, parseISO, differenceInCalendarDays, subDays, addDays} from 'date-fns'
import {isDate, find, get} from 'lodash'
import { it } from 'date-fns/locale'
import { toast } from 'react-toastify'
import elaborati from './Elaborati'

export const pollingInterval = 10000
export {get, map, isEmpty} from "lodash"

export const getEnteLabel = ({nome = "", ipa, tipo = ""  } = {}) => `${tipo}${ipa && ' di '}${nome}`

export const getEnteLabelID = ({ipa}= {}) => `${ipa && 'ID '}${ipa}`

export const getPianoLabel = (tipo = "") => (tipo === "VARIANTE" ? tipo.toLowerCase() : `piano ${tipo.toLowerCase()}`)

export const getDate = (date) => {
    return isDate(date) ? date : parseISO(date)
}

export const formatDate = (date, template = "dd/MM/yyyy") => date ? format(getDate(date), template, {locale: it}) : null

export const getDifferenceInDays = (dateEnd, dateStart) => differenceInCalendarDays(getDate(dateEnd), getDate(dateStart))

export const daysSub = (date, amount) =>  {
    return subDays(getDate(date), amount)
}
export const daysAdd = (date, amount) =>  {
    return addDays(getDate(date), amount)
}
export const getNominativo = ({firstName, lastName, fiscalCode} = {}) =>  firstName || lastName ? `${firstName || ""} ${lastName || ""}` : fiscalCode
export const fasi = [ "anagrafica", "avvio", "adozione", "approvazione", "pubblicazione"]

export const getActionIcon = (stato) => {
    switch (stato) {
        case "NECESSARIA":
            return "alarm_add"
        case "ATTESA":
            return "alarm_on"
        default:
            return "alarm_off"
    }
} 
export const getActionIconColor = (stato) => {
    switch (stato) {
        case "NECESSARIA":
        case "ATTESA":
            return "text-serapide"
        default:
            return ""
    }
}
export const actionHasBtn = (actor = "") => {
    switch (actor) {
        case "AC":
            return true
        default:
            return false
    }
}
export const getAction = (stato) => {
    switch (stato) {
        case "NECESSARIA":
        case "ATTESA":
            return true
        default:
            return false
    }
}

export const showError = ({graphQLErrors, message, networkError: {result:{errors = []} = {}} = {}}) => {
    let  er = [...graphQLErrors, ...errors]
    if(message) { 
        toast.error(message,  {autoClose: true})    
    }
    er.map(({message}) => toast.error(message,  {autoClose: true}))
}

export const elaboratiCompletati = (tipoPiano = "", risorse) => {
            const tipo = tipoPiano.toLocaleLowerCase()
             return elaborati[tipo] && !find(elaborati[tipo]["testuali"], (el, key) => {
                 return !find(risorse, ({node: {tipo: t} = {}}) => {
                    return t === key})})
            }

export const getInputFactory = (inputType) => (uuid, field) => (val) => ({
    variables: {
        input: { 
            [inputType]: { [field]: isDate(val) ? val.toISOString() : val }, 
            uuid
        }
    }
})

export const getCodice = (props) => get(props, "piano.codice")



// Raggruppa le risorse per utente
export const groupResourcesByUser = (resources = []) => resources.reduce((acc, {node}) => {
    if (acc[node.user.fiscalCode]) { 
        acc[node.user.fiscalCode].push(node)
    }
    else {
        acc[node.user.fiscalCode] = [node]
    }
    return acc
} , {})

export const filterAndGroupResourcesByUser = ( resources, type = "") => groupResourcesByUser(resources.filter(({node: {tipo}}) => tipo === type))


export const getContatti = ({ uffici = []} = {}) => {
    return uffici.map(({qualifica: tipologia, ufficio: {uuid,
        descrizione,
        nome,
        ente: {
            nome: nomeEnte} = {}
        } = {}} = {}) => ({label: `Ente ${nomeEnte} ufficio ${nome}`, value: uuid, tipologia}))
}
export const showAdozione = (f) => f === "AVVIO" || f === "ADOZIONE" || f === "APPROVAZIONE" || f === "PUBBLICAZIONE"
export const showApprovazione = (f) => f === "ADOZIONE" || f === "APPROVAZIONE" || f === "PUBBLICAZIONE"
export const showPubblicazione = (f) => f === "APPROVAZIONE" || f === "PUBBLICAZIONE"

export const getAdminEnti = (profiles = []) => profiles.filter(({profilo}) => profilo === "ADMIN_ENTE").map(({ente}) => ente); 
export const isAdminEnte = (profiles = []) => getAdminEnti(profiles).length > 0;