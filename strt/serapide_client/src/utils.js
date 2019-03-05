import { format, parseISO} from 'date-fns'
import { it } from 'date-fns/locale'
import { toast } from 'react-toastify'

export const getEnteLabel = ({name = "", code, type: {tipoente = ""} ={}} = {}) => `${tipoente} di ${name}`
export const getEnteLabelID = ({name = "", code, type: {tipoente = ""} ={}} = {}) => `ID ${tipoente} ${code}`
export const getPianoLabel = (tipo = "") => (tipo === "VARIANTE" ? tipo.toLowerCase() : `piano ${tipo.toLowerCase()}`)
export const formatDate = (date) => format(parseISO(date) , "iiii do MMMM yyyy", {locale: it})
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

