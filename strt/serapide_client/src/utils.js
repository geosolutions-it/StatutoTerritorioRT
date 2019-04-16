import { format, parseISO, differenceInCalendarDays, subDays} from 'date-fns'
import {isDate, find} from 'lodash'
import { it } from 'date-fns/locale'
import { toast } from 'react-toastify'
import elaborati from './Elaborati'
export const getEnteLabel = ({name = "", code, type: {tipoente = ""} ={}} = {}) => `${tipoente} di ${name}`

export const getEnteLabelID = ({name = "", code, type: {tipoente = ""} ={}} = {}) => `ID ${tipoente} ${code}`

export const getPianoLabel = (tipo = "") => (tipo === "VARIANTE" ? tipo.toLowerCase() : `piano ${tipo.toLowerCase()}`)

export const getDate = (date) => {
    return isDate(date) ? date : parseISO(date)
}

export const formatDate = (date, template = "dd/MM/yyyy") => date ? format(getDate(date), template, {locale: it}) : null

export const getDifferenceInDays = (dateEnd, dateStart) => differenceInCalendarDays(getDate(dateEnd), getDate(dateStart))

export const daysSub = (date, amount) =>  {
    return subDays(getDate(date), amount)
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
    const er = [...graphQLErrors, ...errors]
    if(er) er.map(({message}) => toast.error(message,  {autoClose: true})) 
    else toast.error(message,  {autoClose: true})
}

export const elaboratiCompletati = (tipoPiano = "", risorse) => {
            const tipo = tipoPiano.toLocaleLowerCase()
             return  elaborati[tipo] && !find(elaborati[tipo]["testuali"], (el, key) => {
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