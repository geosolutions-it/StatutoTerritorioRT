import { format, parseISO, differenceInCalendarDays, subDays} from 'date-fns'
import {isDate} from 'lodash'
import { it } from 'date-fns/locale'
import { toast } from 'react-toastify'

export const getEnteLabel = ({name = "", code, type: {tipoente = ""} ={}} = {}) => `${tipoente} di ${name}`

export const getEnteLabelID = ({name = "", code, type: {tipoente = ""} ={}} = {}) => `ID ${tipoente} ${code}`

export const getPianoLabel = (tipo = "") => (tipo === "VARIANTE" ? tipo.toLowerCase() : `piano ${tipo.toLowerCase()}`)

export const getDate = (date) => {
    return isDate(date) ? date : parseISO(date)
}

export const formatDate = (date, template = "dd/MM/yyyy") => format(getDate(date), template, {locale: it})

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

export const showError = (error) => {
    toast.error(error.message,  {autoClose: true})
}

